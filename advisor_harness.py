#!/usr/bin/env python3
"""Dependency-free harness for Anthropic's beta advisor tool."""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from copy import deepcopy
from pathlib import Path
from typing import Any


API_URL = "https://api.anthropic.com/v1/messages"
BETA_HEADER = "advisor-tool-2026-03-01"
ANTHROPIC_VERSION = "2023-06-01"

ADVISOR_BREVITY_PREFIX = (
    "(Advisor: please keep your guidance under 120 words. Focus on the "
    "highest-risk decision, the next concrete step, and one failure mode to "
    "check.)\n\n"
)

CODING_SYSTEM_PROMPT = """You have access to an `advisor` tool backed by a stronger reviewer model. It takes NO parameters -- when you call advisor(), your entire conversation history is automatically forwarded. They see the task, every tool call you've made, every result you've seen.

Call advisor BEFORE substantive work -- before writing, before committing to an interpretation, before building on an assumption. If the task requires orientation first (finding files, fetching a source, seeing what's there), do that, then call advisor. Orientation is not substantive work. Writing, editing, and declaring an answer are.

Also call advisor:
- When you believe the task is complete. BEFORE this call, make your deliverable durable: write the file, save the result, commit the change. The advisor call takes time; if the session ends during it, a durable result persists and an unwritten one doesn't.
- When stuck -- errors recurring, approach not converging, results that don't fit.
- When considering a change of approach.

On tasks longer than a few steps, call advisor at least once before committing to an approach and once before declaring done. On short reactive tasks where the next action is dictated by tool output you just read, you don't need to keep calling -- the advisor adds most of its value on the first call, before the approach crystallizes.

Give the advice serious weight. If you follow a step and it fails empirically, or you have primary-source evidence that contradicts a specific claim, adapt. A passing self-test is not evidence the advice is wrong -- it's evidence your test doesn't check what the advice is checking.

If you've already retrieved data pointing one way and the advisor points another: don't silently switch. Surface the conflict in one more advisor call and ask which constraint breaks the tie."""

HAIKU_CODING_EXTRA = """Call advisor for design, architecture, and risk questions where you won't touch a file. If your response would be analysis or a recommendation with no other tool calls, call advisor first -- that judgment call is exactly where a second opinion is highest-value.

Hard rule: your first write_file, edit_file, or state-changing bash call on a task must be preceded by an advisor call in the same or an earlier turn. Read-only orientation commands are not state-changing. This is a checkpoint, not a difficulty judgment. It applies to one-line edits too."""

NUDGE_TEXT = (
    "You have not consulted the advisor yet. If the task has a non-obvious "
    "design decision or a failure mode you haven't ruled out, call advisor "
    "now before committing to an approach."
)

PRESETS: dict[str, dict[str, Any]] = {
    "balanced": {
        "executor_model": "claude-sonnet-4-6",
        "advisor_model": "claude-opus-4-8",
        "max_tokens": 4096,
        "advisor_max_tokens": 2048,
        "advisor_max_uses_per_request": 2,
        "advisor_conversation_max": 3,
        "advisor_cache_ttl": "5m",
        "system_prompt": CODING_SYSTEM_PROMPT,
        "nudge_turn": 0,
    },
    "haiku-coding": {
        "executor_model": "claude-haiku-4-5",
        "advisor_model": "claude-opus-4-8",
        "max_tokens": 4096,
        "advisor_max_tokens": 2048,
        "advisor_max_uses_per_request": 2,
        "advisor_conversation_max": 3,
        "advisor_cache_ttl": "5m",
        "system_prompt": CODING_SYSTEM_PROMPT + "\n\n" + HAIKU_CODING_EXTRA,
        "nudge_turn": 2,
    },
    "max-quality": {
        "executor_model": "claude-sonnet-4-6",
        "advisor_model": "claude-opus-4-8",
        "max_tokens": 8192,
        "advisor_max_tokens": 4096,
        "advisor_max_uses_per_request": 3,
        "advisor_conversation_max": 4,
        "advisor_cache_ttl": "1h",
        "system_prompt": CODING_SYSTEM_PROMPT,
        "nudge_turn": 0,
    },
}

