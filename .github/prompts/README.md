# GitHub Copilot Prompt Files

Reusable prompt files for structured development workflows with GitHub Copilot (and compatible LLM assistants). These files live here because VS Code reads `.github/prompts/` as the workspace prompt library.

## Configuration

Each prompt file has a `## Config` section at the top. Fill these in once when you set up the repo — the prompts reference them throughout.

## Available Prompts

### `init-project.prompt.md`
Run once, right after cloning this template into a fresh repo. Runs a requirements-gathering interview, scaffolds only the folders the project actually needs, fills in `CLAUDE.md`, and writes `docs/foundation.md`.

### `session-start.prompt.md`
Initialize a coding session with full context sync. Run this at the start of each session to ground the LLM in git history, project standards, and the last session snapshot.

### `branch-workflow.prompt.md`
Interactive branch creation with context-aware starter prompts. Run when starting any new unit of work.

### `troubleshoot.prompt.md`
Structured debugging workflow — Observe, Theorize, Act. Run when something is broken and the cause isn't obvious.

### `create-commit.prompt.md`
Semantic commit message generator. Analyzes staged changes and session context to write a Conventional Commits message.

## How to use

1. Open Copilot Chat in VS Code
2. Attach the prompt file
3. Type the usage command shown in each prompt
4. Follow the gated workflow

## Adding new prompts

Naming convention: `{purpose}.prompt.md`

Include at the top:
- `description:` one line explaining what it does
- `## Config` section with project-specific values to fill in
