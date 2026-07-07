#!/usr/bin/env python3
"""Validate the Claude coding harness package and optional installed target."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "template"

REQUIRED_TEMPLATE_FILES = [
    "template/.claude/settings.json",
    "template/.claude/CLAUDE.md",
    "template/.claude/agents/deep-reasoner.md",
    "template/.claude/agents/fast-worker.md",
    "template/.claude/skills/lead-orchestrator/SKILL.md",
    "template/.claude/statusline.py",
    "template/scripts/claude-lead.sh",
    "template/scripts/claude-plan.sh",
    "template/scripts/claude-sonnet-opus.sh",
    "template/scripts/gitnexus-graph.sh",
    "README.md",
    "docs/USAGE.md",
    "docs/ARCHITECTURE.md",
]

REQUIRED_TARGET_FILES = [
    ".claude/settings.json",
    ".claude/CLAUDE.md",
    ".claude/agents/deep-reasoner.md",
    ".claude/agents/fast-worker.md",
    ".claude/skills/lead-orchestrator/SKILL.md",
    ".claude/statusline.py",
    "scripts/claude-lead.sh",
    "scripts/claude-plan.sh",
    "scripts/claude-sonnet-opus.sh",
    "scripts/gitnexus-graph.sh",
]


class Check:
    def __init__(self) -> None:
        self.failures: list[str] = []

    def ok(self, message: str) -> None:
        print(f"ok  {message}")

    def fail(self, message: str) -> None:
        self.failures.append(message)
        print(f"bad {message}")

    def require(self, condition: bool, message: str) -> None:
        if condition:
            self.ok(message)
        else:
            self.fail(message)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate the Claude coding harness.")
    parser.add_argument("--target", type=Path, help="Optional installed target repo to validate.")
    return parser.parse_args()


def json_file(path: Path, check: Check) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        check.fail(f"{path} parses as JSON ({exc})")
        return {}
    check.ok(f"{path} parses as JSON")
    return data


def frontmatter(path: Path, required: list[str], check: Check) -> None:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        check.fail(f"{path} has frontmatter")
        return
    end = text.find("\n---\n", 4)
    if end == -1:
        check.fail(f"{path} closes frontmatter")
        return
    block = text[4:end]
    keys = {line.split(":", 1)[0].strip() for line in block.splitlines() if ":" in line}
    missing = [key for key in required if key not in keys]
    check.require(not missing, f"{path} frontmatter has {', '.join(required)}")


def command_output(command: list[str], cwd: Path) -> tuple[int, str]:
    try:
        result = subprocess.run(command, cwd=cwd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=10)
    except Exception as exc:
        return 1, str(exc)
    return result.returncode, result.stdout.strip()


def validate_package(check: Check) -> None:
    for rel in REQUIRED_TEMPLATE_FILES:
        path = ROOT / rel
        check.require(path.exists(), f"{rel} exists")

    settings = json_file(TEMPLATE / ".claude/settings.json", check)
    plugins = settings.get("enabledPlugins", {})
    check.require(plugins.get("superpowers@superpowers-dev") is True, "template enables Superpowers plugin")
    check.require(plugins.get("codex@openai-codex") is True, "template enables Codex plugin")
    check.require(settings.get("model") == "fable", "template main model is fable")
    check.require(settings.get("advisorModel") == "fable", "template advisor model is fable")

    frontmatter(TEMPLATE / ".claude/agents/deep-reasoner.md", ["name", "description", "model"], check)
    frontmatter(TEMPLATE / ".claude/agents/fast-worker.md", ["name", "description", "model"], check)
    frontmatter(TEMPLATE / ".claude/skills/lead-orchestrator/SKILL.md", ["name", "description"], check)

    plan_text = (TEMPLATE / "scripts/claude-plan.sh").read_text(encoding="utf-8")
    check.require("superpowers:brainstorming" in plan_text, "planning launcher mentions superpowers:brainstorming")
    check.require("superpowers:writing-plans" in plan_text, "planning launcher mentions superpowers:writing-plans")

    claude_md = (TEMPLATE / ".claude/CLAUDE.md").read_text(encoding="utf-8")
    orchestrator = (TEMPLATE / ".claude/skills/lead-orchestrator/SKILL.md").read_text(encoding="utf-8")
    check.require("GitNexus" in claude_md and "gitnexus://repo" in claude_md, "CLAUDE.md makes GitNexus primary for code search")
    check.require("gitnexus-graph.sh analyze" in orchestrator, "lead-orchestrator checks/builds GitNexus graph")

    probe = {
        "workspace": {"current_dir": str(ROOT)},
        "model": {"display_name": "Fable"},
        "effort": {"level": "max"},
        "context_window": {"used_percentage": 12.3},
        "cost": {"total_cost_usd": 0.12},
        "version": "test",
    }
    code, output = command_output(["python3", str(TEMPLATE / ".claude/statusline.py")], ROOT)
    check.require(code == 0, "statusline runs with empty input")
    status_proc = subprocess.run(
        ["python3", str(TEMPLATE / ".claude/statusline.py")],
        cwd=ROOT,
        input=json.dumps(probe),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=10,
    )
    check.require(status_proc.returncode == 0 and "Fable" in status_proc.stdout, "statusline renders Claude payload")

    claude = Path.home() / ".local/bin/claude"
    claude_bin = str(claude) if claude.exists() else shutil.which("claude")
    if claude_bin:
        code, output = command_output([claude_bin, "--version"], ROOT)
        check.require(code == 0, f"Claude Code available ({output})")
    else:
        check.fail("Claude Code binary available")


def validate_target(target: Path, check: Check) -> None:
    target = target.expanduser().resolve()
    check.require(target.exists(), f"target exists: {target}")
    for rel in REQUIRED_TARGET_FILES:
        check.require((target / rel).exists(), f"target has {rel}")
    if (target / ".claude/settings.json").exists():
        json_file(target / ".claude/settings.json", check)
    for rel in ["scripts/claude-lead.sh", "scripts/claude-plan.sh", "scripts/claude-sonnet-opus.sh", "scripts/gitnexus-graph.sh"]:
        path = target / rel
        if path.exists():
            check.require(os.access(path, os.X_OK), f"{rel} is executable")
    if (target / "scripts/claude-lead.sh").exists():
        code, output = command_output([str(target / "scripts/claude-lead.sh"), "--version"], target)
        check.require(code == 0, f"target launcher runs ({output})")


def main() -> int:
    args = parse_args()
    check = Check()
    validate_package(check)
    if args.target:
        validate_target(args.target, check)
    if check.failures:
        print("\nFailures:")
        for failure in check.failures:
            print(f"- {failure}")
        return 1
    print("\nAll checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
