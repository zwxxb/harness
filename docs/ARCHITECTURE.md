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

deslop
  post-implementation cleanup skill; strips AI slop from the branch diff

quality-review
  strict maintainability review; the standard completion gate
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

The concrete search order and resource URIs live in the lead-orchestrator
skill, which is installed into every target repo.

## Why Deslop And Quality-Review Are Separate Gates

`deslop` (ported from Cursor's team kit) is a mechanical pass: strip
AI-generated slop from the branch diff without changing behavior. It runs
after focused verification so cleanup cannot mask a regression.

`quality-review` (ported from Cursor's thermo-nuclear-code-quality-review) is
a structural gate: abstraction quality, file-size growth, spaghetti
conditionals, boundary hygiene. It runs last because it judges the final shape
of the change. Keeping the two separate keeps deslop cheap enough to run
always and the review strict enough to block.
