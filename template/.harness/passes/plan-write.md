# Before the loop 2 — PLAN: write the implementation plan

Adapted from the obra/superpowers writing-plans skill; if it is installed,
use it instead. Write for an engineer who has seen neither this codebase
nor the spec. They write idiomatic code once they know the exact interface
and test; what they cannot know is what you decided. Document those
decisions as bite-sized tasks. DRY, YAGNI, TDD, frequent commits.

Save to `docs/superpowers/plans/YYYY-MM-DD-<feature>.md`.

## Header

- Goal (one sentence), architecture (two or three sentences), tech stack,
  and the path to the design doc.
- Global constraints: the spec's project-wide requirements, exact values
  copied verbatim, one per line.
- Review focus: the five inputs or failure modes the spec implies but no
  task's tests would exercise, most likely first, each with the expected
  behavior. Add each one's test to the task that owns the code. The HUNT
  pass checks this list.

## Tasks

- Map files first: what is created or modified, one responsibility each.
  Follow existing patterns.
- A task is the smallest unit with its own test cycle that a reviewer
  could reject while approving its neighbor. Each task lists its files
  (create, modify with line ranges, test), its interfaces (consumes and
  produces, exact signatures), and checkbox steps.
- A step is one action with a checkable result: write the failing test
  (name and assertions, with the spec's values), run it and see it fail
  (command and expected failure), implement the exact signature, run it
  and see it pass, commit.
- A plan holds the decisions the implementer cannot make alone. No "TBD",
  "handle edge cases", or "add validation"; no function bodies that the
  signature and test already determine.

## Self-review

Fix inline: every spec requirement maps to a task; every step is
unambiguous and none is a transcript of the code; names and types match
across tasks; every review-focus item has a test; the plan is not several
times longer than the spec.

## Handoff

Ask the user to review the plan and choose execution: subagent-driven (a
fresh implementer and reviewer per task; thorough) or inline (you
implement, one review at the end; cheaper). Unattended: subagent-driven if
your harness can spawn agents, else inline; record the choice in the plan.
Next: `.harness/passes/execute-plan.md`.
