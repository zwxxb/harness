# Harness Usage

## Install Into A Repo

```bash
cd ~/Desktop/harness
python3 bin/install.py --target ~/projects/your-repo
```

Use `--force` to overwrite changed files after backing them up.

## Validate

Validate the harness package:

```bash
python3 bin/validate.py
```

Validate a target repo after installation:

```bash
python3 bin/validate.py --target ~/projects/your-repo
```

## Launch

Default Fable-led mode:

```bash
./scripts/claude-lead.sh
```

Superpowers planning mode:

```bash
./scripts/claude-plan.sh
```

Cheaper Sonnet executor + Opus advisor mode:

```bash
./scripts/claude-sonnet-opus.sh
```

## Code Search With GitNexus

Before broad code exploration, build or refresh the GitNexus graph:

```bash
./scripts/gitnexus-graph.sh status
./scripts/gitnexus-graph.sh analyze
```

Once indexed, use GitNexus resources/tools to navigate:

```text
gitnexus://repos
gitnexus://repo/{name}/context
gitnexus://repo/{name}/understand/components
gitnexus://repo/{name}/understand/layers
gitnexus://repo/{name}/understand/tour
gitnexus://repo/{name}/process/{name}
```

Use GitNexus query/context tools for concepts, execution flows, symbols,
callers, and callees. Use `rg` only for literal follow-up checks or when
GitNexus is unavailable.

## First Prompt

```text
Goal: <what I want>
Context: <files, constraints, existing behavior, test expectations>
Use /lead-orchestrator. You are the lead. For planning, use
superpowers:brainstorming first, then superpowers:writing-plans. Delegate hard
reasoning to deep-reasoner, mechanical work to fast-worker, and
fresh-perspective problems to Codex. Use GitNexus to build/check the code graph
and navigate code before broad exploration. Do not execute until the
Superpowers plan is saved and approved.
```

## Codex Setup

Run once if needed:

```bash
claude plugin marketplace add openai/codex-plugin-cc
claude plugin install -s project codex@openai-codex
claude plugin install -s project superpowers@superpowers-dev
```

Inside Claude Code:

```text
/codex:setup
```

If prompted:

```text
!codex login
/codex:setup
```
