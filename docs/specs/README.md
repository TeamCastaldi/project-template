# Technical Specifications

This folder contains technical specifications — detailed descriptions of how the system works, what it does, and how its components fit together. Specs are the bridge between plans and code.

A good spec is specific enough that a developer (or LLM) can implement from it without having to make structural decisions on the fly.

## What belongs here

- Module and component specifications
- Data models and schema definitions
- API contract definitions (request/response shapes, validation rules)
- Integration specifications (how this system talks to external services)
- Business logic documentation (rules, weights, scoring formulas)
- System behavior under edge cases and error conditions

## What does not belong here

- Why a technology was chosen (that goes in docs/ARDs/)
- Roadmaps and timelines (those go in docs/plans/)
- Step-by-step procedures (those go in docs/SOPs/)

## Naming convention

Descriptive names that reflect the module or component being specified.
Examples: `spec-user-profiles.md`, `spec-job-ranking.md`, `spec-auth-flow.md`
