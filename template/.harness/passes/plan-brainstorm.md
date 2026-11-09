# Before the loop 1 — BRAINSTORM: agree on what to build

Adapted from the obra/superpowers brainstorming skill; if it is installed,
use it instead. You build what you believe the user wants, and that belief
is usually thinner than it feels. Find out what they want, and why, before
anything gets built.

## First: what do you actually know?

- Everything that matters is in the request ("make the icon cornflower
  blue"): do it, say what you did, and go to EXECUTE with a one-line plan.
- Something non-trivial is missing: start the conversation.

## The conversation

- Look before you ask: read what the request points at and the code it
  touches until you can explain how it works today and what the change
  touches. Never ask what the project already answers.
- Ask only when the answer changes what gets built. One question at a
  time, in the user's terms, saying why you ask. Otherwise state your call
  and your reason as a proposal they can correct.
- Until you know why they want it, ask open questions. Once you know why,
  sketch named choices concretely, with trade-offs and your pick.
- Lay out the approaches in a message of their own: two or three real
  alternatives grounded in the codebase, what each trades off, and your
  recommendation. If there is one sensible way, say so and why the others
  don't fit.
- Play back each part as you understand it. Only what they said is
  theirs; everything else is your proposal, with a reason.
- A throwaway spike is fine when it is the cheapest way to learn. It skips
  plan and review; keeping it is a new request.

## The design doc

Size the work in plain words: a small change gets a short doc, a project
the full one. Cover the intent and the why; goals, non-goals, anti-goals;
constraints; approaches (considered, trade-offs, picked, why); the decided
parts of the how; what is left to the builder. Save it to
`docs/superpowers/specs/YYYY-MM-DD-<topic>-design.md` unless the user
prefers another place.

For a project, run a builder check: a fresh Tier A reviewer reads the doc
as the builder who must plan from it. Settle minor questions yourself and
mark them as your calls. Bring the user only the questions that change what
gets built, in one message.

## Gate

Nothing gets built (product code, scaffolding, dependency installs) until
the user approves the design doc. Approval covers only what they saw. If
the user opted out of questions, or the run is unattended, the request is
the approved spec: record every call you made in the design doc as yours,
and continue. Next: `.harness/passes/plan-write.md`.
