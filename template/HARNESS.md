# HARNESS.md — Multi-Round Review Protocol

Agent-agnostic quality and security loop for substantial work in this repo.
Any coding agent that can read files, edit files, and run `python3` can
execute it. This file is the law. The checklists in `.harness/passes/` carry
the detail. `.harness/gate.py` is the mechanical exit condition.

One-time setup, only if `.harness/ledger.md` is missing:

    python3 .harness/gate.py --init

## Scope

Run the loop for: features, refactors, bug fixes, security changes,
migrations — any diff touching behavior or invariants.

Skip it for: typo fixes, comment-only edits, generated files, formatting.

## Ground rules

1. Plan before editing: write down the approach, the invariants it touches,
   and how you will verify it. Ask the user when requirements are ambiguous.
2. Branch discipline: never work on the default branch. The gates diff the
   branch against its base.
3. Verify through the project's own documented commands (its normal build and
   test interface), narrowest check first. Do not import the project into a
   foreign runtime to test it.
4. The ledger `.harness/ledger.md` is append-only: add records, flip statuses,
   never delete or renumber.
5. Severity is never downgraded to pass the gate. Only the user may waive a
   finding (status `waived`, with a reason in the record).
6. Every `fixed` needs proof. No proof, no `fixed`.

## Severity scale

| Severity | Meaning |
|---|---|
| critical | exploitable hole; broken security, funds, or data invariant; main-path behavior broken |
| high | realistic-input bug; security weakness with plausible preconditions; structural regression a strict review blocks (unjustified >1k-line file growth, spaghetti growth in existing flows) |
| medium | edge-input bug; boundary or layer leak; missing test on modified code; unhandled error path; wrapper obscuring the real design |
| low | slop: noise comments, needless defensiveness, checker-silencing casts; style drift; minor smells |
| info | notes, observations, follow-up ideas |

The gate blocks on critical, high, and medium. Low and info stay recorded.

## The loop

Run from the repo root. Round N (N = 1, 2, ...):

| Step | Pass | Ledger effect |
|---|---|---|
| 1 HUNT | `.harness/passes/review-thermonuclear.md` | append findings as `open` |
| 2 TRIAGE | `.harness/passes/triage-fp-check.md` | every `open` medium+ becomes `confirmed` or `wontfix` |
| 3 FIX | `.harness/passes/fix-patching-bugs.md` | `confirmed` becomes `fixed` (invariant patch, test, variant sweep, commit) |
| 4 PROVE | `.harness/passes/prove-post-patch-validation.md` | evidence recorded on each `fixed` |
| 5 REGRESS | `.harness/passes/regression-hunt.md` | patch-caused regressions become new findings; exclusions and gaps go in the round report |
| 6 GATE | `python3 .harness/gate.py` | exit 0 required to leave the round |

Gate exit 1 -> next round, working from the ledger's live findings.
Gate exit 2 -> repair the ledger syntax first, then continue.

## Multi-agent orchestration

Tier by capability, never by vendor. Map the tiers to whatever models your
harness actually has:

| Tier | Model class | Owns |
|---|---|---|
| **A — deep** | the strongest, smartest model available (expensive) | architecture and schema/protocol choices; security and invariant analysis; root-cause analysis on confusing bugs; structural analysis of large diffs in HUNT; adversarial review of fixes; adjudication and tie-breaks |
| **B — fast** | the cheapest model that can follow instructions reliably (cheap) | mechanical ledger bookkeeping, test scaffolding, applying pre-decided edits, sweeps and searches, formatting, report assembly, command running |

Rules that hold whether or not your harness supports subagents:

- If it supports model-per-subagent (a model setting per agent, or a model
  argument when spawning one): run Tier A and Tier B as parallel workers
  with tier-appropriate models. If it does not: do Tier A work
  yourself at full effort and keep Tier B strictly mechanical.
- Never burn Tier A on mechanical work. Never let Tier B make design or
  severity decisions.
- Parallel-safe: TRIAGE across independent findings, the three HUNT lenses,
  the variant sweep alongside the suite run, REGRESS candidate demonstrations.
- Strictly serial: FIX (one writer per finding), PROVE after its FIX, GATE
  always last, everything against the same working tree.
- One writer per worktree; parallel implementation requires separate
  worktrees.
- Reviewers start fresh: the agent proving or replaying a fix must not read
  the fixer's transcript — judge the evidence, not the narrative.
- Fan-in is files: workers return ledger records and round-report material,
  not summaries to trust.

## Convergence

MAX_ROUNDS = 6 (edit this line to change the limit).

1. Rounds repeat until the gate exits 0.
2. First clean gate -> run `.harness/passes/final-deslop-simplify.md`
   (deslop + simplification), then re-run the project verification.
3. Deslop edits are still edits: run one more full round (all steps).
   The work is done only when that confirmation round is also clean;
   `python3 .harness/gate.py --done` checks this (clean ledger and at least
   two round reports).

Hard stops — write `.harness/rounds/final-report.md`, list every unresolved
finding with its severity, and stop:

- MAX_ROUNDS rounds without a clean confirmation round.
- Stall: two consecutive rounds add zero new medium+ findings while blockers
  remain open.

Stopping is reporting, not passing. Never flip blocking findings to
`wontfix` or `waived` yourself to force exit 0; escalate to the user.

## Round reports

Write `.harness/rounds/round-NN.md` for each round: findings added and
closed, fixes with commit ids, evidence level reached, and what was not
covered. Honest coverage gaps are required content, not optional.

## Code search

When wording or location is unknown, or a question spans files, use
zvec-grep for discovery: the `zvec_grep_search` tool when your agent has it
connected, otherwise the `zg` CLI. Use rg for exact identifiers, filenames,
and regex. Without zvec-grep, rg alone is fine.

## Installed skills

If your environment has any Trail of Bits skills installed (fp-check,
patching-bugs, post-patch-validation, prove-patch, validate-bug,
differential-review, variant-analysis, regression-hunt, semgrep, codeql), prefer invoking them
for the matching pass. The pass files embed their contracts so the loop also
works without them.
