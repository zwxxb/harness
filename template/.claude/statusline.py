#!/usr/bin/env python3
"""Compact Claude Code status line."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


def get(data: dict, *keys: str, default: object = "") -> object:
    current: object = data
    for key in keys:
        if not isinstance(current, dict):
            return default
        current = current.get(key, default)
    return current


def git_value(cwd: str, *args: str) -> str | None:
    try:
        return subprocess.check_output(
            ["git", "--no-optional-locks", *args],
            cwd=cwd,
            stderr=subprocess.DEVNULL,
            text=True,
            timeout=0.5,
        ).strip()
    except Exception:
        return None


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError:
        data = {}

    cwd = str(get(data, "workspace", "current_dir", default=os.getcwd()))
    model = str(get(data, "model", "display_name", default="Claude"))
    effort = str(get(data, "effort", "level", default="-"))
    pct = get(data, "context_window", "used_percentage", default=0)
    cost = get(data, "cost", "total_cost_usd", default=0)
    version = str(get(data, "version", default=""))

    branch = git_value(cwd, "branch", "--show-current") or "no-branch"
    dirty = git_value(cwd, "status", "--porcelain")
    if dirty is None:
        changed = "?"
    else:
        dirty_count = len([line for line in dirty.splitlines() if line.strip()])
        changed = f"+{dirty_count}" if dirty_count else "clean"
    folder = Path(cwd).name

    try:
        pct_text = f"{float(pct):.0f}%"
    except (TypeError, ValueError):
        pct_text = "?%"
    try:
        cost_text = f"${float(cost):.2f}"
    except (TypeError, ValueError):
        cost_text = "$?"

    print(f"[{model} | {effort}] {folder} {branch} {changed} | ctx {pct_text} | {cost_text} | {version}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

