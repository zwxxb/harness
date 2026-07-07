---
name: deslop
description: Remove AI-generated code slop and clean up code style. Run on the branch diff after implementation passes focused verification, before the quality-review completion gate. Ported from Cursor team kit.
---

# Remove AI code slop

Check the diff against main and remove AI-generated slop introduced in the branch.

## Focus Areas

- Extra comments that are unnecessary or inconsistent with local style
- Defensive checks or try/catch blocks that are abnormal for trusted code paths
- Casts to `any` used only to bypass type issues
- Deeply nested code that should be simplified with early returns
- Other patterns inconsistent with the file and surrounding codebase

## Guardrails

- Keep behavior unchanged unless fixing a clear bug.
- Prefer minimal, focused edits over broad rewrites.
- Keep the final summary concise (1-3 sentences).

## Harness Integration

- Diff against the repo's default branch if it is not `main`.
- Run after focused verification passes and before the `quality-review`
  completion gate.
- The fixes are mechanical: when the diff spans more than a few files,
  delegate the edits to `fast-worker` with the specific findings to fix.
- Re-run the focused verification after deslopping to confirm behavior is
  unchanged.
