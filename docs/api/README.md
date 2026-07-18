# API Documentation

This folder contains hand-written API documentation, integration guides, and reference material for the project's APIs.

Only relevant if this project exposes an API. Some frameworks (e.g. FastAPI) generate interactive OpenAPI docs automatically at runtime — if this project's framework does, note the URL here (e.g. `/docs`). Either way, what lives in this folder is the documentation an auto-generator can't produce: context, intent, and integration guidance.

## What belongs here

- Endpoint guides that explain the "why" behind API design choices
- Authentication and authorization flow documentation
- Integration guides for external consumers of this API
- Postman collections or Bruno request files
- Versioning and deprecation policy
- Rate limiting and error code reference

## What does not belong here

- Auto-generated OpenAPI/Swagger specs (those are served live by the framework, if it produces them)
- Architecture decisions about the API design (those go in docs/ADRs/)
- Deployment or infrastructure docs (those go in docs/SOPs/)
