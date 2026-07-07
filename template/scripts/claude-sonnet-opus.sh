#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

export CLAUDE_MAIN_MODEL="${CLAUDE_MAIN_MODEL:-sonnet}"
export CLAUDE_ADVISOR_MODEL="${CLAUDE_ADVISOR_MODEL:-opus}"

exec "$repo_root/scripts/claude-lead.sh" "$@"

