from __future__ import annotations

from typing import Iterable
import random
import pandas as pd

from .used_storage import UsedStorage


def categories_with_counts(df: pd.DataFrame) -> dict[str, int]:
    counts = (
        df.groupby("分类说明")["号码"].count().sort_values(ascending=False)
    )
    return counts.to_dict()


def _unused_numbers_in_category(df: pd.DataFrame, store: UsedStorage, category: str) -> list[dict]:
    subset = df[df["分类说明"] == category]
    rows = []
    for _, r in subset.iterrows():
        num = str(r["号码"]).strip()
        if not store.is_used(num):
            rows.append({
                "号码": num,
                "预存": float(r["预存"]) if pd.notna(r["预存"]) else None,
                "低消": float(r["低消"]) if pd.notna(r["低消"]) else None,
                "分类说明": category,
            })
    return rows


def choose_category(
    df: pd.DataFrame,
    store: UsedStorage,
    *,
    preferred: str | None,
    priority_list: Iterable[str],
    min_count: int = 15,
    randomize: bool = False,
) -> str | None:
    # 若指定分类，且满足数量，直接使用
    if preferred:
        avail = _unused_numbers_in_category(df, store, preferred)
        if len(avail) >= min_count:
            return preferred

    # 优先未使用过的分类；默认按固定优先级排序
    categories = list(df["分类说明"].dropna().astype(str).unique())
    # stable order by priority_list index, else after
    prio_index = {c: i for i, c in enumerate(priority_list)}
    if not randomize:
        categories.sort(key=lambda c: (prio_index.get(c, 10_000), c))
    else:
        random.shuffle(categories)

    unused_first = []
    used_later = []
    for cat in categories:
        rows = _unused_numbers_in_category(df, store, cat)
        if len(rows) < min_count:
            continue
        if store.category_used_ever(cat):
            used_later.append(cat)
        else:
            unused_first.append(cat)

    for group in (unused_first, used_later):
        if group:
            if randomize:
                return random.choice(group)
            return group[0]
    return None


def pick_numbers_for_category(
    df: pd.DataFrame,
    store: UsedStorage,
    category: str,
    *,
    count: int = 15,
) -> list[dict]:
    rows = _unused_numbers_in_category(df, store, category)
    return rows[:count]
