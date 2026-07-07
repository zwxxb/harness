#!/usr/bin/env python3
"""Install the Claude coding harness template into a target repository."""

from __future__ import annotations

import argparse
import json
import shutil
import stat
import sys
import time
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "template"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Install the Claude coding harness into a repo.")
    parser.add_argument("--target", type=Path, default=Path.cwd(), help="Target repository root.")
    parser.add_argument("--force", action="store_true", help="Overwrite existing files after backing them up.")
    parser.add_argument("--dry-run", action="store_true", help="Show planned changes without writing.")
    return parser.parse_args()


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def merge_settings(existing: Any, template: Any) -> Any:
    if isinstance(existing, dict) and isinstance(template, dict):
        merged = dict(existing)
        for key, value in template.items():
            if key in merged:
                merged[key] = merge_settings(merged[key], value)
            else:
                merged[key] = value
        return merged
    if isinstance(existing, list) and isinstance(template, list):
        merged = list(existing)
        for item in template:
            if item not in merged:
                merged.append(item)
        return merged
    return template


def backup(path: Path) -> Path:
    stamp = time.strftime("%Y%m%d-%H%M%S")
    backup_path = path.with_name(f"{path.name}.bak-{stamp}")
    shutil.copy2(path, backup_path)
    return backup_path


def write_file(path: Path, content: bytes, executable: bool, dry_run: bool) -> None:
    if dry_run:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)
    if executable:
        mode = path.stat().st_mode
        path.chmod(mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def install_file(source: Path, target: Path, force: bool, dry_run: bool) -> str:
    executable = bool(source.stat().st_mode & stat.S_IXUSR) or source.suffix == ".sh"
    content = source.read_bytes()

    if source.relative_to(TEMPLATE).as_posix() == ".claude/settings.json" and target.exists():
        merged = merge_settings(read_json(target), read_json(source))
        content = (json.dumps(merged, indent=2, ensure_ascii=False) + "\n").encode("utf-8")

    if target.exists() and target.read_bytes() == content:
        return f"unchanged {target}"

    if target.exists() and not force and source.relative_to(TEMPLATE).as_posix() != ".claude/settings.json":
        return f"skip existing {target} (use --force to overwrite)"

    note = "write"
    if target.exists():
        note = f"backup {backup(target) if not dry_run else target.with_suffix(target.suffix + '.bak-*')} then write"
    write_file(target, content, executable, dry_run)
    return f"{note} {target}"


def iter_template_files() -> list[Path]:
    ignored_parts = {"__pycache__", ".DS_Store"}
    files: list[Path] = []
    for path in TEMPLATE.rglob("*"):
        if not path.is_file():
            continue
        if any(part in ignored_parts for part in path.parts):
            continue
        if path.suffix in {".pyc", ".pyo"}:
            continue
        files.append(path)
    return sorted(files)


def main() -> int:
    args = parse_args()
    target_root = args.target.expanduser().resolve()
    if not TEMPLATE.exists():
        print(f"Template missing: {TEMPLATE}", file=sys.stderr)
        return 1
    if not target_root.exists():
        print(f"Target does not exist: {target_root}", file=sys.stderr)
        return 1
    if not target_root.is_dir():
        print(f"Target is not a directory: {target_root}", file=sys.stderr)
        return 1

    actions: list[str] = []
    for source in iter_template_files():
        rel = source.relative_to(TEMPLATE)
        actions.append(install_file(source, target_root / rel, args.force, args.dry_run))

    for action in actions:
        print(action)

    if args.dry_run:
        print("Dry run only. No files changed.")
    else:
        print(f"Installed harness into {target_root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
