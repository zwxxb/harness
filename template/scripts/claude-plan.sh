#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

claude_bin="${CLAUDE_BIN:-}"
if [[ -z "$claude_bin" ]]; then
  if [[ -x "$HOME/.local/bin/claude" ]]; then
    claude_bin="$HOME/.local/bin/claude"
  else
    claude_bin="$(command -v claude)"
  fi
fi

exec "$claude_bin" \
  --model "${CLAUDE_MAIN_MODEL:-fable}" \
  --advisor "${CLAUDE_ADVISOR_MODEL:-fable}" \
  --append-system-prompt "Planning workflow for this session: use Superpowers skills for planning. For broad features, behavior changes, architecture, or complex debugging, invoke superpowers:brainstorming first to explore context, ask clarifying questions, compare approaches, and write an approved design spec under docs/superpowers/specs/. After the design/spec is approved, invoke superpowers:writing-plans to write the implementation plan under docs/superpowers/plans/. Do not use native /plan as the primary planning workflow unless the user explicitly requests Claude Code plan mode." \
  "$@"

