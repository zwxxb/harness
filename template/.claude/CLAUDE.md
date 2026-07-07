# Claude Coding Harness

Default posture: the main Claude thread is the Fable lead. Plan, decompose,
synthesize, and keep the main context lean. For non-trivial work, run the
`lead-orchestrator` skill — it owns the detailed workflow.

## Planning

For broad features, behavior changes, architecture, or complex debugging:
`superpowers:brainstorming` first (approved design spec in
`docs/superpowers/specs/`), then `superpowers:writing-plans` (implementation
plan in `docs/superpowers/plans/`). Execute only after the plan is approved.
Native `/plan` is not the primary planning workflow.

## Code Search

GitNexus is the primary layer for broad or semantic exploration —
architecture, flow tracing, impact analysis, unfamiliar code. The SessionStart
hook reports graph status; build or refresh with
`./scripts/gitnexus-graph.sh analyze` (in the background) when missing or
stale. Use `rg` for literal strings and exact filenames, or while the graph is
building — not as the primary architecture search tool.

## Delegation

- Hard reasoning (architecture, complex debugging, algorithms,
  security-sensitive decisions, invariants, high-stakes tradeoffs) ->
  `deep-reasoner` (Opus).
- Mechanical work (scoped edits, boilerplate, test scaffolding, formatting,
  simple refactors) -> `fast-worker` (Sonnet), only after the approach is
  decided.
- Fresh perspective, rescue, or adversarial review -> Codex
  (`codex:rescue --background` and related commands), an independent peer
  from another model family. For high-stakes questions, ask Codex and
  `deep-reasoner` in parallel without showing either the other's answer, then
  synthesize.
- Fable advisor is the native advisor (the only valid advisor for a Fable
  main model). Consult it at hard decision points.

## Finishing

- After implementation passes focused verification, run `deslop` on the
  branch diff.
- Gate substantial work with `quality-review` before declaring completion.
  Stack `deep-reasoner` + Codex review only for security, funds,
  data-integrity, migration, or invariant decisions.

## Execution Discipline

- Read relevant files before editing them.
- Prefer existing patterns and helper APIs.
- Keep edits scoped.
- Run focused verification before broad verification.
- Report actual command results, not guesses.
