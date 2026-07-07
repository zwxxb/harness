# Harness Architecture

## Model Routing

```text
Fable main thread
  owns planning, orchestration, synthesis, final judgment

Fable native advisor
  server-side second opinion at hard decision points

deep-reasoner
  Opus subagent for architecture, debugging, invariants, and tradeoffs

fast-worker
  Sonnet subagent for scoped implementation and verification

Codex
  independent peer from another model family

Superpowers
  process skills for brainstorming, writing plans, and executing plans

GitNexus
  code graph for architecture, semantic search, execution flows, symbols,
  callers, callees, and impact navigation
```

## Why Fable Advisor With Fable Main

Claude Code requires the advisor to be at least as capable as the main model.
With Fable as the main model, Fable is the valid native advisor. Opus still
plays a major role as `deep-reasoner`.

## Why Superpowers Owns Planning

Native `/plan` is useful, but it tends to produce a plan directly. Superpowers
adds two stronger gates:

1. `superpowers:brainstorming` produces an approved design/spec.
2. `superpowers:writing-plans` turns the approved spec into an executable plan.

This prevents the main thread from jumping into implementation with vague
requirements.

## Why Codex Is A Peer

Codex should receive independent prompts. For high-stakes decisions, do not show
Codex the Opus answer or show Opus the Codex answer first. Ask both, then
synthesize.

## Why GitNexus Owns Code Search

`rg` is excellent for literal strings, but it does not know the code graph.
GitNexus builds the repository graph and exposes architecture resources,
execution processes, symbol context, callers, and callees. That makes it the
right first stop for unfamiliar code, flow tracing, architecture, refactoring,
and impact analysis.

Expected search order:

1. Check graph status with `./scripts/gitnexus-graph.sh status`.
2. Build or refresh with `./scripts/gitnexus-graph.sh analyze` when missing or stale.
3. Read `gitnexus://repo/{name}/context`.
4. Use `understand/components`, `understand/layers`, and `understand/tour` for architecture.
5. Use GitNexus query/context tools for concepts, flows, symbols, callers, and callees.
6. Use `rg` for literal checks and exact file/string follow-up.
