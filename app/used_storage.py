from __future__ import annotations

from pathlib import Path
from typing import Iterable
import json
from datetime import datetime


class UsedStorage:
    def __init__(self, path: Path) -> None:
        self.path = path
        self._data = {"used_numbers": {}, "log": []}
        self._loaded = False

    def load(self) -> None:
        if self._loaded:
            return
        if self.path.exists():
            try:
                self._data = json.loads(self.path.read_text(encoding="utf-8"))
            except Exception:
                # 兜底，避免文件损坏导致崩溃
                self._data = {"used_numbers": {}, "log": []}
        self._loaded = True

    def save(self) -> None:
        if not self._loaded:
            return
        self.path.write_text(json.dumps(self._data, ensure_ascii=False, indent=2), encoding="utf-8")

    def is_used(self, number: str) -> bool:
        self.load()
        return number in self._data.get("used_numbers", {})

    def mark_used(self, numbers: Iterable[str], *, category: str, output_path: str, ts: str | None = None) -> None:
        self.load()
        if ts is None:
            ts = datetime.now().isoformat(timespec="seconds")
        used = self._data.setdefault("used_numbers", {})
        for n in numbers:
            if n not in used:
                used[n] = {
                    "first_used_at": ts,
                    "category": category,
                    "outputs": [output_path],
                }
            else:
                used[n].setdefault("outputs", []).append(output_path)
        self._data.setdefault("log", []).append({
            "ts": ts,
            "category": category,
            "numbers": list(numbers),
            "output": output_path,
        })
        self.save()

    def category_used_ever(self, category: str) -> bool:
        self.load()
        for n, meta in self._data.get("used_numbers", {}).items():
            if meta.get("category") == category:
                return True
        return False

