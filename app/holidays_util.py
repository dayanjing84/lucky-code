from __future__ import annotations

from datetime import date
import holidays


CN_HOLIDAYS = holidays.CountryHoliday("CN")


def get_holiday_name(d: date) -> str | None:
    try:
        name = CN_HOLIDAYS.get(d)
        if isinstance(name, list):
            return name[0]
        return name
    except Exception:
        return None


def season_by_month(m: int) -> str:
    mapping = {
        1: "寒冬",
        2: "初春前",
        3: "早春",
        4: "暮春",
        5: "初夏",
        6: "盛夏",
        7: "仲夏",
        8: "夏末",
        9: "初秋",
        10: "金秋",
        11: "初冬",
        12: "隆冬",
    }
    return mapping.get(m, "当季")


def date_cn_str(d: date) -> str:
    return d.strftime("%Y年%m月%d日")

