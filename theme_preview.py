"""
主题预览工具
生成所有主题的示例海报，用于对比效果
"""
from __future__ import annotations

import sys
from pathlib import Path
from datetime import datetime

# 添加项目路径
sys.path.append(str(Path(__file__).parent))

from app.theme_system import THEMES, ThemeColors
from app.poster_generator_v2 import render_poster
from app.config import select_font_path, ensure_dirs, CFG


def generate_theme_preview(theme_name: str, theme: ThemeColors, output_dir: Path):
    """生成单个主题的预览海报"""

    # 示例数据
    items = [
        {"号码": "13800138000", "预存": 1000, "低消": 58},
        {"号码": "13900139001", "预存": 800, "低消": 48},
        {"号码": "13700137002", "预存": 600, "低消": 38},
        {"号码": "13600136003", "预存": 500, "低消": 28},
        {"号码": "13500135004", "预存": 1200, "低消": 68},
        {"号码": "13400134005", "预存": 900, "低消": 58},
        {"号码": "13300133006", "预存": 700, "低消": 48},
        {"号码": "13200132007", "预存": 600, "低消": 38},
        {"号码": "13100131008", "预存": 500, "低消": 28},
    ]

    output_path = output_dir / f"主题预览_{theme_name}.jpg"
    font_path = select_font_path()

    try:
        render_poster(
            output_path=output_path,
            font_path=font_path,
            title="吉祥号码精选",
            subtitle=f"2025年10月20日 {theme_name}｜示例专场",
            tagline="主题预览 - 幸运好号，限时抢购，心动不如行动！",
            items=items,
            branding_label="南昌县移动专供",
            grid_cols=3,
            grid_rows=3,
            location="南昌",
            hotline="13507094669",
            theme=theme,
        )
        print(f"[OK] 已生成: {output_path.name}")
        return True
    except Exception as e:
        print(f"[ERROR] 生成失败 ({theme_name}): {e}")
        return False


def main():
    """生成所有主题的预览海报"""
    print("=" * 60)
    print("主题预览工具")
    print("=" * 60)

    # 创建输出目录
    preview_dir = CFG.output_dir / "theme_preview"
    preview_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n输出目录: {preview_dir}")
    print(f"主题数量: {len(THEMES)}\n")

    # 生成每个主题的预览
    success_count = 0
    for theme_name, theme in THEMES.items():
        if generate_theme_preview(theme_name, theme, preview_dir):
            success_count += 1

    # 总结
    print("\n" + "=" * 60)
    print(f"完成！成功生成 {success_count}/{len(THEMES)} 个主题预览")
    print(f"查看目录: {preview_dir}")
    print("=" * 60)


if __name__ == "__main__":
    main()
