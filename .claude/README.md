# .claude

Claude Code configuration that travels with the repo. Every project cloned from this template inherits this folder, so anything added here is a standing cost on projects that may have nothing to do with it.

```
.claude/
├── commands/     slash commands — workflows you invoke by name
└── skills/       skills — workflows Claude starts when it recognizes the situation
```

## Choosing between a command and a skill

Both hold instructions for a repeatable workflow. The difference is **who decides it runs**, and getting it wrong is what produced the mess this layout replaced.

| | Skill | Command |
|---|---|---|
| Starts when | Claude recognizes the situation from your description of the work | You type `/name` |
| You must remember it exists | No | Yes |
| Triggering is | Fuzzy — competes with every other skill whose description overlaps | Exact — no ambiguity possible |
| Best for | Work you would want done even if you forgot the workflow existed | Work with a moment you choose to begin it |

**Write a skill** when the right moment is one Claude can spot and you might miss: docs going stale after a session, a pile of Dependabot PRs, a fresh clone that has never been initialized. The value is that it fires without being summoned.

**Write a command** when *you* pick the moment: starting a session, closing one out, cutting a branch, running an audit. Being summoned is the point — a command that fired on its own would be an interruption.

The test that settles most cases: *if the user never learned this existed, should it still run?* Yes means skill. No means command.

### Signs you chose wrong

- **A skill with a mode table.** If a skill routes `/this` and `/that` to different sections, it is several commands wearing one skill's clothing. Split it. The dispatcher exists only because skills cannot be invoked by name.
- **A skill that duplicates one from a marketplace.** Two descriptions competing for the same phrases resolve unpredictably. If the workflow has a moment you choose, a command sidesteps the collision entirely, because explicit invocation never competes.
- **A command nobody remembers to run.** If work keeps getting missed because a command went untyped, the moment is recognizable rather than chosen — it wanted to be a skill.

## What belongs here at all

Beyond picking the right mechanism, both share the bar in [`skills/README.md`](skills/README.md): it must be about building software rather than one person's environment, must work on a fresh clone, and must not duplicate something a marketplace already provides. A workflow that fails those does not become acceptable by being a command instead of a skill.

## Configuration values

Commands and skills that need project-specific values — test command, source root, where snapshots go — read them from the `## Session Config` section of the root `CLAUDE.md`. They are not repeated per file. That section is the single source of truth; `init-project` fills it in during scaffolding.

## Layout requirements

- A **command** is `commands/<name>.md`, invoked as `/<name>`, with YAML frontmatter carrying at least a `description`.
- A **skill** is `skills/<name>/SKILL.md` — the filename is exact, and `scripts/validate_skills.sh` enforces the rest.

## Workflows that moved

Kept so anyone following an old reference can find where it went. These name files that no longer exist, deliberately.

| Was | Now |
|---|---|
| `.github/prompts/init-project.prompt.md` | The `init-project` skill <!-- inherited-docs-ok --> |
| `.github/prompts/session-start.prompt.md` | The `/session-start` command <!-- inherited-docs-ok --> |
| `.github/prompts/create-commit.prompt.md` | The `/commit-msg` command <!-- inherited-docs-ok --> |
| `.github/prompts/branch-workflow.prompt.md` | The `/branch-workflow` command <!-- inherited-docs-ok --> |
| `.github/prompts/sync-template.prompt.md` | The `/sync-template` command <!-- inherited-docs-ok --> |
| `.github/prompts/troubleshoot.prompt.md` | Removed with no replacement in this repo <!-- inherited-docs-ok --> |
| The `session-manager` skill | Split into `/session-start`, `/session-end` and `/commit-msg` |

The `.github/prompts/` folder is gone. It existed for GitHub Copilot's attach-a-file behavior, which nothing in this repo depends on any more; slash commands do the same job natively and need no attaching.
