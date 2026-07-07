# Claude Coding Harness

A reusable Claude Code harness for serious coding work:

- Fable leads the main session.
- Fable is the native advisor when Fable is the main model.
- Opus is available as `deep-reasoner`.
- Sonnet is available as `fast-worker`.
- Superpowers drives planning: `brainstorming` first, then `writing-plans`.
- GitNexus drives code search: build/check the code graph, then navigate flows,
  symbols, callers/callees, layers, and architecture from the graph.
- Codex is available as an independent peer through the OpenAI Codex Claude Code plugin.

The harness is packaged as a template you can install into any repo.

## Quick Start

Validate the harness itself:

```bash
cd ~/Desktop/harness
python3 bin/validate.py
```

Install into a target repo:

```bash
python3 bin/install.py --target ~/projects/your-repo
```

Start the default Fable-led session from the target repo:

```bash
cd ~/projects/your-repo
./scripts/claude-lead.sh
```

Start a Superpowers planning session:

```bash
./scripts/claude-plan.sh
```

Use the cheaper Sonnet executor + Opus advisor mode:

```bash
./scripts/claude-sonnet-opus.sh
```

## Expected Workflow

The full workflow lives in `template/.claude/skills/lead-orchestrator/SKILL.md`
(installed as `.claude/skills/lead-orchestrator/SKILL.md`). In short: Superpowers
brainstorming -> approved spec -> Superpowers plan -> delegated execution
(`deep-reasoner` for hard reasoning, `fast-worker` for mechanical work, Codex
as an independent peer) -> `deslop` cleanup -> `quality-review` completion
gate. Rationale for each piece is in `docs/ARCHITECTURE.md`.

## Files

- `template/` - files installed into target repositories.
- `bin/install.py` - installer with backup/merge behavior.
- `bin/validate.py` - sanity checks for the harness and optional target repo.
- `docs/USAGE.md` - detailed setup and daily workflow.
- `docs/ARCHITECTURE.md` - how the model/subagent/plugin pieces fit.

## Code Search

GitNexus is the primary code-search layer for installed repos. Build or check
the graph:

```bash
./scripts/gitnexus-graph.sh status
./scripts/gitnexus-graph.sh analyze
```

Resource URIs and query-tool usage live in the lead-orchestrator skill.

## One-Time Plugin Setup

The installer can write the project config, but Claude Code plugins still need to
be installed in Claude Code's plugin store. Run these once if missing:

```bash
claude plugin marketplace add openai/codex-plugin-cc
claude plugin install -s project codex@openai-codex
claude plugin install -s project superpowers@superpowers-dev
```

Then inside Claude Code:

```text
/codex:setup
```

If Codex is not authenticated:

```text
!codex login
/codex:setup
```