VALID_ADVISORS_BY_EXECUTOR = {
    "claude-haiku-4-5-20251001": {
        "claude-sonnet-4-6",
        "claude-opus-4-6",
        "claude-opus-4-7",
        "claude-opus-4-8",
        "claude-fable-5",
        "claude-mythos-5",
    },
    "claude-haiku-4-5": {
        "claude-sonnet-4-6",
        "claude-opus-4-6",
        "claude-opus-4-7",
        "claude-opus-4-8",
        "claude-fable-5",
        "claude-mythos-5",
    },
    "claude-sonnet-4-6": {
        "claude-sonnet-4-6",
        "claude-opus-4-6",
        "claude-opus-4-7",
        "claude-opus-4-8",
        "claude-fable-5",
        "claude-mythos-5",
    },
    "claude-sonnet-5": {"claude-opus-4-7", "claude-opus-4-8", "claude-fable-5", "claude-mythos-5"},
    "claude-opus-4-6": {"claude-opus-4-6", "claude-opus-4-7", "claude-opus-4-8", "claude-fable-5", "claude-mythos-5"},
    "claude-opus-4-7": {"claude-opus-4-7", "claude-opus-4-8", "claude-fable-5", "claude-mythos-5"},
    "claude-opus-4-8": {"claude-opus-4-7", "claude-opus-4-8", "claude-fable-5", "claude-mythos-5"},
    "claude-fable-5": {"claude-fable-5"},
    "claude-mythos-5": {"claude-mythos-5"},
}


def env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if not value:
        return default
    try:
        return int(value)
    except ValueError:
        raise SystemExit(f"{name} must be an integer, got {value!r}")


def load_dotenv(path: Path) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Anthropic Messages with the beta advisor tool.")
    parser.add_argument("task", nargs="?", help="Task to send to the executor.")
    parser.add_argument("--preset", choices=sorted(PRESETS), default=os.getenv("ADVISOR_PRESET", "balanced"))
    parser.add_argument("--executor-model", default=os.getenv("EXECUTOR_MODEL"))
    parser.add_argument("--advisor-model", default=os.getenv("ADVISOR_MODEL"))
    parser.add_argument("--max-tokens", type=int)
    parser.add_argument("--advisor-max-tokens", type=int, default=None)
    parser.add_argument("--advisor-max-uses-per-request", type=int, default=None)
    parser.add_argument("--advisor-conversation-max", type=int, default=None)
    parser.add_argument("--advisor-cache-ttl", choices=["off", "5m", "1h"], default=os.getenv("ADVISOR_CACHE_TTL"))
    parser.add_argument("--max-turns", type=int, default=10)
    parser.add_argument("--no-brevity-prefix", action="store_true")
    parser.add_argument("--show-advisor", action="store_true")
    parser.add_argument("--transcript", type=Path, help="Existing transcript JSON to continue.")
    parser.add_argument("--save", type=Path, help="Path for transcript JSON. Defaults to runs/advisor-*.json.")
    parser.add_argument("--print-config", action="store_true", help="Print resolved setup and exit without calling the API.")
    return parser.parse_args()


