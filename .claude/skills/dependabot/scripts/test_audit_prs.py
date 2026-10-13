"""Tests for audit_prs.py.

Run with:

    python3 -m pytest .claude/skills/dependabot/scripts/test_audit_prs.py -q
"""
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest

SCRIPT_DIR = Path(__file__).parent
SCRIPT = SCRIPT_DIR / "audit_prs.py"
sys.path.insert(0, str(SCRIPT_DIR))

import audit_prs
from categorize_prs import categorize

NOW = datetime(2026, 10, 13, tzinfo=timezone.utc)
GREEN = [{"status": "COMPLETED", "conclusion": "SUCCESS"}]


def make(number, title, branch="dependabot/pip/x", **extra):
    base = {"number": number, "title": title, "url": "u", "headRefName": branch}
    return categorize({**base, **extra})


def audit_one(title, **extra):
    return audit_prs.audit([make(1, title, **extra)], now=NOW)[0]


# ------------------------------------------------------------------- CI state


@pytest.mark.parametrize(
    "rollup,expected",
    [
        (None, "none"),
        ([], "none"),
        (GREEN, "passing"),
        ([{"status": "COMPLETED", "conclusion": "SKIPPED"}], "passing"),
        ([{"status": "IN_PROGRESS", "conclusion": ""}], "pending"),
        ([{"state": "PENDING"}], "pending"),
        ([{"status": "COMPLETED", "conclusion": "FAILURE"}], "failing"),
        ([{"state": "ERROR"}], "failing"),
        # Failing outranks pending: a red check is already a verdict.
        ([{"status": "IN_PROGRESS"}, {"status": "COMPLETED", "conclusion": "FAILURE"}], "failing"),
    ],
)
def test_ci_state(rollup, expected):
    assert audit_prs._ci_state(rollup) == expected


# ------------------------------------------------------------ recommendations


def test_green_minor_is_merge_candidate():
    row = audit_one("Bump requests from 2.30.0 to 2.31.0", statusCheckRollup=GREEN)
    assert row["recommendation"] == "merge-candidate"


def test_missing_signal_fields_do_not_raise():
    row = audit_one("Bump requests from 2.30.0 to 2.31.0")
    assert row["ci"] == "none"
    assert row["age_days"] is None
    assert row["recommendation"] == "merge-candidate"


def test_major_is_never_promoted_by_green_ci():
    row = audit_one("Bump lodash from 3.10.1 to 4.17.21", statusCheckRollup=GREEN)
    assert row["recommendation"] == "review-major"


def test_grouped_stays_grouped():
    row = audit_one("Bump the pip group with 3 updates", statusCheckRollup=GREEN)
    assert row["recommendation"] == "review-grouped"


def test_unrecognized_title_is_manual_review():
    assert audit_one("Add a shiny feature")["recommendation"] == "manual-review"


def test_failing_ci_is_investigate_not_merge():
    row = audit_one(
        "Bump requests from 2.30.0 to 2.31.0",
        statusCheckRollup=[{"status": "COMPLETED", "conclusion": "FAILURE"}],
    )
    assert row["recommendation"] == "investigate-ci"
    assert "CI failing" in row["signals"]


def test_pending_ci_waits():
    row = audit_one("Bump requests from 2.30.0 to 2.31.0", statusCheckRollup=[{"status": "QUEUED"}])
    assert row["recommendation"] == "wait"


@pytest.mark.parametrize("extra", [{"mergeable": "CONFLICTING"}, {"mergeStateStatus": "DIRTY"}])
def test_conflict_is_rebase(extra):
    row = audit_one("Bump requests from 2.30.0 to 2.31.0", statusCheckRollup=GREEN, **extra)
    assert row["recommendation"] == "rebase"
    assert "conflicts" in row["signals"]


def test_behind_but_green_is_rebase():
    row = audit_one("Bump requests from 2.30.0 to 2.31.0", statusCheckRollup=GREEN, mergeStateStatus="BEHIND")
    assert row["recommendation"] == "rebase"


def test_conflict_outranks_failing_ci():
    """A conflicting branch's CI result is not worth reading until it is rebased."""
    row = audit_one(
        "Bump requests from 2.30.0 to 2.31.0",
        mergeable="CONFLICTING",
        statusCheckRollup=[{"status": "COMPLETED", "conclusion": "FAILURE"}],
    )
    assert row["recommendation"] == "rebase"


# ------------------------------------------------------------------- security


def test_security_label_is_flagged():
    row = audit_one("Bump requests from 2.30.0 to 2.31.0", labels=[{"name": "security"}, {"name": "dependencies"}])
    assert row["security"] is True
    assert "security" in row["signals"]


def test_no_labels_is_not_security():
    assert audit_one("Bump requests from 2.30.0 to 2.31.0")["security"] is False


