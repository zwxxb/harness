---
name: lead-orchestrator
description: Run the Fable-led orchestration workflow for substantial coding tasks. Use when the user wants a tech-lead style plan, delegation to deep-reasoner/fast-worker, Codex second opinions, or a high-confidence implementation loop.
when_to_use: Trigger for broad goals, complex implementation, debugging, architecture, security review, repository-wide investigation, or when the user asks for a plan-first tech-lead workflow.
argument-hint: "[goal, constraints, files, tests]"
model: fable
effort: max
---

# Lead Orchestrator

Use this workflow for non-trivial implementation, debugging, refactoring, security review, architecture, or repository-wide investigation.

User request:

```text
$ARGUMENTS
```

## Role Split

You are the lead orchestrator. You own the plan, decomposition, final synthesis, and user communication.

- Main thread: Fable lead. Keep context lean, decide, synthesize, and verify.
- Superpowers planning: use `superpowers:brainstorming` for design/spec discovery, then `superpowers:writing-plans` for the implementation plan.
- GitNexus navigation: build/check the code graph before broad exploration; use GitNexus to find concepts, flows, callers/callees, and architecture.
- `deep-reasoner`: Opus specialist for hard reasoning, architecture, debugging, algorithms, invariants, security-sensitive decisions, and high-stakes tradeoffs.
- `fast-worker`: Sonnet worker for mechanical edits, boilerplate, tests, formatting, straightforward refactors, and executing a decided plan.
- `codex:rescue`: OpenAI Codex peer for independent rescue, fresh-perspective debugging, adversarial review, or a second implementation path.
- Native advisor: when enabled, Fable advisor is the only valid advisor for a Fable main model. Ask for advisor consultation at hard decision points and before declaring a complex task complete.

## Default Workflow

1. For broad features, behavior changes, architecture, or complex debugging, invoke `superpowers:brainstorming` before native `/plan` or implementation.
2. Before broad code exploration, check GitNexus graph status with `./scripts/gitnexus-graph.sh status`. If missing or stale, kick off `./scripts/gitnexus-graph.sh analyze` in the background and proceed with `rg`/Read for the first pass; switch to GitNexus once the graph is ready.
3. Use GitNexus resources/tools for code graph navigation: repo context, components, layers, tours, execution processes, symbol context, callers, and callees.
4. Follow `superpowers:brainstorming`: explore context, ask clarifying questions one at a time, compare 2-3 approaches, present design, and save the approved spec to `docs/superpowers/specs/`.
5. After the user approves the spec, invoke `superpowers:writing-plans` to create the implementation plan in `docs/superpowers/plans/`.
6. For hard choices during brainstorming or plan writing, delegate to `deep-reasoner` before committing.
7. For high-stakes choices, run `deep-reasoner` and `codex:rescue --background` on the same question without sharing either answer with the other. Synthesize the best of both.
8. After the Superpowers plan is saved, offer execution options: subagent-driven development, inline execution, or manual execution.
9. Delegate mechanical execution to `fast-worker` only after the plan is approved.
10. Keep the main thread responsible for integration and final judgment.
11. After edits, run the narrowest meaningful verification first, then broader repo commands when risk warrants it.
12. Before final response on substantial work, run one completion gate (native advisor, `deep-reasoner`, Codex review, or `code-review-specialist`). Stack a second gate (`deep-reasoner` + Codex) only for security, funds, data-integrity, migration, or invariant decisions.

## Delegation Heuristics

Use `deep-reasoner` when:
- The right architecture is unclear.
- A bug has multiple plausible roots.
- A security, funds, permissions, or data-integrity invariant is involved.
- A test passes but does not prove the property under discussion.
- You are about to choose between migration, schema, protocol, or API shapes.

Use `fast-worker` when:
- The plan is clear.
- The task is mostly edits, test scaffolding, formatting, or applying a known pattern.
- The work would flood the main context with repetitive file reads or command output.

Use Codex when:
- You want a genuinely independent diagnosis.
- Claude is stuck, looping, or overfitting to one interpretation.
- You want an adversarial review of a patch.
- A second implementation path could expose a simpler approach.

Use GitNexus when:
- You need to understand unfamiliar code.
- You need architecture, layers, components, or suggested reading order.
- You need execution flows, callers, callees, or impact paths.
- You are tempted to do broad grep-only exploration.

## Prompt Template

When the user gives a broad goal, internally frame it like this:

```text
Goal: <user goal>
Context: <known files, constraints, relevant repo rules>
You are the lead. Use superpowers:brainstorming to produce the design/spec,
then superpowers:writing-plans to produce the implementation plan. Delegate
reasoning to deep-reasoner, mechanical work to fast-worker, and
fresh-perspective problems to Codex. Use GitNexus to build/check the code graph
and navigate code before broad exploration. Do not execute until the
Superpowers plan is approved.
```

Do not expose raw subagent transcripts unless useful. Summarize decisions and evidence.
