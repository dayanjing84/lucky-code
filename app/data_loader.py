from __future__ import annotations

from pathlib import Path
import pandas as pd

REQUIRED_COLUMNS = ["号码", "预存", "低消", "分类说明"]


def load_numbers_excel(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"找不到 Excel 文件: {path}")

    df = pd.read_excel(path, dtype={"号码": str}, engine=None)

    # 标准化列名（容错：去空格）
    df.columns = [str(c).strip() for c in df.columns]

    # 基本校验
    for col in REQUIRED_COLUMNS:
        if col not in df.columns:
            raise ValueError(f"缺少必需列: {col}")

    # 号码转字符串，去空白
    df["号码"] = df["号码"].astype(str).str.replace(" ", "", regex=False).str.strip()

    # 数值列转浮点或保留原值
    for col in ("预存", "低消"):
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # 删除号码为空的行
    df = df[df["号码"].str.len() > 0].copy()

    return df

