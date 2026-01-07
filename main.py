from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
import sys
import pytz

from apscheduler.schedulers.blocking import BlockingScheduler

from app.config import CFG, ensure_dirs, select_font_path
from app.data_loader import load_numbers_excel
from app.used_storage import UsedStorage
from app.selection import choose_category, pick_numbers_for_category
from app.holidays_util import date_cn_str, get_holiday_name
from app.ai_copy import generate_copy
from app.weather_api import get_weather
from app.theme_system import select_theme, get_theme_description
from app.wechat_sender import create_wechat_sender
try:
    from app.poster_generator_v2 import render_poster  # 新版渲染（3x3、两行meta、间距优化）
except Exception:
    from app.poster_generator import render_poster  # 退回旧版


def now_shanghai() -> datetime:
    tz = pytz.timezone(CFG.timezone)
    return datetime.now(tz)


def format_out_name(d: datetime) -> str:
    return d.strftime("%Y%m%d_%H%M.jpg")


def generate_once(category: str | None, *, slot: str | None = None, excel_path: Path | None = None, debug: bool = False, auto_send: bool = False) -> Path | None:
    ensure_dirs()
    d = now_shanghai()
    slot_tag = slot or ("morning" if d.hour < 12 else ("noon" if d.hour < 18 else "evening"))
    print(f"[INFO] 生成时间: {d.isoformat()} 时段: {slot_tag}")

    # 读取数据
    try:
        xls = excel_path if excel_path else CFG.excel_file
        print(f"[INFO] 使用 Excel: {xls}")
        df = load_numbers_excel(xls)
    except Exception as e:
        print(f"[ERROR] 读取 Excel 失败: {e}")
        return None

    store = UsedStorage(CFG.used_json)

    # 选择分类
    chosen = choose_category(
        df,
        store,
        preferred=category,
        priority_list=CFG.category_priority,
        min_count=CFG.numbers_per_poster,
        randomize=CFG.randomize_category_default,
    )
    if not chosen:
        print("[WARN] 未找到满足条件的分类（>=15 个未使用号码）。本次不生成。")
        return None
    print(f"[INFO] 选择分类: {chosen}")

    # 抽取号码
    items = pick_numbers_for_category(df, store, chosen, count=CFG.numbers_per_poster)
    if len(items) < CFG.numbers_per_poster:
        print(f"[WARN] 分类号码数不足 {CFG.numbers_per_poster}，本次跳过。")
        return None
    if debug:
        print("[DEBUG] 选取号码:")
        for it in items:
            print("  -", it["号码"], "/ 预存", it.get("预存"), "/ 低消", it.get("低消"))

    # 获取节日和天气信息
    holiday_name = get_holiday_name(d.date())
    if holiday_name:
        print(f"[INFO] 今日节日: {holiday_name}")

    weather = None
    try:
        weather = get_weather(CFG.location_name)
        print(f"[INFO] 当前天气: {weather}")
    except Exception as e:
        print(f"[WARN] 获取天气失败: {e}")

    # 选择主题
    theme = select_theme(dt=d, weather=weather, holiday_name=holiday_name)
    print(f"[INFO] 使用主题: {theme.name}")

    # AI 文案
    copy = generate_copy(d, chosen, tone=slot_tag)  # 返回 {title, tagline}
    title = copy.get("title", "好号专场")
    tagline = copy.get("tagline", "幸运好号，多重优惠，限时抢购！")

    # 构建副标题（包含日期、天气、主题信息和分类）
    theme_desc = get_theme_description(theme, weather)
    subtitle = f"{date_cn_str(d.date())} {theme_desc}｜{chosen}专场"

    # 渲染图片
    out_path = CFG.output_dir / format_out_name(d)
    font_path = select_font_path()
    try:
        render_poster(
            output_path=out_path,
            font_path=font_path,
            title=title,
            subtitle=subtitle,
            tagline=tagline,
            items=items,
            branding_label=getattr(CFG, "branding_label", None),
            grid_cols=3,
            grid_rows=3,
            location=getattr(CFG, "location_name", None),
            hotline=getattr(CFG, "hotline", None),
            theme=theme,
        )
    except Exception as e:
        print(f"[ERROR] 渲染图片失败: {e}")
        return None

    # 标记已使用
    store.mark_used([it["号码"] for it in items], category=chosen, output_path=str(out_path))

    print(f"[OK] 已生成: {out_path}")

    # 自动发送到微信
    if auto_send:
        try:
            sender = create_wechat_sender()
            success = sender.send_poster(
                image_path=out_path,
                title=title,
                description=tagline
            )
            if success:
                print("[OK] 微信发送成功")
            else:
                print("[WARN] 微信发送失败或未启用")
        except Exception as e:
            print(f"[ERROR] 微信发送异常: {e}")

    return out_path