def resolved_config(args: argparse.Namespace) -> dict[str, Any]:
    preset = deepcopy(PRESETS[args.preset])
    preset["executor_model"] = args.executor_model or preset["executor_model"]
    preset["advisor_model"] = args.advisor_model or preset["advisor_model"]
    preset["max_tokens"] = args.max_tokens or env_int("MAX_TOKENS", preset["max_tokens"])
    preset["advisor_max_tokens"] = args.advisor_max_tokens or env_int("ADVISOR_MAX_TOKENS", preset["advisor_max_tokens"])
    preset["advisor_max_uses_per_request"] = args.advisor_max_uses_per_request or env_int(
        "ADVISOR_MAX_USES_PER_REQUEST", preset["advisor_max_uses_per_request"]
    )
    preset["advisor_conversation_max"] = args.advisor_conversation_max or env_int(
        "ADVISOR_CONVERSATION_MAX", preset["advisor_conversation_max"]
    )
    if args.advisor_cache_ttl:
        preset["advisor_cache_ttl"] = args.advisor_cache_ttl

    allowed = VALID_ADVISORS_BY_EXECUTOR.get(preset["executor_model"])
    if allowed is not None and preset["advisor_model"] not in allowed:
        raise SystemExit(
            f"Invalid advisor pair: executor {preset['executor_model']} cannot use "
            f"advisor {preset['advisor_model']}."
        )
    if preset["advisor_max_tokens"] < 1024:
        raise SystemExit("advisor max_tokens must be at least 1024.")
    return preset


def advisor_tool(config: dict[str, Any]) -> dict[str, Any]:
    tool: dict[str, Any] = {
        "type": "advisor_20260301",
        "name": "advisor",
        "model": config["advisor_model"],
        "max_uses": config["advisor_max_uses_per_request"],
        "max_tokens": config["advisor_max_tokens"],
    }
    ttl = config.get("advisor_cache_ttl")
    if ttl and ttl != "off":
        tool["caching"] = {"type": "ephemeral", "ttl": ttl}
    return tool


def is_advisor_block(block: Any) -> bool:
    return isinstance(block, dict) and (
        block.get("type") == "advisor_tool_result"
        or (block.get("type") == "server_tool_use" and block.get("name") == "advisor")
    )


def strip_advisor_blocks(messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    stripped: list[dict[str, Any]] = []
    for message in messages:
        content = message.get("content")
        if isinstance(content, list):
            new_content = [block for block in content if not is_advisor_block(block)]
            stripped.append({**message, "content": new_content})
        else:
            stripped.append(message)
    return stripped


def count_advisor_calls(messages: list[dict[str, Any]]) -> int:
    calls = 0
    for message in messages:
        content = message.get("content")
        if not isinstance(content, list):
            continue
        calls += sum(
            1
            for block in content
            if isinstance(block, dict) and block.get("type") == "server_tool_use" and block.get("name") == "advisor"
        )
    return calls


def extract_text(content: list[dict[str, Any]], show_advisor: bool) -> str:
    parts: list[str] = []
    for block in content:
        block_type = block.get("type")
        if block_type == "text":
            parts.append(block.get("text", ""))
        elif show_advisor and block_type == "advisor_tool_result":
            advisor_content = block.get("content", {})
            if advisor_content.get("type") == "advisor_result":
                parts.append("\n[advisor]\n" + advisor_content.get("text", ""))
            elif advisor_content.get("type") == "advisor_tool_result_error":
                parts.append("\n[advisor error]\n" + advisor_content.get("error_code", "unknown"))
            elif advisor_content.get("type") == "advisor_redacted_result":
                parts.append("\n[advisor]\n<redacted advisor result>")
    return "\n".join(part for part in parts if part)


RETRY_STATUSES = {429, 500, 502, 503, 529}


def request_message(api_key: str, payload: dict[str, Any]) -> dict[str, Any]:
    body = json.dumps(payload).encode("utf-8")
    headers = {
        "x-api-key": api_key,
        "anthropic-version": ANTHROPIC_VERSION,
        "anthropic-beta": BETA_HEADER,
        "content-type": "application/json",
    }
    for attempt in range(3):
        request = urllib.request.Request(API_URL, data=body, method="POST", headers=headers)
        try:
            with urllib.request.urlopen(request, timeout=600) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            if exc.code in RETRY_STATUSES and attempt < 2:
                time.sleep(2 ** attempt)
                continue
            detail = exc.read().decode("utf-8", errors="replace")
            raise SystemExit(f"Anthropic API error {exc.code}:\n{detail}") from exc
        except urllib.error.URLError as exc:
            if attempt < 2:
                time.sleep(2 ** attempt)
                continue
            raise SystemExit(f"Anthropic API network error: {exc}") from exc
    raise SystemExit("Anthropic API retries exhausted.")


def default_save_path() -> Path:
    stamp = time.strftime("%Y%m%d-%H%M%S")
    return Path("runs") / f"advisor-transcript-{stamp}.json"


def load_transcript(path: Path) -> tuple[list[dict[str, Any]], dict[str, Any] | None]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict) and isinstance(data.get("messages"), list):
        return data["messages"], data.get("config")
    if isinstance(data, list):
        return data, None
    raise SystemExit(f"Transcript {path} must be a JSON list or an object with a messages list.")


