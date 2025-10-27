from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os


BASE_DIR = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class AppConfig:
    excel_file: Path = BASE_DIR / "吉祥号码.xlsx"
    template_image: Path = BASE_DIR / "吉祥号图片.jpg"
    output_dir: Path = BASE_DIR / "output"
    used_json: Path = BASE_DIR / "used_numbers.json"
    timezone: str = "Asia/Shanghai"
    # 优先级：前者优先
    category_priority: tuple[str, ...] = (
        "尾号双重",
        "中间任意数字",
        "*AABB",
        "*ABC",
        "尾号双重689",
        "尾号至尾号",
    )
    # 计划分类（可留空自动选择）
    schedule_plan: dict[str, str | None] = None  # e.g. {"09:00": "尾号1001类", ...}
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    branding_label: str = "南昌县移动专供"
    # 数量与布局
    numbers_per_poster: int = 9  # 三列×三行
    randomize_category_default: bool = True
    # 地区与热线
    location_name: str = "南昌"
    hotline: str = "13507094669"

    # 字体候选（按顺序尝试）
    font_candidates: tuple[str, ...] = (
        str(BASE_DIR / "msyh.ttc"),
        r"C:\\Windows\\Fonts\\msyh.ttc",
        r"C:\\Windows\\Fonts\\msyh.ttf",
        str(BASE_DIR / "arial.ttf"),
    )


CFG = AppConfig(
    schedule_plan={
        "09:00": None,
        "12:00": None,
        "18:00": None,
    }
)


def ensure_dirs() -> None:
    CFG.output_dir.mkdir(parents=True, exist_ok=True)


def select_font_path() -> str | None:
    for p in CFG.font_candidates:
        if Path(p).exists():
            return p
    return None
