# Review Harness

Plan, build, and review code with any AI coding agent, in rounds, until no
critical, high, or medium finding remains.

The workflow is plain markdown (`HARNESS.md`). Completion is checked by a
standard-library Python script (`.harness/gate.py`). It needs no plugins,
vendor-specific configuration, or shell scripts, so it works with any agent
that can read files, edit files, and run commands.

## Requirements

- Python 3.10 or newer (standard library only)
- Git
- A coding agent with file and shell access

## Quick start

```bash
git clone https://github.com/zwxxb/harness
cd harness
python3 bin/validate.py                         # self-test: gate and installer
python3 bin/install.py --target /path/to/repo   # install into a project
```

Then, in the project, give your agent the task:

```text
Run the HARNESS.md loop for: <goal, constraints, relevant files, how to test>
```

To upgrade an installed project, run the installer again with `--force`;
changed files are backed up as `<file>.bak-<timestamp>`. To check an
installed project, run `python3 bin/validate.py --target /path/to/repo`.

## How it works

```text
Plan       BRAINSTORM -> PLAN -> EXECUTE
Review     HUNT -> TRIAGE -> FIX -> PROVE -> REGRESS -> GATE   (repeat until clean)
Finish     DESLOP + SIMPLIFY -> one full confirmation round -> gate.py --done
```

1. **Plan.** The agent agrees on a design with you, writes a task-by-task
   plan, and implements it with tests first. No product code is written
   before the design is approved.
2. **Review.** Each round hunts for problems, confirms that each finding is
   real, fixes it at the root, proves the fix against the baseline, and
   checks the fix for regressions. Findings are recorded in an append-only
   ledger with a severity.
3. **Finish.** When no critical, high, or medium finding is open, the agent
   removes AI slop, simplifies the code, and runs one more full round. The
   work is done when `gate.py --done` passes.

The loop stops after six rounds, or when two rounds in a row add no new
medium or higher finding while blockers remain. It then reports every unresolved finding instead
of passing. Severity is never lowered to pass the gate; only you can waive a
finding.

## Workflow steps

Each step is a checklist in `.harness/passes/`. If the original skills are
installed in your agent, they are used instead.

| Step | Checklist | Based on |
|---|---|---|
| Brainstorm | `plan-brainstorm.md` | superpowers: brainstorming |
| Plan | `plan-write.md` | superpowers: writing-plans |
| Execute | `execute-plan.md` | superpowers: executing-plans, subagent-driven-development |
| Hunt | `review-thermonuclear.md` | Cursor thermo-nuclear review; Trail of Bits: differential-review |
| Triage | `triage-fp-check.md` | Trail of Bits: fp-check |
| Fix | `fix-patching-bugs.md` | Trail of Bits: patching-bugs, implement-patch, variant-analysis |
| Prove | `prove-post-patch-validation.md` | Trail of Bits: post-patch-validation, prove-patch |
| Regress | `regression-hunt.md` | Trail of Bits: regression-hunt |
| Finish | `final-deslop-simplify.md` | Cursor deslop |

## The gate

| Command | Result |
|---|---|
| `python3 .harness/gate.py` | `0` when no critical, high, or medium finding is open; `1` when one is (the blocking ids are listed); `2` when the ledger is malformed |
| `python3 .harness/gate.py --done` | Also requires two round reports. This is the completion check |
| `python3 .harness/gate.py --json` | Counts and blocking ids as JSON |
| `python3 .harness/gate.py --init` | Creates a missing ledger |

A finding moves from `open` to `confirmed` to `fixed`, and `fixed` needs a
commit and a proof. Otherwise it ends as `wontfix` (a false positive, with
evidence) or `waived` (your decision only). Severity definitions are in
`HARNESS.md`.

## Model tiers

Work is assigned by capability, so any provider's models can be used.

| Tier | Model | Work |
|---|---|---|
| A | The strongest model available | Design, planning, architecture, security and invariant analysis, adjudication |
| B | The cheapest model that follows instructions reliably | Implementing plan tasks, test scaffolding, bookkeeping, sweeps |

`HARNESS.md` also lists which steps can run in parallel and which must run
in order. It requires one writer per worktree and reviewers with fresh
context.

## Agent compatibility

The installer adds a short, marked pointer block to the files that agents
read. Existing content is kept, and re-running the installer updates the
block in place.

| File | Read by |
|---|---|
| `AGENTS.md` | Codex, Cursor, GitHub Copilot, Windsurf, Gemini CLI (when configured), goose, Zed, opencode, Amp, Jules, Factory, Roo Code, Kilo Code, Warp, Devin, Junie, Augment, Prime Agent |
| `CLAUDE.md` | Claude Code |
| `GEMINI.md` | Gemini CLI (default) |

For Aider, run `aider --read AGENTS.md`. Any other agent can be pointed at
`HARNESS.md` directly.

## Unattended runs

Any runner that repeats work until a command succeeds can use
`python3 .harness/gate.py --done` as its completion check. With Prime Agent,
for example:

```bash
prime-agent --autonomous --autonomous-gate "python3 .harness/gate.py --done" \
  --autonomous-max-turns 200 --autonomous-max-tokens 2000000 \
  "Run the HARNESS.md loop for: <task>"
```

A multi-round loop needs much higher turn and token limits than a single
task; the values above are a starting point. When no one is available to
answer questions, the request is treated as the approved spec, and every
decision the agent makes is recorded in the design doc and the plan.

## Optional: semantic code search

[zvec-grep](https://github.com/zvec-ai/zvec-grep) adds search by meaning
alongside exact-match search. The workflow uses it when it is available and
falls back to `rg` otherwise.

```bash
npm install -g @zvec/zvec-grep --allow-scripts=@zvec/zvec-grep
cd /path/to/repo
zg --index --embedding local/potion-retrieval-32m
zg --install --target <agent> --yes   # codex, claude, cursor, copilot, opencode, vscode, ...
```

## Design principles

- **One source of truth.** `HARNESS.md` holds the whole protocol. The
  pointer blocks only reference it.
- **The gate decides.** Completion is computed from the ledger; the model
  does not judge its own work.
- **Evidence over assertion.** Findings are confirmed before they are
  patched. Fixes are proven against the baseline. Reviewers work from
  files, not summaries.
- **Cleanup is reviewed too.** The final cleanup gets a full review round,
  and its edits are reverted if behavior changes.
- **No lock-in.** `bin/validate.py` fails if vendor-specific configuration
  or removed tools reappear.

## Repository layout

```text
bin/install.py        Installs the core, adds the pointer blocks, creates the ledger
bin/validate.py       Self-test: gate behavior, installer round trip, drift guard
template/HARNESS.md   The protocol
template/.harness/    The gate and the nine step checklists
```

## Acknowledgements

The step checklists adapt work from:

- [obra/superpowers](https://github.com/obra/superpowers): brainstorming,
  writing-plans, executing-plans, subagent-driven-development
- [Trail of Bits skills](https://github.com/trailofbits/skills): fp-check,
  patching-bugs, implement-patch, variant-analysis, post-patch-validation,
  prove-patch, differential-review, regression-hunt
- Cursor team kit: deslop and the thermo-nuclear code quality review
