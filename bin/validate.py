#!/usr/bin/env python3
"""Validate the review harness package, and optionally an installed repo."""

import argparse
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from install import BEGIN, POINTER_FILES, ROOT, TEMPLATE, core_files

SELF = Path(__file__).resolve()
PASS_REF = re.compile(r"\.harness/passes/[a-z0-9-]+\.md")
FORBIDDEN = ("gitnexus", ".claude/")  # removed by design; must not creep back


class Check:
    def __init__(self) -> None:
        self.failures: list[str] = []

    def require(self, condition: bool, message: str, bad: list[str] | None = None) -> None:
        if condition:
            print(f"ok  {message}")
            return
        self.failures.append(message)
        print(f"bad {message}" + (f": {', '.join(bad)}" if bad else ""))


def run(command: list[str], cwd: Path) -> tuple[int, str]:
    result = subprocess.run(command, cwd=cwd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return result.returncode, result.stdout


def package_texts() -> dict[Path, str]:
    return {
        p: p.read_text(encoding="utf-8", errors="replace")
        for p in ROOT.rglob("*")
        if p.is_file() and not ({".git", "__pycache__"} & set(p.parts)) and p.resolve() != SELF
    }


def gate_probe(check: Check, harness_dir: Path, label: str) -> None:
    """Exercise the real gate on a scratch copy: init, block, pass, reject malformed."""
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp)
        shutil.copytree(harness_dir, work / ".harness",
                        ignore=shutil.ignore_patterns("__pycache__", "ledger.md", "rounds"))
        gate = [sys.executable, ".harness/gate.py"]
        ledger = work / ".harness/ledger.md"

        code, _ = run(gate + ["--init"], work)
        check.require(code == 0 and ledger.is_file(), f"{label}: --init creates a passing empty ledger")
        seed = ledger.read_text(encoding="utf-8")
        for record, expected, message in [
            ("### F-901 [open] high", 1, "open high blocks"),
            ("### F-901 [fixed] high", 0, "fixed high passes"),
            ("### oops [broken] huge", 2, "malformed record is rejected"),
        ]:
            ledger.write_text(f"{seed}\n{record}\n", encoding="utf-8")
            code, out = run(gate, work)
            named = expected != 1 or "F-901" in out
            check.require(code == expected and named, f"{label}: {message} (exit {expected})")

        ledger.write_text(seed, encoding="utf-8")
        code, _ = run(gate + ["--done"], work)
        check.require(code == 1, f"{label}: --done fails without round reports")
        (work / ".harness/rounds").mkdir()
        for n in (1, 2):
            (work / f".harness/rounds/round-0{n}.md").write_text("report", encoding="utf-8")
        code, _ = run(gate + ["--done"], work)
        check.require(code == 0, f"{label}: --done passes with a clean ledger and two rounds")


def validate_package(check: Check) -> None:
    texts = package_texts()
    pass_files = {f".harness/passes/{p.name}" for p in (TEMPLATE / ".harness/passes").glob("*.md")}
    refs = set(PASS_REF.findall(texts[TEMPLATE / "HARNESS.md"]))
    check.require(refs == pass_files, "HARNESS.md references every pass file and nothing else",
                  sorted(refs ^ pass_files))
    dangling = sorted({f"{ref} in {p.relative_to(ROOT)}" for p, t in texts.items()
                       for ref in PASS_REF.findall(t) if ref not in pass_files})
    check.require(not dangling, "every pass reference resolves", dangling)
    hits = sorted(str(p.relative_to(ROOT)) for p, t in texts.items()
                  if any(token in t.lower() for token in FORBIDDEN))
    check.require(not hits, f"no references to removed tooling ({', '.join(FORBIDDEN)})", hits)

    gate_probe(check, TEMPLATE / ".harness", "gate")

    with tempfile.TemporaryDirectory() as tmp:
        target = Path(tmp)
        (target / "AGENTS.md").write_text("# Existing rules\nkeep me\n", encoding="utf-8")
        install = [sys.executable, str(ROOT / "bin/install.py"), "--target", str(target)]

        code, _ = run(install, ROOT)
        expected = [str(p.relative_to(TEMPLATE)) for p in core_files()] + list(POINTER_FILES) + [".harness/ledger.md"]
        missing = [rel for rel in expected if not (target / rel).is_file()]
        check.require(code == 0 and not missing, "install writes the core, pointers, and ledger", missing)
        agents = (target / "AGENTS.md").read_text(encoding="utf-8")
        check.require("keep me" in agents and agents.count(BEGIN) == 1,
                      "pointer block is added once and existing AGENTS.md content is kept")

        code, out = run(install, ROOT)
        changed = [line for line in out.splitlines() if line.startswith(("write", "update", "backup"))]
        check.require(code == 0 and not changed, "re-install is idempotent", changed)

        (target / "HARNESS.md").write_text("local edit", encoding="utf-8")
        code, _ = run(install + ["--force"], ROOT)
        check.require(code == 0 and any(target.glob("HARNESS.md.bak-*")), "--force backs up before overwriting")

        ledger = target / ".harness/ledger.md"
        before = ledger.read_text(encoding="utf-8")
        validate_target(check, target)
        check.require(ledger.read_text(encoding="utf-8") == before, "target validation leaves the ledger untouched")


def validate_target(check: Check, target: Path) -> None:
    expected = [str(p.relative_to(TEMPLATE)) for p in core_files()] + [".harness/ledger.md"]
    missing = [rel for rel in expected if not (target / rel).is_file()]
    check.require(not missing, "target has the harness core and ledger", missing)
    gate_probe(check, target / ".harness", "target gate")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the review harness.")
    parser.add_argument("--target", type=Path, help="Installed repo to validate as well.")
    args = parser.parse_args()

    check = Check()
    validate_package(check)
    if args.target:
        validate_target(check, args.target.expanduser().resolve())
    print(f"\nFAILED: {len(check.failures)} check(s)" if check.failures else "\nAll checks passed.")
    return 1 if check.failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
