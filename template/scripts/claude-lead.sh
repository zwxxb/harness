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
  "$@"

