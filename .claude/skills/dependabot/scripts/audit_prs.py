#!/usr/bin/env python3
"""Turn categorized Dependabot PRs into audit rows with a recommendation.

Reads the JSON array printed by categorize_prs.py from stdin. For the CI,
conflict, age and security signals to work, the PRs must also carry the extra
fields requested in the skill's Phase 1 query:

    createdAt, mergeable, mergeStateStatus, labels, statusCheckRollup

A missing field degrades to "unknown" for that signal; it never raises.

Prints a JSON array. Each PR gains:

    ecosystem       - from the branch name (dependabot/<ecosystem>/...), or null
    directory       - from a trailing " in /dir" on the title, or null
    ci              - "passing" | "failing" | "pending" | "none"
    conflict        - true when GitHub reports the branch cannot merge cleanly
    behind          - true when the branch is behind its base
    age_days        - whole days since the PR was opened, or null
    security        - true when the PR carries a label containing "security"
    superseded_by   - number of a newer open PR for the same package, or null
    signals         - short human-readable flags worth showing in a report
    recommendation  - one of the values below
    rationale       - one line saying why

Recommendations:

    close-superseded  A newer open PR bumps the same package further.
    review-major      Major (or pre-1.0 minor) bump. A human reads the notes.
    review-grouped    Dependabot's own grouped update. Left intact.
    manual-review     The title was not classifiable. Never guessed at.
    rebase            Minor/Patch, but conflicting or behind its base.
    investigate-ci    Minor/Patch with failing CI. Report it, do not fix it.
    wait              Minor/Patch with CI still running.
    merge-candidate   Minor/Patch, CI green (or no CI), clean. Safe to batch.

Order matters: a superseded PR is closed regardless of its own state, and a
non-Minor/Patch category is never promoted by good CI. Like categorize_prs.py,
this only reads its input. It does not touch git, GitHub or the network.
"""
import json
import re
import sys
from datetime import datetime, timezone

from categorize_prs import _core_version

FAILING_CONCLUSIONS = {"FAILURE", "TIMED_OUT", "CANCELLED", "ACTION_REQUIRED", "STARTUP_FAILURE"}
FAILING_STATES = {"FAILURE", "ERROR"}
PENDING_STATES = {"PENDING", "EXPECTED"}

DIRECTORY_RE = re.compile(r" in (\S+)$")


def _ci_state(rollup):
    """Fold statusCheckRollup into one word. Failing outranks pending."""
    if not rollup:
        return "none"
    pending = False
    for check in rollup:
        conclusion = (check.get("conclusion") or "").upper()
        state = (check.get("state") or "").upper()
        status = (check.get("status") or "").upper()
        if conclusion in FAILING_CONCLUSIONS or state in FAILING_STATES:
            return "failing"
        if state in PENDING_STATES or (status and status != "COMPLETED"):
            pending = True
    return "pending" if pending else "passing"


def _age_days(created_at, now):
    if not created_at:
        return None
    try:
        created = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
    except ValueError:
        return None
    return max((now - created).days, 0)


def _ecosystem(branch):
    parts = (branch or "").split("/")
    return parts[1] if len(parts) > 2 and parts[0] == "dependabot" else None


def _directory(title):
    match = DIRECTORY_RE.search(title or "")
    return match.group(1) if match else None


def _find_superseders(rows):
    """Map PR number -> number of the PR that supersedes it.

    Two PRs compete only if package, ecosystem and directory all match. The
    winner is the one with the strictly greater target version; equal targets
    are left alone rather than guessed at.
    """
    groups = {}
    for row in rows:
        if row.get("category") == "Grouped" or not row.get("package"):
            continue
        target = _core_version(row.get("new_version") or "")
        if target is None:
            continue
        key = (row["ecosystem"], row["package"], row["directory"])
        groups.setdefault(key, []).append((target, row["number"]))

    superseded = {}
    for members in groups.values():
        best_target, best_number = max(members)
        for target, number in members:
            if target < best_target:
                superseded[number] = best_number
    return superseded


def _recommend(row):
    category = row.get("category")
    if row["superseded_by"] is not None:
        return "close-superseded", f"#{row['superseded_by']} bumps the same package further."
    if category == "Major":
        return "review-major", row.get("reason", "Major bump.")
    if category == "Grouped":
        return "review-grouped", "Dependabot's own grouped update; leave intact."
    if category != "Minor/Patch":
        return "manual-review", row.get("reason", "Not classifiable.")
    if row["conflict"]:
        return "rebase", "Conflicts with its base branch."
    if row["ci"] == "failing":
        return "investigate-ci", "CI is failing; report it, do not fix it here."
    if row["ci"] == "pending":
        return "wait", "CI is still running."
    if row["behind"]:
        return "rebase", "Behind its base branch."
    return "merge-candidate", f"{row.get('reason', 'Minor/Patch bump.')} CI: {row['ci']}."


def audit(prs, now=None):
    now = now or datetime.now(timezone.utc)
    rows = []
    for pr in prs:
        merge_state = (pr.get("mergeStateStatus") or "").upper()
        row = {
            **pr,
            "ecosystem": _ecosystem(pr.get("headRefName")),
            "directory": _directory(pr.get("title")),
            "ci": _ci_state(pr.get("statusCheckRollup")),
            "conflict": (pr.get("mergeable") or "").upper() == "CONFLICTING" or merge_state == "DIRTY",
            "behind": merge_state == "BEHIND",
            "age_days": _age_days(pr.get("createdAt"), now),
            "security": any(
                "security" in (label.get("name") or "").lower() for label in pr.get("labels") or []
            ),
        }
        rows.append(row)

    superseded = _find_superseders(rows)
    for row in rows:
        row["superseded_by"] = superseded.get(row["number"])
        row["recommendation"], row["rationale"] = _recommend(row)

        signals = []
        if row["security"]:
            signals.append("security")
        if row["conflict"]:
            signals.append("conflicts")
        if row["behind"]:
            signals.append("behind base")
        if row["ci"] == "failing":
            signals.append("CI failing")
        if row["age_days"] is not None and row["age_days"] > 45:
            signals.append(f"open {row['age_days']}d")
        row["signals"] = signals
    return rows


def main():
    raw = sys.stdin.read()
    try:
        prs = json.loads(raw)
    except json.JSONDecodeError as exc:
        print(f"Error: input was not valid JSON ({exc}).", file=sys.stderr)
        sys.exit(1)

    if not isinstance(prs, list):
        print("Error: expected a JSON array of pull requests.", file=sys.stderr)
        sys.exit(1)

    print(json.dumps(audit(prs), indent=2))


if __name__ == "__main__":
    main()
