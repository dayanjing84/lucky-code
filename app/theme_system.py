"""
海报主题系统
根据时间、天气、节假日自动选择主题配色和文案风格
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, time
from typing import Literal

from .weather_api import WeatherType


ThemeType = Literal[
    "早晨清新", "午间活力", "傍晚温暖", "夜晚神秘",
    "晴天明亮", "雨天温馨", "雪天浪漫",
    "春节喜庆", "情人节浪漫", "清明素雅", "劳动节活力",
    "端午传统", "中秋团圆", "国庆爱国", "元旦新年",
    "默认蓝调"
]


@dataclass
class ThemeColors:
    """主题配色方案"""
    # 渐变背景
    bg_top: tuple[int, int, int]
    bg_bottom: tuple[int, int, int]

    # 头部渐变
    header_top: tuple[int, int, int]
    header_bottom: tuple[int, int, int]

    # 底部渐变
    footer_top: tuple[int, int, int]
    footer_bottom: tuple[int, int, int]

    # 文字颜色
    title_color: tuple[int, int, int] = (255, 255, 255)
    subtitle_color: tuple[int, int, int] = (230, 242, 255)
    tagline_color: tuple[int, int, int] = (255, 255, 255)

    # 卡片颜色
    card_fill: tuple[int, int, int] = (250, 252, 255)
    card_border: tuple[int, int, int] = (230, 235, 245)

    # 主题名称
    name: str = "默认主题"


# ==================== 主题库 ====================

THEMES: dict[ThemeType, ThemeColors] = {
    # 时间段主题
    "早晨清新": ThemeColors(
        name="早晨清新",
        bg_top=(255, 250, 240),
        bg_bottom=(255, 245, 230),
        header_top=(255, 183, 77),
        header_bottom=(255, 213, 128),
        footer_top=(255, 183, 77),
        footer_bottom=(255, 213, 128),
        title_color=(255, 255, 255),
        subtitle_color=(255, 248, 235),
    ),

    "午间活力": ThemeColors(
        name="午间活力",
        bg_top=(255, 248, 240),
        bg_bottom=(255, 243, 224),
        header_top=(255, 87, 34),
        header_bottom=(255, 138, 101),
        footer_top=(255, 87, 34),
        footer_bottom=(255, 138, 101),
        title_color=(255, 255, 255),
        subtitle_color=(255, 235, 215),
    ),

    "傍晚温暖": ThemeColors(
        name="傍晚温暖",
        bg_top=(255, 245, 238),
        bg_bottom=(255, 238, 220),
        header_top=(255, 112, 67),
        header_bottom=(255, 152, 107),
        footer_top=(255, 112, 67),
        footer_bottom=(255, 152, 107),
        title_color=(255, 255, 255),
        subtitle_color=(255, 228, 210),
    ),

    "夜晚神秘": ThemeColors(
        name="夜晚神秘",
        bg_top=(240, 242, 250),
        bg_bottom=(230, 232, 245),
        header_top=(63, 81, 181),
        header_bottom=(92, 107, 192),
        footer_top=(63, 81, 181),
        footer_bottom=(92, 107, 192),
        title_color=(255, 255, 255),
        subtitle_color=(220, 230, 255),
    ),

    # 天气主题
    "晴天明亮": ThemeColors(
        name="晴天明亮",
        bg_top=(255, 251, 230),
        bg_bottom=(255, 245, 210),
        header_top=(255, 193, 7),
        header_bottom=(255, 213, 79),
        footer_top=(255, 193, 7),
        footer_bottom=(255, 213, 79),
        title_color=(255, 255, 255),
        subtitle_color=(255, 248, 220),
    ),

    "雨天温馨": ThemeColors(
        name="雨天温馨",
        bg_top=(240, 245, 250),
        bg_bottom=(230, 240, 250),
        header_top=(66, 165, 245),
        header_bottom=(100, 181, 246),
        footer_top=(66, 165, 245),
        footer_bottom=(100, 181, 246),
        title_color=(255, 255, 255),
        subtitle_color=(225, 245, 254),
    ),

    "雪天浪漫": ThemeColors(
        name="雪天浪漫",
        bg_top=(250, 250, 255),
        bg_bottom=(245, 248, 255),
        header_top=(158, 158, 158),
        header_bottom=(189, 189, 189),
        footer_top=(158, 158, 158),
        footer_bottom=(189, 189, 189),
        title_color=(255, 255, 255),
        subtitle_color=(240, 240, 255),
    ),

    # 节日主题
    "春节喜庆": ThemeColors(
        name="春节喜庆",
        bg_top=(255, 245, 235),
        bg_bottom=(255, 238, 220),
        header_top=(211, 47, 47),
        header_bottom=(239, 83, 80),
        footer_top=(211, 47, 47),
        footer_bottom=(239, 83, 80),
        title_color=(255, 235, 59),
        subtitle_color=(255, 245, 220),
    ),

    "情人节浪漫": ThemeColors(
        name="情人节浪漫",
        bg_top=(255, 240, 245),
        bg_bottom=(255, 228, 240),
        header_top=(233, 30, 99),
        header_bottom=(244, 67, 54),
        footer_top=(233, 30, 99),
        footer_bottom=(244, 67, 54),
        title_color=(255, 255, 255),
        subtitle_color=(255, 235, 245),
    ),

    "清明素雅": ThemeColors(
        name="清明素雅",
        bg_top=(245, 248, 250),
        bg_bottom=(238, 243, 248),
        header_top=(96, 125, 139),
        header_bottom=(120, 144, 156),
        footer_top=(96, 125, 139),
        footer_bottom=(120, 144, 156),
        title_color=(255, 255, 255),
        subtitle_color=(236, 239, 241),
    ),

    "劳动节活力": ThemeColors(
        name="劳动节活力",
        bg_top=(255, 243, 224),
        bg_bottom=(255, 236, 179),
        header_top=(255, 152, 0),
        header_bottom=(255, 183, 77),
        footer_top=(255, 152, 0),
        footer_bottom=(255, 183, 77),
        title_color=(255, 255, 255),
        subtitle_color=(255, 245, 225),
    ),

    "端午传统": ThemeColors(
        name="端午传统",
        bg_top=(240, 248, 240),
        bg_bottom=(232, 245, 233),
        header_top=(56, 142, 60),
        header_bottom=(76, 175, 80),
        footer_top=(56, 142, 60),
        footer_bottom=(76, 175, 80),
        title_color=(255, 255, 255),
        subtitle_color=(232, 245, 233),
    ),

    "中秋团圆": ThemeColors(
        name="中秋团圆",
        bg_top=(255, 248, 225),
        bg_bottom=(255, 243, 205),
        header_top=(255, 143, 0),
        header_bottom=(255, 167, 38),
        footer_top=(255, 143, 0),
        footer_bottom=(255, 167, 38),
        title_color=(255, 255, 255),
        subtitle_color=(255, 245, 220),
    ),

    "国庆爱国": ThemeColors(
        name="国庆爱国",
        bg_top=(255, 245, 238),
        bg_bottom=(255, 235, 220),
        header_top=(198, 40, 40),
        header_bottom=(229, 57, 53),
        footer_top=(198, 40, 40),
        footer_bottom=(229, 57, 53),
        title_color=(255, 235, 59),
        subtitle_color=(255, 243, 224),
    ),

    "元旦新年": ThemeColors(
        name="元旦新年",
        bg_top=(250, 245, 255),
        bg_bottom=(243, 238, 255),
        header_top=(123, 31, 162),
        header_bottom=(156, 39, 176),
        footer_top=(123, 31, 162),
        footer_bottom=(156, 39, 176),
        title_color=(255, 255, 255),
        subtitle_color=(237, 231, 246),
    ),

    # 默认主题
    "默认蓝调": ThemeColors(
        name="默认蓝调",
        bg_top=(246, 249, 255),
        bg_bottom=(234, 239, 250),
        header_top=(55, 120, 240),
        header_bottom=(95, 160, 255),
        footer_top=(55, 120, 240),
        footer_bottom=(95, 160, 255),
        title_color=(255, 255, 255),
        subtitle_color=(230, 242, 255),
    ),
}


def select_theme(
    dt: datetime | None = None,
    weather: WeatherType | None = None,
    holiday_name: str | None = None
) -> ThemeColors:
    """
    根据日期时间、天气、节日自动选择主题

    优先级：
    1. 重要节日主题
    2. 天气主题
    3. 时间段主题
    4. 默认主题
    """
    if dt is None:
        dt = datetime.now()

    # 1. 检查是否是重要节日
    if holiday_name:
        theme = _get_holiday_theme(holiday_name)
        if theme:
            return theme

    # 2. 检查天气主题
    if weather:
        theme = _get_weather_theme(weather)
        if theme:
            return theme

    # 3. 根据时间段选择
    return _get_time_theme(dt.time())


def _get_holiday_theme(holiday_name: str) -> ThemeColors | None:
    """根据节日名称返回主题"""
    holiday_map = {
        "春节": "春节喜庆",
        "除夕": "春节喜庆",
        "情人节": "情人节浪漫",
        "清明节": "清明素雅",
        "劳动节": "劳动节活力",
        "端午节": "端午传统",
        "中秋节": "中秋团圆",
        "国庆节": "国庆爱国",
        "元旦": "元旦新年",
    }

    for key, theme_name in holiday_map.items():
        if key in holiday_name:
            return THEMES[theme_name]

    return None


def _get_weather_theme(weather: WeatherType) -> ThemeColors | None:
    """根据天气返回主题"""
    weather_map: dict[WeatherType, ThemeType] = {
        "晴天": "晴天明亮",
        "小雨": "雨天温馨",
        "中雨": "雨天温馨",
        "大雨": "雨天温馨",
        "雷阵雨": "雨天温馨",
        "雪": "雪天浪漫",
    }

    theme_name = weather_map.get(weather)
    return THEMES[theme_name] if theme_name else None


def _get_time_theme(t: time) -> ThemeColors:
    """根据时间段返回主题"""
    hour = t.hour

    if 5 <= hour < 9:
        return THEMES["早晨清新"]
    elif 9 <= hour < 13:
        return THEMES["午间活力"]
    elif 13 <= hour < 18:
        return THEMES["午间活力"]
    elif 18 <= hour < 21:
        return THEMES["傍晚温暖"]
    else:
        return THEMES["夜晚神秘"]


def get_theme_description(theme: ThemeColors, weather: WeatherType | None = None) -> str:
    """获取主题的描述性文本，用于海报副标题"""
    descriptions = []

    # 添加天气信息
    if weather and weather != "未知":
        from .weather_api import get_weather_emoji
        emoji = get_weather_emoji(weather)
        descriptions.append(f"{emoji}{weather}" if emoji else weather)

    # 添加主题名称
    descriptions.append(theme.name)

    return " · ".join(descriptions)
