# Skills

Claude Code skills that ship with this template. Before adding one, check [`../README.md`](../README.md) — a workflow you invoke by name belongs in `commands/`, not here, and choosing wrong is what produced the layout this folder replaced. Every project cloned from it inherits this folder, so what lives here is a standing cost on every downstream project — a skill that is wrong for a project still loads its description into that project's every session.

## What belongs here

A skill earns a slot here when all three are true:

- **It is about building software, not about one person's environment.** Workflows that apply to any repo — starting a session, writing a commit, triaging dependency PRs, keeping docs honest.
- **It works on a fresh clone**, with no host, service, or account that the template cannot assume exists.
- **It is not already available from a marketplace the user has installed.** A duplicate here competes with the marketplace copy for the same trigger phrases, and the two drift apart independently.

## What does not belong here

- Skills tied to specific infrastructure — named hosts, a particular reverse proxy, a home lab, one company's deploy pipeline. These belong in a personal skills directory or a marketplace, not in a template handed to unrelated projects.
- Skills tied to one person's non-engineering workflows (job hunting, meal planning, personal correspondence).
- A second copy of a skill the user already gets from a marketplace.

## Layout requirements

Claude Code discovers a skill by looking for `SKILL.md` inside a directory under `.claude/skills/`. Two things follow, and both have bitten this repo before:

```
.claude/skills/
└── my-skill/
    ├── SKILL.md          ← must be exactly this name
    ├── scripts/          ← optional helper scripts
    └── references/       ← optional supporting docs
```

- **The file must be named `SKILL.md`.** Not `my-skill-SKILL.md`. A renamed file does not load, does not error, and does not appear anywhere — it simply never triggers, and the only symptom is a skill that "doesn't seem to work."
- **`SKILL.md` needs YAML frontmatter with `name` and `description`.** The `name` must match the directory name.
- **Do not commit packaged `.skill` archives.** A zip alongside the unpacked directory is a second copy that drifts, and nothing loads it from here.

`scripts/validate_skills.sh` checks all of this in CI. Run it before committing a new skill:

```bash
bash scripts/validate_skills.sh
```

## Writing a skill

Anthropic's [skill authoring guide](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) is the reference. The rules this repo holds its own skills to:

- **Stay inside the limits.** A `name` of 1–64 lowercase letters, digits and hyphens, without "anthropic" or "claude"; a `description` of at most 1,024 characters with no XML tags; a body of at most 500 lines. `validate_skills.sh` fails on each. Claude Code itself tolerates more, but claude.ai uploads and the Skills API do not.
- **The description says what and when.** Write it in the third person, with the trigger phrases a user would actually type. Claude reads only the description when choosing a skill, so "when to use this" belongs there, not in the body. `init-project`'s is the model.
- **The body holds what Claude needs to act.** Reasoning written for maintainers goes in a README; see "Which workflow keeps which docs true" in [`../README.md`](../README.md).
- **Put what must not be lost at the top.** After compaction, Claude Code keeps only the start of an invoked skill, roughly 20,000 characters, and `validate_skills.sh` warns past that. Give a long workflow a progress checklist to copy, as `init-project` and `dependabot` do.
- **Move detail into files the skill links, one level deep.** `SKILL.md` links each one and says when to read it; a linked file links nothing further. Give a file over 100 lines a table of contents. See `init-project/references/`.
- **Name scripts by repo-relative path,** as in `bash .claude/skills/<name>/scripts/<script>.sh`. A bare `scripts/…` resolves to the root `scripts/` folder, and `${CLAUDE_SKILL_DIR}` expands to an absolute path the allow rules in `.claude/settings.json` do not match.
- **Ship three evaluations** with any new skill, and re-run them after changing one, as described under [Evaluations](#evaluations). Give a code fixture a non-`.py` extension (`stub.py.txt`), because CI runs `pytest` and `ruff` over all of `.claude/skills`.

## Testing a skill's scripts

A skill that ships executable scripts ships tests for them, colocated in the same `scripts/` directory as `test_*.sh` or `test_*.py`. CI runs them on every push. See `.github/workflows/skills-ci.yml`.

## Evaluations

Script tests prove a skill's scripts work. They cannot tell you whether Claude picks the skill for the right request, or follows it once it has. Each skill has three evaluations for that, in `evals/evals.json`, in the [skill-creator](https://agentskills.io/skill-creation/evaluating-skills) format:

1. a request the skill should trigger on
2. a near-miss it should not trigger on, usually a request that belongs to a neighbouring command or skill
3. a behaviour the skill must get right once it runs

They need a model, so CI does not run them. Run them by hand after changing a skill's description or instructions:

1. Install the plugin once: `/plugin install skill-creator@claude-plugins-official`.
2. In a fresh session, in the setup below, ask: `evaluate the <name> skill with skill-creator`. A fresh session matters: context left over from editing the skill hides gaps in what it actually says.
3. Repeat for each model family you expect the skill to run on (`/model`).

skill-creator's documented layout puts run output in a `<name>-workspace/` folder beside the skill. That path is gitignored. Delete the folder when you are done, because `validate_skills.sh` reads any folder here as a skill.

| Skill | Cases | Run them in |
|---|---|---|
| `dependabot` | 1 | A repo with `gh` authenticated. An empty Dependabot queue is fine; the skill should still preflight first. |
| `dependabot` | 2 | A repo that has `requirements-dev.txt`. |
| `dependabot` | 3 | Any repo, after creating an uncommitted file, for example `echo note > scratch.md`. |
| `docs-updater` | 1–3 | An initialized project. In this template, build one with `bash scripts/simulate_init.sh python-cli <dir>`. |
| `init-project` | 1, 3 | A fresh clone of the template. They do not apply in a project. |
| `init-project` | 2 | An initialized project. |
| `sync-from-template` | 1 | An initialized project with one line of `.claude/commands/commit-msg.md` edited, so the report has a change to show. It needs network access to the template repo. |
| `sync-from-template` | 2 | An initialized project. |
| `sync-from-template` | 3 | An initialized project with an extra `.claude/commands/local-note.md`. |
| `testing-standards` | 1–3 | Any repo. The prompts carry their own code. |
