# GitHub Copilot Prompt Files

Reusable prompt files for structured development workflows with GitHub Copilot (and compatible LLM assistants). These files live here because VS Code reads `.github/prompts/` as the workspace prompt library.

Most of this template's workflows are now **skills** in `.claude/skills/`, not prompt files. Skills load themselves when the work matches their description, so they need no attaching. What remains here are the two workflows that are still prompt files.

## Configuration

Each prompt file has a `## Config` section at the top. Fill these in once when you set up the repo — the prompts reference them throughout. The `init-project` skill fills them in as part of scaffolding.

## Available prompts

### `branch-workflow.prompt.md`
Interactive branch creation with context-aware starter prompts. Run when starting any new unit of work.

### `sync-template.prompt.md`
Checks for drift between this repo's folder structure, READMEs, and tooling. Run after any structural change.

## Workflows that are skills, not prompts

These were prompt files in earlier versions of the template. If a doc still points you at a `.prompt.md` file for one of them, that reference is stale — the skill is the current workflow.

| Was | Now |
|---|---|
| `init-project.prompt.md` | The `init-project` skill — one-time setup interview and scaffolding <!-- inherited-docs-ok --> |
| `session-start.prompt.md` | The `session-manager` skill, `/session-start` mode <!-- inherited-docs-ok --> |
| `create-commit.prompt.md` | The `session-manager` skill, `/commit-msg` mode <!-- inherited-docs-ok --> |

The template also ships `docs-updater`, `dependabot`, and `sync-from-template` skills, which never had prompt-file equivalents. See [`.claude/skills/README.md`](../../.claude/skills/README.md) for the full set and for what belongs there.

`troubleshoot.prompt.md` was removed without a replacement in this repo. If you want a structured debugging workflow, add one as a skill. <!-- inherited-docs-ok -->

## How to use a prompt file

1. Open Copilot Chat in VS Code
2. Attach the prompt file
3. Type the usage command shown in each prompt
4. Follow the gated workflow

## Adding new prompts

Prefer a skill in `.claude/skills/` for new workflows — it loads on its own, and works outside VS Code. Add a prompt file here only when you specifically need Copilot's attach-a-file behavior.

Naming convention: `{purpose}.prompt.md`

Include at the top:
- `description:` one line explaining what it does
- `## Config` section with project-specific values to fill in
