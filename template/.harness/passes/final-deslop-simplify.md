# Final pass — DESLOP + SIMPLIFY (once, after the first clean gate)

Adapted from the Cursor team kit deslop skill plus the simplification
ambition of the thermonuclear review. The loop is clean; now make it small.
This pass still edits code, so it re-enters the loop: afterwards re-run the
project verification and one full confirmation round (every HARNESS.md step).
Done = two clean gates, the second one after this pass.

## Deslop (mechanical — always)

On the whole branch diff, remove the slop the work introduced:

- comments that narrate the obvious or contradict local style
- defensive checks or try/catch on paths that cannot fail in this codebase
- casts (`any`, `as unknown`, `@SuppressWarnings`, `# type: ignore`) used
  only to silence the checker
- deep nesting that collapses with early returns
- dead flags, unused parameters, speculative generality, near-duplicate copies
- anything inconsistent with the file's surrounding style

## Simplify (ambitious — where a clear path exists)

Prefer the version a reader can hold in their head:

- delete a layer of indirection rather than polishing it
- reframe the state model so conditionals disappear
- collapse special cases into the default flow
- reuse the canonical helper instead of a near-duplicate
- make the type boundary explicit so the control flow simplifies

Restructure only with a clear path to meaningfully simpler. Otherwise leave
it and record the idea as `info` in the ledger for the user.

## Guardrails

- Behavior unchanged. If verification fails after deslopping, revert the
  deslop edits — slop removal is never worth a regression.
- Minimal, focused edits; no drive-by rewrites of untouched code.
- Then: project verification -> confirmation round. The confirmation round
  may add findings; the loop continues until it is clean.