def save_transcript(path: Path, messages: list[dict[str, Any]], config: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps({"config": config, "messages": messages}, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    load_dotenv(Path(".env"))
    args = parse_args()
    config = resolved_config(args)

    if args.print_config:
        printable = {k: v for k, v in config.items() if k != "system_prompt"}
        printable["tool"] = advisor_tool(config)
        print(json.dumps(printable, indent=2))
        return 0

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise SystemExit("Set ANTHROPIC_API_KEY or add it to .env before running.")

    if args.transcript:
        messages, saved_config = load_transcript(args.transcript)
        if saved_config:
            config = {**config, **{k: v for k, v in saved_config.items() if k != "system_prompt"}}
        if args.task:
            content = args.task if args.no_brevity_prefix else ADVISOR_BREVITY_PREFIX + args.task
            messages.append({"role": "user", "content": content})
    else:
        if not args.task:
            raise SystemExit("Provide a task, or pass --transcript to continue an existing conversation.")
        content = args.task if args.no_brevity_prefix else ADVISOR_BREVITY_PREFIX + args.task
        messages = [{"role": "user", "content": content}]

    save_path = args.save or default_save_path()
    advisor_called_before_turn = count_advisor_calls(messages) > 0

    for turn in range(1, args.max_turns + 1):
        advisor_calls = count_advisor_calls(messages)
        use_advisor = advisor_calls < config["advisor_conversation_max"]
        request_messages = messages if use_advisor else strip_advisor_blocks(messages)
        tools = [advisor_tool(config)] if use_advisor else []

        payload: dict[str, Any] = {
            "model": config["executor_model"],
            "max_tokens": config["max_tokens"],
            "messages": request_messages,
            "system": [
                {
                    "type": "text",
                    "text": config["system_prompt"],
                    "cache_control": {"type": "ephemeral"},
                }
            ],
        }
        if tools:
            payload["tools"] = tools

        response = request_message(api_key, payload)
        content = response.get("content", [])
        messages.append({"role": "assistant", "content": content})
        save_transcript(save_path, messages, config)

        assistant_text = extract_text(content, args.show_advisor)
        if assistant_text:
            print(assistant_text)

        advisor_called_now = count_advisor_calls([{"role": "assistant", "content": content}]) > 0
        advisor_called_before_turn = advisor_called_before_turn or advisor_called_now
        stop_reason = response.get("stop_reason")

        if stop_reason == "pause_turn":
            continue

        if stop_reason == "tool_use":
            print(
                "\nThe executor requested a client-side tool, but this harness only wires the server-side "
                "advisor tool. Add your tool dispatcher before using this flow with custom tools.",
                file=sys.stderr,
            )
            break

        if (
            config.get("nudge_turn")
            and turn == config["nudge_turn"] - 1
            and not advisor_called_before_turn
            and stop_reason != "end_turn"
        ):
            messages.append({"role": "user", "content": NUDGE_TEXT})
            continue

        break

    print(f"\nTranscript saved to {save_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

