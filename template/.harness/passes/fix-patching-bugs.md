# Pass 3 — FIX: patch each confirmed finding

Adapted from the Trail of Bits patching-bugs, implement-patch, and
variant-analysis skills. One confirmed finding at a time. Stay inside the
finding's scope: log unrelated bugs you notice as new findings instead of
fixing them mid-flight.

For each `confirmed` finding:

1. **Record the invariant.** One sentence naming the property that must hold
   ("uploads stay inside the upload directory"). The fix restores the
   invariant; it does not swat the symptom.
2. **Reproduce on the baseline first.** Write the smallest command or snippet
   showing the broken behavior on unpatched code, and observe it fail. If it
   does not reproduce through trustworthy steps, triage was wrong: flip the
   record to `wontfix` with that evidence and move on.
3. **Pin the regression test.** A test that fails on the baseline for the
   named bug. Run it; observe the failure; keep it.
4. **Patch minimally.** The smallest reviewable change that restores the
   invariant. Then run the variant sweep: search the invariant's boundary for
   every other instance of the same root cause — sibling call sites, the same
   pattern family, adjacent error and teardown paths — and fix those in the
   same change. Each variant is its own ledger record, retired together with
   the root.
5. **Verify.** Regression test passes; the project's own suite passes;
   compare before/after failures and explain any pre-existing ones from
   evidence. One local commit (one per root cause if variants came from
   distinct sites).
6. **Record.** Flip to `fixed`; add `- commit: <sha>` and
   `- proof: pending (pass 4)`.

Limits: three patch attempts per finding. Still failing -> stop, report the
attempts honestly in the round report, leave the record `confirmed`, escalate
to the user. Blockers (missing tools, unrelated broken build) -> stop and
report; do not improvise around them.

Rationalizations to reject: "the patcher already tested it" (pass 4 exists
for exactly that); "fix it in the caller just this once" (restore the
invariant, not the symptom); "skip the baseline failure" (an unobserved
reproduction is an unproven reproduction).
