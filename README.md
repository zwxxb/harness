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

## Expected Planning Flow

For substantial work, Claude should follow this sequence:

1. Use `superpowers:brainstorming`.
2. Explore repo context.
3. Ask clarifying questions one at a time.
4. Compare 2-3 approaches and recommend one.
5. Save the approved design/spec under `docs/superpowers/specs/`.
6. Use `superpowers:writing-plans`.
7. Save the implementation plan under `docs/superpowers/plans/`.
8. Execute only after the plan is approved.

## Expected Execution Flow

After the plan is approved:

- Use `deep-reasoner` for hard architecture, debugging, security, and invariant decisions.
- Use `fast-worker` for scoped mechanical edits and verification.
- Use Codex for independent rescue, fresh diagnosis, or adversarial review.
- Use advisor, Codex review, or `code-review-specialist` before finalizing substantial work.

## Files

- `template/` - files installed into target repositories.
- `bin/install.py` - installer with backup/merge behavior.
- `bin/validate.py` - sanity checks for the harness and optional target repo.
- `docs/USAGE.md` - detailed setup and daily workflow.
- `docs/ARCHITECTURE.md` - how the model/subagent/plugin pieces fit.

## Code Search

For broad code search in an installed repo:

```bash
./scripts/gitnexus-graph.sh status
./scripts/gitnexus-graph.sh analyze
```

Then use GitNexus resources/tools from Claude Code:

- `gitnexus://repo/{name}/context`
- `gitnexus://repo/{name}/understand/components`
- `gitnexus://repo/{name}/understand/layers`
- `gitnexus://repo/{name}/understand/tour`
- GitNexus query/context tools for execution flows and symbols

Use `rg` for literal follow-up checks, not as the primary architecture search
tool.

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
