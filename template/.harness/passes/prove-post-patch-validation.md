# Pass 4 — PROVE: validate every fixed finding

Adapted from the Trail of Bits post-patch-validation and prove-patch skills.
The diff, the author, and a passing suite cannot establish correctness. For
each `fixed` record, produce baseline-versus-patched evidence and write it
into the record as the `- proof:` line. If your environment has
post-patch-validation, prove-patch, or validate-bug installed, prefer running
them.

Pin first: the vulnerable base ref and the patch commit. Prove from clean
checkouts (`git worktree`), not the live tree. Never edit the patch during
validation — failures go back to pass 3 as a new attempt.

State the highest honest evidence level and record it:

- `source` — reasoning over code and diff only. Weakest; rarely enough alone.
- `build` — compiled or analyzed, but the reported behavior was not executed.
- `runtime` — the checks below executed the behavior. Required for critical
  and security findings whenever running the project is possible.

Runtime checks (each side = baseline AND patched):

| Check | Expectation |
|---|---|
| control | benign usage of the changed code succeeds on both sides |
| exploit | the original PoC demonstrates the bug on baseline; the safety assertion holds on patched |
| variant | an independent root-cause variant fails on baseline and holds on patched |
| behavior | unaffected behavior byte-identical on both sides |
| regression | targeted checks for the touched area pass on both sides |
| suite | project suite passes on patched; failures attributed against baseline |

Honesty rules — violating one is itself a finding, never a pass:

- A nonzero exit is not a reproduction. Print a marker (for example
  `PPV_REACHED`) and flush it immediately before the assertion; confirm the
  baseline failure is your assertion, not an import error or a crash en route.
- Exploit and variant checks stay side-blind: they assert the safe behavior,
  not "which revision am I on".
- Suite fails on patched, passes on baseline -> regression; back to pass 3.
  Fails on both -> unresolved attribution; report it, do not guess.
- Keep the first pinned result. Fix nondeterminism; do not rerun until green.
- "The PoC no longer fires" is never enough: at least one independent
  root-cause variant must also hold on patched.
- Record the evidence level beside every pass. A source-level claim about
  runtime behavior is a gap; gaps are reported as gaps.

Proof line format:
`- proof: runtime — control/exploit/variant/behavior/regression as above, suite green, commit <sha>`
