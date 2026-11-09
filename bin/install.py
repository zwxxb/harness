#!/usr/bin/env python3
"""Install the review harness into a target repository.

Copies HARNESS.md and .harness/ (gate + passes), adds a pointer block to
AGENTS.md, CLAUDE.md, and GEMINI.md (existing content is kept), and creates
the ledger.
"""

import argparse
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "template"

# AGENTS.md is read natively by most coding agents; Claude Code and Gemini CLI
# read their own file by default.
POINTER_FILES = ("AGENTS.md", "CLAUDE.md", "GEMINI.md")
BEGIN, END = "<!-- harness:begin -->", "<!-- harness:end -->"
POINTER = f"""{BEGIN}
## Review harness

For any substantial change, read and follow `HARNESS.md`: brainstorm and
plan first, execute the plan task by task, then review rounds (hunt, triage,
fix, prove, regress) until `python3 .harness/gate.py` exits 0, then a deslop
+ simplify pass and one clean confirmation round.
{END}
"""
BLOCK = re.compile(re.escape(BEGIN) + ".*?" + re.escape(END) + "\n?", re.DOTALL)


def core_files() -> list[Path]:
    return sorted(p for p in TEMPLATE.rglob("*") if p.is_file() and "__pycache__" not in p.parts)


def install_core(source: Path, target: Path, force: bool) -> str:
    content = source.read_bytes()
    if target.exists() and target.read_bytes() == content:
        return f"unchanged {target}"
    if target.exists() and not force:
        return f"skip changed {target} (use --force to overwrite)"
    note = "write"
    if target.exists():
        backup = target.with_name(f"{target.name}.bak-{time.strftime('%Y%m%d-%H%M%S')}")
        shutil.copy2(target, backup)
        note = f"backup to {backup.name} and write"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(content)
    return f"{note} {target}"


def install_pointer(target: Path) -> str:
    text = target.read_text(encoding="utf-8") if target.exists() else ""
    if BLOCK.search(text):
        updated = BLOCK.sub(lambda _: POINTER, text, count=1)
    else:
        updated = text.rstrip("\n") + "\n\n" + POINTER if text.strip() else POINTER
    if updated == text:
        return f"unchanged {target}"
    target.write_text(updated, encoding="utf-8")
    return f"{'update' if text else 'write'} {target}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Install the review harness into a repo.")
    parser.add_argument("--target", type=Path, default=Path.cwd(), help="Target repository root.")
    parser.add_argument("--force", action="store_true", help="Overwrite changed harness files after a backup.")
    args = parser.parse_args()

    root = args.target.expanduser().resolve()
    if not root.is_dir():
        print(f"Target is not a directory: {root}", file=sys.stderr)
        return 1

    for source in core_files():
        print(install_core(source, root / source.relative_to(TEMPLATE), args.force))
    for name in POINTER_FILES:
        print(install_pointer(root / name))
    if not (root / ".harness/ledger.md").exists():
        subprocess.run([sys.executable, ".harness/gate.py", "--init"], cwd=root, check=True, capture_output=True)
        print(f"write {root / '.harness/ledger.md'}")
    print(f"Installed into {root}. Gate: python3 .harness/gate.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
