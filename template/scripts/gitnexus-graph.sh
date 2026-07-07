#!/usr/bin/env bash
set -euo pipefail

repo_root="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$repo_root"

command_name="${1:-status}"
shift || true

runner=".gitnexus/run.cjs"

if [[ -f "$runner" ]]; then
  exec node "$runner" "$command_name" "$@"
fi

case "$command_name" in
  analyze)
    if command -v gitnexus >/dev/null 2>&1; then
      exec gitnexus analyze "$@"
    fi
    if command -v pnpm >/dev/null 2>&1; then
      exec pnpm dlx gitnexus@latest analyze "$@"
    fi
    if command -v npx >/dev/null 2>&1; then
      exec npx gitnexus analyze "$@"
    fi
    echo "GitNexus runner is missing and no gitnexus/pnpm/npx command is available." >&2
    exit 127
    ;;
  status)
    echo "No GitNexus runner found at .gitnexus/run.cjs." >&2
    echo "Build the graph with: ./scripts/gitnexus-graph.sh analyze" >&2
    exit 2
    ;;
  *)
    echo "No GitNexus runner found at .gitnexus/run.cjs." >&2
    echo "Run './scripts/gitnexus-graph.sh analyze' first, then retry '$command_name'." >&2
    exit 2
    ;;
esac
