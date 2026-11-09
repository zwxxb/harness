# Pass 2 — TRIAGE: verify every medium+ finding

Adapted from the Trail of Bits fp-check skill. Pattern recognition is not
analysis: before anything gets patched, prove each `open` finding of
severity critical, high, or medium is real. Low/info findings skip triage —
they do not block the gate.

For each open medium+ finding, in order:

1. **Trace, do not pattern-match.** Read the actual code path: where the
   tainted, untrusted, or odd value originates, what it flows through, what
   is at the sink. Cite file:line for every hop.
2. **Test preconditions.** Can the required conditions occur in this program
   as it is actually called — real callers, real config, real inputs? A path
   reachable only in theory is `wontfix` material with that reason.
3. **Demonstrate cheaply when possible.** A snippet, a unit call, a crafted
   input. For security findings this becomes the PoC seed that pass 4 reuses.
4. **Verdict, recorded in the ledger:**
   - TRUE POSITIVE -> `[confirmed]`. If the trace showed the severity was
     misjudged, rescale it now — with the evidence in the record. This is
     the only legitimate rescaling: it happens before patching, on evidence.
   - FALSE POSITIVE -> `[wontfix]` plus one line: what the trace showed.
   - Inconclusive after honest effort -> leave `confirmed` (conservative).
     The fix and prove passes work from evidence; a phantom dies there.

Rationalizations to reject (ToB fp-check):

| Thought | Required action |
|---|---|
| "The pattern looks dangerous" | finish the data-flow trace first |
| "Verify the rest quickly" | every finding gets the full trace |
| "Exploitability is someone else's call" | preconditions are part of the verdict |
| "Already confirmed, why re-check" | triage re-reads the code, not the hunt's summary |

Round report: one line per finding — verdict plus the decisive evidence.