def list_categories(excel_path: Path | None = None) -> int:
    from app.selection import _unused_numbers_in_category

    try:
        xls = excel_path if excel_path else CFG.excel_file
        df = load_numbers_excel(xls)
    except Exception as e:
        print(f"[ERROR] 读取 Excel 失败: {e}")
        return 1

    store = UsedStorage(CFG.used_json)
    store.load()
    cats = list(df["分类说明"].dropna().astype(str).unique())
    print(f"[INFO] 分类数: {len(cats)} （来自列‘分类说明’的唯一值）")
    for cat in cats:
        total = int((df["分类说明"] == cat).sum())
        unused = len(_unused_numbers_in_category(df, store, cat))
        print(f"- {cat}: 总数{total}，未使用{unused}")
    return 0


def run_schedule(excel_path: Path | None = None) -> None:
    sched = BlockingScheduler(timezone=CFG.timezone)

    def job(category: str | None, slot: str, auto_send: bool = False):
        try:
            generate_once(category, slot=slot, excel_path=excel_path, auto_send=auto_send)
        except Exception as e:
            print(f"[ERROR] 任务异常: {e}")

    # 三个时间点,12点和18点自动发送
    p = CFG.schedule_plan or {"09:00": None, "12:00": None, "18:00": None}
    for hhmm, cat in p.items():
        hh, mm = [int(x) for x in hhmm.split(":")]
        slot = "morning" if hh < 12 else ("noon" if hh < 18 else "evening")
        # 12:00和18:00自动发送到微信
        auto_send = (hhmm in ["12:00", "18:00"])
        sched.add_job(job, "cron", hour=hh, minute=mm, args=[cat, slot, auto_send], id=f"slot_{hhmm}")
        send_tag = " [自动发送微信]" if auto_send else ""
        print(f"[SCHED] 已安排 {hhmm} 分类={cat or '自动选择'}{send_tag}")

    print("[SCHED] 调度器启动，按 Ctrl+C 停止")
    try:
        sched.start()
    except (KeyboardInterrupt, SystemExit):
        print("[SCHED] 已停止")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="每日吉祥号码海报自动生成器")
    parser.add_argument("--once", action="store_true", help="立即生成一次")
    parser.add_argument("--category", type=str, default=None, help="指定分类说明（可选）")
    parser.add_argument("--schedule", action="store_true", help="启动定时任务")
    parser.add_argument("--excel", type=str, default=None, help="指定 Excel 路径（默认读取项目根的吉祥号码.xlsx）")
    parser.add_argument("--debug", action="store_true", help="打印调试信息（选取号码等）")
    parser.add_argument("--slot", type=str, choices=["morning", "noon", "evening"], default=None, help="覆盖时段：morning/noon/evening")
    parser.add_argument("--list-categories", action="store_true", help="仅列出分类与数量并退出")
    parser.add_argument("--send", action="store_true", help="生成后自动发送到微信（需配置wechat_config.json）")

    args = parser.parse_args(argv)

    excel_override = Path(args.excel) if args.excel else None
    if args.list_categories:
        return list_categories(excel_override)

    if args.once:
        generate_once(args.category, slot=args.slot, excel_path=excel_override, debug=args.debug, auto_send=args.send)
        return 0

    if args.schedule:
        run_schedule(excel_path=excel_override)
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
