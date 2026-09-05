#!/usr/bin/env python3
"""Categorize open Dependabot pull requests by SemVer risk.

Reads a JSON array of pull requests from stdin - the shape produced by:

    gh pr list --author "app/dependabot" --state open \
        --json number,title,url,headRefName --limit 100

Prints a JSON array to stdout. Each PR is enriched with:

    package       - dependency name, or "group:<name>" for a grouped update
    old_version   - version string before the bump (null if not parseable)
    new_version   - version string after the bump (null if not parseable)
    category      - "Major" | "Minor/Patch" | "Grouped" | "Unknown"
    reason        - a one-line, human-readable explanation of the category

Category rules:

    Major        A major-version bump (e.g. 3.x -> 4.x). Also covers a
                 pre-1.0 MINOR bump (e.g. 0.4.x -> 0.5.x): SemVer makes no
                 compatibility promise below 1.0, so a 0.x minor bump
                 carries the same "anything can break" risk as a major
                 bump on a stable release. Treat it the same way.
    Minor/Patch  A minor or patch bump on a stable (>=1.0) release, or a
                 patch-only bump within the same 0.x minor line
                 (0.4.1 -> 0.4.3). This is the safe, stackable set.
    Grouped      One of Dependabot's own grouped-update PRs. It already
                 bundles several packages that were tested together;
                 pulling it apart to cherry-pick individual packages
                 risks breaking a combination its maintainers verified.
                 Left intact, not decomposed.
    Unknown      The PR title didn't match a recognized Dependabot
                 pattern, or a version number couldn't be parsed. Never
                 guess a risk level here - route it to manual review.

This script only classifies. It does not touch git, GitHub, or any
repository state.
"""
import json
import re
import sys

GROUPED_RE = re.compile(
    r"^Bump the (?P<group>[\w./-]+) group"
    r"(?: across \d+ director(?:y|ies))?"
    r" with (?P<count>\d+) updates?",
    re.IGNORECASE,
)

SINGLE_RE = re.compile(
    r"^Bump (?P<package>\S+) from (?P<old>\S+) to (?P<new>\S+)",
    re.IGNORECASE,
)


def _core_version(raw):
    """Return the (major, minor, patch) ints from a version string.

    Strips pre-release/build metadata (anything after a "-" or "+") and
    reads up to the first three dot-separated numeric segments. A leading
    "v" is stripped first, since GitHub Actions dependencies are commonly
    tagged "v2", "v3", etc. rather than "2.0.0". Returns None if no
    leading numeric run is found - callers must treat that as "could not
    parse", never as "0".
    """
    core = re.split(r"[-+]", raw, maxsplit=1)[0]
    core = re.sub(r"^[vV]", "", core)
    segments = core.split(".")
    nums = []
    for segment in segments[:3]:
        match = re.match(r"\d+", segment)
        if not match:
            return None
        nums.append(int(match.group()))
    while len(nums) < 3:
        nums.append(0)
    return tuple(nums)


def categorize(pr):
    title = pr.get("title", "")

    grouped = GROUPED_RE.match(title)
    if grouped:
        return {
            **pr,
            "package": f"group:{grouped.group('group')}",
            "old_version": None,
            "new_version": None,
            "category": "Grouped",
            "reason": (
                f"Dependabot's own grouped update "
                f"({grouped.group('count')} package(s)). Left intact "
                "rather than split apart, since the group was tested "
                "together."
            ),
        }

    single = SINGLE_RE.match(title)
    if not single:
        return {
            **pr,
            "package": None,
            "old_version": None,
            "new_version": None,
            "category": "Unknown",
            "reason": "Title did not match a recognized Dependabot pattern. Needs manual review.",
        }

    package = single.group("package")
    old_raw, new_raw = single.group("old"), single.group("new")
    old_version, new_version = _core_version(old_raw), _core_version(new_raw)

    base = {**pr, "package": package, "old_version": old_raw, "new_version": new_raw}

    if old_version is None or new_version is None:
        return {
            **base,
            "category": "Unknown",
            "reason": "Could not parse one or both version numbers. Needs manual review.",
        }

    old_major, old_minor, _ = old_version
    new_major, new_minor, _ = new_version

    if new_major != old_major:
        return {
            **base,
            "category": "Major",
            "reason": f"Major version bump ({old_major} -> {new_major}).",
        }

    if old_major == 0 and new_minor != old_minor:
        return {
            **base,
            "category": "Major",
            "reason": (
                f"0.{old_minor}.x -> 0.{new_minor}.x on a pre-1.0 package. "
                "SemVer treats the minor number as the breaking axis "
                "below 1.0, so this carries major-bump risk."
            ),
        }

    return {
        **base,
        "category": "Minor/Patch",
        "reason": f"{old_raw} -> {new_raw} is a minor/patch bump on a stable release.",
    }


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

    print(json.dumps([categorize(pr) for pr in prs], indent=2))


if __name__ == "__main__":
    main()
