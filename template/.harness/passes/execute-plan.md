# Before the loop 3 — EXECUTE: implement the plan task by task

Adapted from the obra/superpowers executing-plans and
subagent-driven-development skills; if they are installed, use them
instead. The plan already did the thinking: execute it exactly, prove each
step with a test you watched fail and then pass, and leave a record.

Work on a feature branch or worktree. For each task, in order:

- **Subagent-driven** (your harness can spawn agents): a fresh Tier B
  implementer (the plan carries the design) gets only its task, the global
  constraints, and the interfaces it consumes. It implements with TDD,
  commits, and self-reviews. A fresh Tier A reviewer then checks spec
  compliance and code quality. Fix and re-review until approved. Never two
  implementers on one tree.
- **Inline** (no subagents, or the user chose it): work the steps yourself
  in order, run every verification and read its output, commit per task.

For both:

- Run continuously; do not stop between tasks to ask whether to continue.
- Rulings, not stalls: decide conflicts, ambiguities, and plan defects
  yourself. The spec binds, the plan argues for it, your judgment settles
  the rest. Record each in the plan file as
  `Ruling: <decision> — <why> — <cost if wrong>`.
- Stop and ask only for an irreversible or destructive operation, a
  security-sensitive action, a side effect outside the worktree (merge,
  push to a shared branch, publish), or a plan so broken that every path
  is a guess.
- Output that does not match the plan's expected result is a failure to
  diagnose, never a step to skip.

When every task is done and the suite passes, the whole-branch review is
the HARNESS.md loop: start round 1 with the HUNT pass.
