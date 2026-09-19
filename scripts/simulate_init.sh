#!/usr/bin/env bash
# simulate_init.sh
#
# Builds a copy of this template transformed the way init-project's phases say
# to transform it, for a given project shape. The result is fed to
# check_scaffolded_project.sh, so CI can answer a question nothing else does:
# would a fresh clone, taken through the documented steps, come out clean?
#
# This is a fixture builder, not a reimplementation of the skill. It performs
# the mechanical edits the phases specify — filling placeholders, writing the
# founding brief, seeding an ADR, removing the template's own changelog — and
# deliberately nothing that needs judgement. If the two disagree, the skill is
# the source of truth and this script is what needs updating.
#
# Keeping it honest: the value here is that the verifier is a real, shippable
# check run on real projects too, not a test-only mirror. A simulation that
# drifts still cannot make the verifier accept a broken project.
#
# Usage:
#   simulate_init.sh <shape> <dest>
#
#   shape   python-cli | ts-web
#   dest    directory to create; must not already exist
#
# Exit status: 0 built, 2 bad usage.

set -euo pipefail

if [[ "$#" -ne 2 ]]; then
  echo "usage: $0 <python-cli|ts-web> <dest>" >&2
  exit 2
fi

SHAPE="$1"
DEST="$2"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC="$(cd "$HERE/.." && pwd)"

case "$SHAPE" in
  python-cli)
    PROJECT_NAME="kettle"
    BLURB="A command-line tool for brewing structured reports from messy CSV exports."
    SRC_ROOT="src/"
    TEST_COMMAND="pytest tests/ -v"
    LINT_COMMAND="ruff check ."
    MANIFEST="pyproject.toml"
    STACK_LINES="- Python 3.12\n- pytest for tests\n- ruff for lint and format\n- Click for the CLI surface"
    ADR_TITLE="Python and Click for the CLI"
    ADR_BODY="Click gives declarative subcommands and generated help, which the project needs from the first release. argparse was ruled out for the amount of boilerplate a nested command tree requires."
    ;;
  ts-web)
    PROJECT_NAME="lantern"
    BLURB="A dashboard that renders live build health for a small team's services."
    SRC_ROOT="frontend/src/"
    TEST_COMMAND="npm test"
    LINT_COMMAND="npm run lint"
    MANIFEST="package.json"
    STACK_LINES="- TypeScript 5.x on Node 22\n- React 19 with Vite\n- vitest for tests\n- eslint and prettier for lint and format"
    ADR_TITLE="Vite and React for the dashboard"
    ADR_BODY="Vite's dev server keeps the feedback loop under a second on this codebase's size, and React is what the team already reviews fluently. Next.js was ruled out: the dashboard needs no server rendering or routing beyond one page."
    ;;
  *)
    echo "$0: unknown shape: $SHAPE (expected python-cli or ts-web)" >&2
    exit 2
    ;;
esac

if [[ -e "$DEST" ]]; then
  echo "$0: destination already exists: $DEST" >&2
  exit 2
fi

# Copy tracked files only, so local caches and build artifacts stay out. Reads
# working-tree content rather than `git archive HEAD`, so an uncommitted fix is
# testable locally; in CI the two are identical, since the runner checks out the
# commit under test.
mkdir -p "$DEST"
git -C "$SRC" ls-files -z | tar -C "$SRC" --null -T - -cf - | tar -x -C "$DEST"

cd "$DEST"

# --- Phase 3: fill CLAUDE.md's Session Config -----------------------------
# One table, read by every command in .claude/commands/. Filling it here is the
# whole of what used to be a per-prompt-file Config block edit.
sed -i \
  -e "s|{set by init-project — e.g. \"pytest tests/ -v\" or \"npm test\"}|$TEST_COMMAND|" \
  -e "s|{set by init-project — e.g. \"ruff check .\" or \"npm run lint\"}|$LINT_COMMAND|" \
  -e "s|{set by init-project — the main source folder}|$SRC_ROOT|" \
  CLAUDE.md

# --- Phase 3: the root README --------------------------------------------
# Drop the one-time Getting started section, fill name, stack and quick start.
# Done in Python rather than sed: the stack block is multi-line and starts with
# a "-", which sed substitutions and printf both mangle for different reasons.
awk '
  /^## Getting started$/ { skipping = 1; next }
  skipping && /^## / { skipping = 0 }
  !skipping { print }
' README.md > README.tmp && mv README.tmp README.md

python3 - "$PROJECT_NAME" "$BLURB" "$STACK_LINES" "$TEST_COMMAND" <<'PY'
import pathlib, sys
name, blurb, stack_lines, test_cmd = sys.argv[1:5]
p = pathlib.Path("README.md")
text = p.read_text()
text = text.replace("{PROJECT_NAME}", name)
text = text.replace(
    "{One or two sentence description of what this project does and who it's for.}",
    blurb,
)
text = text.replace(
    "<!-- init-project fills this in -->",
    stack_lines.replace("\\n", "\n"),
)
text = text.replace(
    "<!-- init-project fills this in with the real setup steps for the chosen stack -->",
    f"Install dependencies, then run `{test_cmd}`.",
)
p.write_text(text)
PY

