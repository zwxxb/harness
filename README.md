# Review Harness

A multi-round code review loop that runs in any coding agent. The protocol is
markdown (`HARNESS.md`). The exit condition is a stdlib Python script
(`.harness/gate.py`). No vendor models, plugins, or shell scripts.

## The loop

```text
Round N:  HUNT -> TRIAGE -> FIX -> PROVE -> REGRESS -> GATE
          repeat until the gate reports zero open critical/high/medium

First clean gate -> DESLOP + SIMPLIFY -> re-verify -> one full confirmation round
Done:     python3 .harness/gate.py --done   (clean ledger + two round reports)
```

- Findings go into an append-only ledger (`.harness/ledger.md`) with a
  severity: critical, high, medium, low, or info.
- The gate blocks on critical, high, and medium. Severity is never lowered to
  pass the gate; only the user can waive a finding.
- `MAX_ROUNDS = 6` and a stall rule end the loop with an honest report
  instead of looping silently.

## The passes

Each step has a checklist in `.harness/passes/`, adapted from Trail of Bits
skills. If the real skills are installed, agents use them instead.

| Step | Pass file | Adapted from |
|---|---|---|
| HUNT | `review-thermonuclear.md` | Cursor thermo-nuclear review, ToB differential-review |
| TRIAGE | `triage-fp-check.md` | ToB fp-check |
| FIX | `fix-patching-bugs.md` | ToB patching-bugs, implement-patch, variant-analysis |
| PROVE | `prove-post-patch-validation.md` | ToB post-patch-validation, prove-patch |
| REGRESS | `regression-hunt.md` | ToB regression-hunt |
| final | `final-deslop-simplify.md` | Cursor deslop |

## Model tiers

Roles depend on capability, not vendor:

| Tier | Model | Work |
|---|---|---|
| A (deep) | the strongest model available (expensive) | planning, architecture, security and invariant analysis, hard root causes, adjudication |
| B (fast) | the cheapest model that follows instructions reliably | bookkeeping, test scaffolding, pre-decided edits, sweeps, reports |

`HARNESS.md` lists which steps can run in parallel and which must run in
order. It also requires one writer per worktree and fresh-context reviewers.

## Agent compatibility

The installer adds a marked pointer block to three files. Existing content is
kept, and re-installs update the block in place.

| File | Read by |
|---|---|
| `AGENTS.md` | Codex, Cursor, GitHub Copilot, Windsurf, goose, Zed, opencode, Amp, Jules, Factory, Roo Code, Kilo Code, Warp, Devin, Junie, Augment, Prime Agent |
| `CLAUDE.md` | Claude Code |
| `GEMINI.md` | Gemini CLI |

For Aider, run `aider --read AGENTS.md`. For any other agent, tell it once to
read `HARNESS.md`. An agent only needs to read files, edit files, and run
`python3`.

**Prime Agent** finds `AGENTS.md` on its own. To map the tiers, pass a model
to `rlm.spawn(prompt, name=..., model=...)`; `rlm.find_models()` lists the
available models. Trail of Bits skills under `~/.prime/agent/skills/` are
used directly. To run the loop unattended, with the gate as the stop
condition:

```bash
prime-agent --autonomous --autonomous-gate "python3 .harness/gate.py --done" \
  --autonomous-gate-retries 6 --autonomous-max-turns 200 --autonomous-max-tokens 2000000 \
  "Run the HARNESS.md loop for: <task>"
```

The default autonomous limits (12 turns, 80k tokens) are too small for a
multi-round loop. The limits above are example values.

## Install

```bash
git clone https://github.com/zwxxb/harness && cd harness
python3 bin/validate.py                                 # live gate and installer tests
python3 bin/install.py --target ~/projects/your-repo    # --force upgrades changed files, with backups
python3 bin/validate.py --target ~/projects/your-repo   # check an installed repo
```

Then prompt your agent in the repo:

```text
Run the HARNESS.md loop for: <goal, constraints, files, tests>
```

## Code search (optional): zvec-grep

```bash
npm install -g @zvec/zvec-grep --allow-scripts=@zvec/zvec-grep
cd ~/projects/your-repo
zg --index --embedding local/potion-retrieval-32m
zg --install --target <agent> --yes   # codex, claude, cursor, copilot, opencode, vscode, ...
```

Agents without a zvec-grep integration, Prime Agent included, can call the
`zg` CLI directly.

## The gate

```bash
python3 .harness/gate.py          # 0 clean, 1 blocked (lists ids), 2 ledger error
python3 .harness/gate.py --done   # final check: clean ledger + two round reports
python3 .harness/gate.py --json   # counts and blocking ids
python3 .harness/gate.py --init   # recreate a missing ledger
```

Ledger statuses: `open` -> `confirmed` -> `fixed` (needs commit + proof), or
`wontfix` (false positive, with evidence), or `waived` (user decision only).

## Design

- **One protocol.** `HARNESS.md` is the only copy. Each pointer block is a
  few lines, so there is nothing to keep in sync.
- **The gate decides, not the model.** Pass/fail is arithmetic over ledger
  headings. Findings change status but never disappear. Severity changes
  only in triage, with evidence.
- **Evidence over assertion.** Triage proves a finding is real before
  anyone patches it. Proofs compare the baseline with the patch. Reviewers
  start fresh and work from files, not summaries.
- **Cleanup re-enters the loop.** Deslop edits get a full confirmation
  round, and they are reverted if they break behavior.
- **No vendor lock-in.** The harness has no settings files, subagent
  definitions, plugins, or launch scripts. A drift guard in
  `bin/validate.py` keeps them out.

## Layout

```text
bin/install.py        copies the core, adds pointer blocks, creates the ledger
bin/validate.py       live gate tests, installer round trip, drift guard
template/HARNESS.md   the protocol
template/.harness/    gate.py (holds the ledger template) and the six passes
```
