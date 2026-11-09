# Pass 1 — HUNT: thermonuclear review

One full review round over the branch diff (diff against the base branch).
Append every finding to `.harness/ledger.md` as `open` with a HARNESS.md
severity, file:line, evidence, and one-line impact. "No findings" is valid
only after a real hunt — the round report says what was covered.

Adapted from the Cursor team kit "thermo-nuclear-code-quality-review" and the
Trail of Bits differential-review skill. If your environment has ToB skills
installed (differential-review, semgrep, codeql), run them too and fold their
results into the ledger.

## Lens A — structural quality (be ambitious)

Hunt for the reorganization that makes whole branches, helpers, modes, or
layers disappear while behavior stays identical. Assume a "code judo" move
often exists: a reframing that uses the existing architecture so the change
becomes dramatically simpler. Do not stop at "this could be cleaner".

Presumptive blockers (severity high unless clearly justified in the diff):

- a file pushed from under 1k lines to over 1k lines
- ad-hoc conditionals or one-off branches bolted into existing flows
- feature logic leaking into shared paths; details leaking through APIs
- thin wrappers, identity abstractions, pass-through helpers
- casts / `any` / `unknown` / needless optionality hiding the real contract
- copy-pasted logic where a canonical helper already exists
- a refactor that moves complexity around instead of deleting it
- sequential orchestration where independent work could be parallel and simpler
- partial updates leaving state less atomic than it should be

Also flag (severity medium unless clearly worse): repeated conditionals
signaling a missing model or helper; generic "magic" handling hiding simple
data shapes; narrow edge-case handling in the middle of a busy function;
"temporary" branching that will become permanent debt.

## Lens B — correctness and security

- Trace the changed control and data flows end to end; name the invariant
  each change relies on.
- Boundary and error paths: untrusted input, empty/none, partial failure,
  teardown, concurrency.
- Auth, permissions, funds, secrets: a new or moved trust boundary is at
  least medium until proven fine; exploitable or invariant-breaking is
  critical.
- Regression watch: if history shows a similar fix nearby, verify this change
  does not undo it.
- If a plan exists, check its review focus and global constraints against
  the diff; an untested review-focus item is a finding.
- Missing tests on modified behavior: medium. A test that passes but does not
  prove the property under discussion: medium.

## Lens C — differential (the diff is the suspect)

- Risk first: auth, crypto, value transfer, external calls, migrations.
  Classify by risk, not by line count — Heartbleed was 2 lines.
- Blast radius: count callers of changed functions; follow transitive
  callers one level.
- Coverage: list modified behavior with no test touching it.

## Output

Ledger records, then `.harness/rounds/round-NN.md` with what was reviewed,
findings added with severities, and honest coverage gaps. Prioritize:
structural regressions > missed simplification > spaghetti growth >
boundary/type problems > size > nits. Few high-conviction findings beat a
pile of nits.
