# Claude Coding Harness

Default posture: the main Claude thread is the Fable lead. Plan, decompose,
synthesize, and keep the main context lean.

## Planning

Use Superpowers as the primary planning workflow:

1. Invoke `superpowers:brainstorming` before native `/plan` or implementation
   for broad features, behavior changes, architecture, and complex debugging.
2. Use it to explore context, ask clarifying questions, compare approaches, and
   write an approved design spec in `docs/superpowers/specs/`.
3. After the spec is approved, invoke `superpowers:writing-plans` to write the
   implementation plan in `docs/superpowers/plans/`.
4. Only execute after the Superpowers plan is saved and the user chooses the
   execution path.

## Code Search And Navigation

Use GitNexus as the primary code-search and navigation layer for broad or
semantic exploration.

Before broad code exploration:

1. Check whether the repo has a GitNexus graph:
   `./scripts/gitnexus-graph.sh status`
2. If missing or stale, start `./scripts/gitnexus-graph.sh analyze` in the
   background and continue with `rg`/Read for the first exploration pass.
   Switch to GitNexus queries once the graph is ready.
3. Use GitNexus resources and tools to navigate:
   - `gitnexus://repos`
   - `gitnexus://repo/{name}/context`
   - `gitnexus://repo/{name}/understand/components`
   - `gitnexus://repo/{name}/understand/layers`
   - `gitnexus://repo/{name}/understand/tour`
   - `gitnexus://repo/{name}/process/{name}`
   - GitNexus query/context tools for concepts, flows, callers, callees, and symbols.

Use `rg` after GitNexus for literal string checks, exact filenames, or when
GitNexus is unavailable. Do not rely on ad hoc grep-only exploration for
architecture, flow tracing, impact analysis, or unfamiliar code paths.

## Delegation

- Reasoning-heavy phases -> `deep-reasoner` (Opus). Use for architecture,
  complex debugging, algorithm design, security-sensitive decisions, invariant
  analysis, and high-stakes tradeoffs.
- Mechanical work -> `fast-worker` (Sonnet). Use for straightforward edits,
  boilerplate, test scaffolding, formatting, and simple refactors after the
  plan is clear.
- Fresh perspective -> `codex:rescue --background` or related Codex commands.
  Treat Codex as a peer engineer from a different model family, not as a
  passive reviewer.
- Completion checks -> native advisor, `deep-reasoner`, Codex review, or
  `code-review-specialist` depending on task risk.

For high-stakes decisions, ask `deep-reasoner` and Codex the same question in
parallel without showing either one the other's answer. Synthesize the strongest
argument and state the tie-breaker evidence.

When running with Fable as the main model, use Fable as the native advisor.
Claude Code does not allow Opus or Sonnet to advise Fable. Opus remains
available through `deep-reasoner`.

## Execution Discipline

- Read relevant files before editing them.
- Prefer existing patterns and helper APIs.
- Keep edits scoped.
- Run focused verification before broad verification.
- Report actual command results, not guesses.