# ------------------------------------------------------------------------ age


def test_age_in_days_and_old_flag():
    row = audit_one("Bump requests from 2.30.0 to 2.31.0", createdAt="2026-08-01T00:00:00Z")
    assert row["age_days"] == 73
    assert "open 73d" in row["signals"]


def test_young_pr_has_no_age_signal():
    row = audit_one("Bump requests from 2.30.0 to 2.31.0", createdAt="2026-10-10T00:00:00Z")
    assert row["age_days"] == 3
    assert not any(s.startswith("open ") for s in row["signals"])


def test_bad_timestamp_is_null_not_an_error():
    assert audit_one("Bump requests from 2.30.0 to 2.31.0", createdAt="yesterday")["age_days"] is None


# ----------------------------------------------------------------- superseded


def test_older_bump_of_same_package_is_superseded():
    rows = audit_prs.audit(
        [
            make(1, "Bump requests from 2.30.0 to 2.31.0"),
            make(2, "Bump requests from 2.30.0 to 2.32.0"),
        ],
        now=NOW,
    )
    assert rows[0]["recommendation"] == "close-superseded"
    assert rows[0]["superseded_by"] == 2
    assert rows[1]["superseded_by"] is None
    assert rows[1]["recommendation"] == "merge-candidate"


def test_superseded_even_when_the_older_pr_is_a_major():
    rows = audit_prs.audit(
        [
            make(1, "Bump lodash from 3.0.0 to 4.0.0"),
            make(2, "Bump lodash from 3.0.0 to 5.0.0"),
        ],
        now=NOW,
    )
    assert rows[0]["recommendation"] == "close-superseded"
    assert rows[1]["recommendation"] == "review-major"


def test_same_package_in_different_directories_is_not_superseded():
    rows = audit_prs.audit(
        [
            make(1, "Bump lodash from 4.17.20 to 4.17.21 in /frontend"),
            make(2, "Bump lodash from 4.17.20 to 4.17.22 in /admin"),
        ],
        now=NOW,
    )
    assert all(r["superseded_by"] is None for r in rows)


def test_same_package_in_different_ecosystems_is_not_superseded():
    rows = audit_prs.audit(
        [
            make(1, "Bump foo from 1.0.0 to 1.1.0", branch="dependabot/pip/foo-1.1.0"),
            make(2, "Bump foo from 1.0.0 to 1.2.0", branch="dependabot/npm_and_yarn/foo-1.2.0"),
        ],
        now=NOW,
    )
    assert all(r["superseded_by"] is None for r in rows)


def test_equal_targets_are_left_alone():
    rows = audit_prs.audit(
        [
            make(1, "Bump requests from 2.30.0 to 2.31.0"),
            make(2, "Bump requests from 2.29.0 to 2.31.0"),
        ],
        now=NOW,
    )
    assert all(r["superseded_by"] is None for r in rows)


def test_grouped_prs_never_supersede_each_other():
    rows = audit_prs.audit(
        [make(1, "Bump the pip group with 2 updates"), make(2, "Bump the pip group with 3 updates")],
        now=NOW,
    )
    assert all(r["superseded_by"] is None for r in rows)


# --------------------------------------------------------------- branch parse


def test_ecosystem_and_directory_parsed():
    row = audit_one("Bump lodash from 4.17.20 to 4.17.21 in /frontend", branch="dependabot/npm_and_yarn/frontend/lodash-4.17.21")
    assert row["ecosystem"] == "npm_and_yarn"
    assert row["directory"] == "/frontend"


def test_non_dependabot_branch_has_no_ecosystem():
    assert audit_one("Bump lodash from 4.17.20 to 4.17.21", branch="feature/x")["ecosystem"] is None


def test_input_fields_are_preserved():
    row = audit_one("Bump requests from 2.30.0 to 2.31.0")
    assert row["number"] == 1 and row["category"] == "Minor/Patch"


# ------------------------------------------------------------------ end to end


def run_script(stdin_text):
    return subprocess.run(
        [sys.executable, str(SCRIPT)], input=stdin_text, capture_output=True, text=True, check=False
    )


def test_end_to_end_emits_json_array():
    result = run_script(json.dumps([make(1, "Bump requests from 2.30.0 to 2.31.0")]))
    assert result.returncode == 0
    assert json.loads(result.stdout)[0]["recommendation"] == "merge-candidate"


def test_empty_array_is_valid_input():
    result = run_script("[]")
    assert result.returncode == 0 and json.loads(result.stdout) == []


def test_invalid_json_exits_nonzero():
    result = run_script("nope")
    assert result.returncode == 1 and "not valid JSON" in result.stderr


def test_non_array_input_exits_nonzero():
    result = run_script("{}")
    assert result.returncode == 1 and "expected a JSON array" in result.stderr
