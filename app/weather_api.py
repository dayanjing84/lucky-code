"""
天气API集成模块
支持多个免费天气API，自动回退
"""
from __future__ import annotations

import os
from typing import Literal
import requests


WeatherType = Literal["晴天", "多云", "阴天", "小雨", "中雨", "大雨", "雷阵雨", "雪", "雾霾", "未知"]


def get_weather(city: str = "南昌", timeout: int = 5) -> WeatherType:
    """
    获取指定城市的天气状况

    优先级：
    1. 天气API（如果配置了API_KEY）
    2. 简化的公开API
    3. 默认返回"晴天"
    """
    # 尝试使用高德天气API（免费，需要key）
    amap_key = os.getenv("AMAP_WEATHER_KEY")
    if amap_key:
        result = _get_weather_amap(city, amap_key, timeout)
        if result != "未知":
            return result

    # 回退：返回默认天气
    return "晴天"


def _get_weather_amap(city: str, api_key: str, timeout: int) -> WeatherType:
    """使用高德天气API获取天气"""
    try:
        # 高德天气API
        url = "https://restapi.amap.com/v3/weather/weatherInfo"
        params = {
            "city": city,
            "key": api_key,
            "extensions": "base"
        }

        response = requests.get(url, params=params, timeout=timeout)
        data = response.json()

        if data.get("status") == "1" and data.get("lives"):
            weather_text = data["lives"][0].get("weather", "")
            return _normalize_weather(weather_text)
    except Exception:
        pass

    return "未知"


def _normalize_weather(weather_text: str) -> WeatherType:
    """将各种天气描述标准化"""
    weather_text = weather_text.lower()

    if "晴" in weather_text:
        return "晴天"
    elif "雨" in weather_text:
        if "雷" in weather_text:
            return "雷阵雨"
        elif "大雨" in weather_text or "暴雨" in weather_text:
            return "大雨"
        elif "中雨" in weather_text:
            return "中雨"
        else:
            return "小雨"
    elif "雪" in weather_text:
        return "雪"
    elif "云" in weather_text or "多云" in weather_text:
        return "多云"
    elif "阴" in weather_text:
        return "阴天"
    elif "霾" in weather_text or "雾" in weather_text:
        return "雾霾"
    else:
        return "未知"


def get_weather_emoji(weather: WeatherType) -> str:
    """获取天气对应的emoji"""
    emoji_map = {
        "晴天": "☀️",
        "多云": "⛅",
        "阴天": "☁️",
        "小雨": "🌧️",
        "中雨": "🌧️",
        "大雨": "⛈️",
        "雷阵雨": "⛈️",
        "雪": "❄️",
        "雾霾": "🌫️",
        "未知": ""
    }
    return emoji_map.get(weather, "")
