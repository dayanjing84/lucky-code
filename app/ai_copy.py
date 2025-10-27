from __future__ import annotations

import json
import os
from datetime import datetime
from typing import Literal

from .config import CFG
from .holidays_util import get_holiday_name, season_by_month, date_cn_str


Tone = Literal["morning", "noon", "evening"]


def _local_fallback_copy(d: datetime, category: str, tone: Tone) -> dict:
    # 简单本地模板兜底
    holiday = get_holiday_name(d.date())
    season = season_by_month(d.month)
    date_str = date_cn_str(d.date())

    title_prefix = {
        "morning": "早安好号",
        "noon": "午间好号",
        "evening": "夜场好号",
    }[tone]

    if holiday:
        title = f"{title_prefix}·{holiday}专享"
        tagline = f"{season}{category}精选号源，幸运与优惠同到来，限时速抢！"
    else:
        title = f"{title_prefix}·{season}专场"
        tagline = f"{category}好号来袭，幸运好号与多重优惠，错过不再！"

    return {
        "title": title,
        "tagline": tagline,
        "meta": {
            "date": date_str,
            "holiday": holiday,
            "season": season,
            "source": "local",
        },
    }


def _compose_prompt(d: datetime, category: str, tone: Tone) -> str:
    date_str = date_cn_str(d.date())
    holiday = get_holiday_name(d.date()) or "无"
    season = season_by_month(d.month)

    style_hint = {
        "morning": "清新、提气",
        "noon": "活泼、热闹",
        "evening": "温暖、收尾",
    }[tone]

    return (
        "请根据今天的日期、节日、时令、近期热门事件，为中国移动吉祥号码促销活动生成中文广告文案。\n"
        "要求：\n"
        "1) 输出 JSON 格式：{\"title\": 标题, \"tagline\": 宣传语}，不要解释与多余字段。\n"
        "2) 标题8-12字，宣传语约30字，口语化，积极向上。\n"
        "3) 必须包含：幸运、好号、优惠 等关键词。\n"
        f"4) 日期：{date_str}；节日：{holiday}；时令：{season}；分类：{category}；风格偏好：{style_hint}。\n"
        "5) 倾向结合当下热点但避免敏感与带争议内容。\n"
    )


def _try_openai_client():
    # 尝试新 SDK
    try:
        from openai import OpenAI  # type: ignore

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return None, None
        client = OpenAI(api_key=api_key)
        return client, "sdk_v1"
    except Exception:
        pass

    # 尝试旧 SDK
    try:
        import openai  # type: ignore

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return None, None
        openai.api_key = api_key
        return openai, "sdk_legacy"
    except Exception:
        return None, None


def generate_copy(d: datetime, category: str, tone: Tone) -> dict:
    client, mode = _try_openai_client()
    prompt = _compose_prompt(d, category, tone)

    if client is None:
        return _local_fallback_copy(d, category, tone)

    try:
        if mode == "sdk_v1":
            resp = client.chat.completions.create(
                model=CFG.openai_model,
                messages=[
                    {"role": "system", "content": "你是专业中文广告文案助手。"},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.8,
                max_tokens=300,
            )
            text = resp.choices[0].message.content or ""
        else:
            # legacy
            text = client.ChatCompletion.create(
                model=getattr(CFG, "openai_model", "gpt-3.5-turbo"),
                messages=[
                    {"role": "system", "content": "你是专业中文广告文案助手。"},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.8,
                max_tokens=300,
            )["choices"][0]["message"]["content"]

        # 解析 JSON
        text = text.strip()
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1:
            raw = text[start : end + 1]
            obj = json.loads(raw)
            title = str(obj.get("title", "好号专场")).strip()
            tagline = str(obj.get("tagline", "幸运好号，多重优惠，限时抢购！")).strip()
        else:
            # 回落：简单切分
            lines = text.replace("：", ":").splitlines()
            title = "好号专场"
            tagline = "幸运好号，多重优惠，限时抢购！"
            for ln in lines:
                if "title" in ln.lower():
                    title = ln.split(":", 1)[-1].strip()
                if "tagline" in ln.lower():
                    tagline = ln.split(":", 1)[-1].strip()

        return {
            "title": title[:18] if len(title) > 18 else title,
            "tagline": tagline,
            "meta": {"source": "openai"},
        }
    except Exception:
        return _local_fallback_copy(d, category, tone)

