# Security Policy

## Supported versions

This is a project template, not a deployed application. There are no versioned releases to patch. Security considerations apply to the tooling and dependency defaults included in the template.

## Reporting a vulnerability

If you find a security issue in this template — for example, an insecure default in the CI workflow, a vulnerable dependency in `requirements-dev.txt`, or a misconfiguration in `.github/` — please report it privately rather than opening a public issue.

**How to report:**
Use GitHub's private vulnerability reporting feature:
`Security` tab → `Report a vulnerability`

**Response time:**
This is a solo-maintained project. Expect an initial response within 7 days. Critical issues will be prioritized.

## Dependency vulnerabilities

Dependabot is enabled on this repo and runs weekly. It watches the ecosystems listed in [`.github/dependabot.yml`](.github/dependabot.yml) — currently `github-actions` and `pip`, the latter covering the pinned lint and test tooling in `requirements-dev.txt`. The `init-project` skill adds a block per ecosystem it scaffolds, so a project built from this template widens that list to match its own stack.

`scripts/check_doc_claims.sh` verifies that the ecosystems named in this section match what `.github/dependabot.yml` actually configures, so this paragraph cannot quietly drift out of date. If you spot a vulnerable dependency that Dependabot hasn't caught, please report it using the process above.