# --- Phase 3: a manifest, so the stack is real ----------------------------
case "$SHAPE" in
  python-cli) printf '[project]\nname = "%s"\nversion = "0.1.0"\n' "$PROJECT_NAME" > "$MANIFEST" ;;
  ts-web)     printf '{\n  "name": "%s",\n  "version": "0.1.0"\n}\n' "$PROJECT_NAME" > "$MANIFEST" ;;
esac

# --- Phase 3: drop what belongs to the template, not the project ----------
# The changelog logs template releases. template-ci.yml asserts that this repo
# FAILS scaffolding verification, which stops being true the moment it is
# scaffolded. simulate_init.sh has nothing left to simulate here.
rm -f CHANGELOG.md
rm -f .github/workflows/template-ci.yml
rm -f scripts/simulate_init.sh

# --- Phase 4: seed a real ADR and index it --------------------------------
ADR_FILE="ADR-001-$(tr '[:upper:] ' '[:lower:]-' <<<"$ADR_TITLE" | tr -cd '[:alnum:]-').md"
cat > "docs/ADRs/$ADR_FILE" <<EOF
# ADR-001 — $ADR_TITLE

**Status**: Accepted
**Date**: $(date -u +%Y-%m-%d)

## Context

$PROJECT_NAME needed a stack settled before any code was written.

## Decision

$ADR_BODY

## Consequences

The choice is load-bearing for every module written from here on. Revisiting it
after the first release would mean rewriting the entry points.
EOF

# Replace the empty Index placeholder row with a real one.
sed -i "s|^| _none yet_ | — | — ||| [ADR-001]($ADR_FILE) | $ADR_TITLE | Accepted ||" "docs/ADRs/README.md" 2>/dev/null || true
python3 - "$ADR_FILE" "$ADR_TITLE" <<'PY'
import pathlib, sys
adr_file, adr_title = sys.argv[1], sys.argv[2]
p = pathlib.Path("docs/ADRs/README.md")
text = p.read_text()
row = f"| [ADR-001]({adr_file}) | {adr_title} | Accepted |"
text = text.replace("| _none yet_ | — | — |", row)
p.write_text(text)
PY

# --- Phase 4: re-point the inherited docs ---------------------------------
# Only the mechanical part: strip the template-claiming language the sweep
# looks for. A real run rewrites these with judgement; the post-condition
# being tested is just that nothing still describes the template.
python3 - "$PROJECT_NAME" "$MANIFEST" "$TEST_COMMAND" "$LINT_COMMAND" <<'PY'
import pathlib, sys
name, manifest, test_cmd, lint_cmd = sys.argv[1:5]

pathlib.Path("CONTRIBUTING.md").write_text(f"""# Contributing

How to work in {name}.

## Workflow

Branch, make an atomic change, open a PR. Conventional Commits are expected.

Run the checks before pushing:

```bash
{test_cmd}
{lint_cmd}
```

## What's in scope

- Application code, tests, and the docs describing them.
""")

pathlib.Path("SECURITY.md").write_text(f"""# Security Policy

## Supported versions

{name} tracks its latest release. Older versions are not patched.

## Reporting a vulnerability

Use GitHub's private vulnerability reporting: `Security` tab -> `Report a vulnerability`.
Expect an initial response within 7 days.

## Dependency vulnerabilities

Dependabot runs weekly against the ecosystems configured in
`.github/dependabot.yml`. Application dependencies live in `{manifest}`.
""")

# .claude/README.md and .claude/skills/README.md are timeless guides that
# init-project leaves alone, so there is nothing to re-point there.
PY

# --- Phase 5: fill in CLAUDE.md -------------------------------------------
python3 - "$PROJECT_NAME" "$BLURB" "$ADR_FILE" "$ADR_TITLE" <<'PY'
import pathlib, re, sys
name, blurb, adr_file, adr_title = sys.argv[1:5]
p = pathlib.Path("CLAUDE.md")
text = p.read_text()

# Strip every HTML-comment instruction block, as the file's own header says to.
text = re.sub(r"<!--.*?-->\n?", "", text, flags=re.DOTALL)

text = text.replace(
    "## Project identity\n",
    f"## Project identity\n\n{name} — {blurb}\n",
)
text = text.replace(
    "## Decision log\n",
    f"## Decision log\n\n- [ADR-001: {adr_title}](docs/ADRs/{adr_file}) — settled the stack before any code was written.\n",
)
text = text.replace(
    "*Last updated: {date} | Session: {brief description}*",
    "*Last updated: 2026-01-01 | Session: initial scaffolding*",
)
p.write_text(text)
PY

# --- Phase 6: the founding brief ------------------------------------------
cat > docs/foundation.md <<EOF
# $PROJECT_NAME — Foundation
**Status**: Draft v0.1
**Date**: $(date -u +%Y-%m-%d)

---

## The Problem

$BLURB

## The Solution

What gets built, and how it addresses the problem.

## The User

Small teams who need this without standing up more infrastructure.

## What We Are Not Building

Anything outside the scope above.

## Success Metric

Not yet defined — revisit before first release.

## Open Questions

None recorded during scaffolding.

---
*This document is the source of truth for product intent. Architecture and technology decisions live in docs/ADRs/; this file is about why, not how.*
EOF

echo "SIMULATED=$DEST"
echo "SHAPE=$SHAPE"
