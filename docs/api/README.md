# API Documentation

This folder contains hand-written API documentation, integration guides, and reference material for the project's APIs.

FastAPI generates interactive OpenAPI docs automatically at `/docs` (Swagger) and `/redoc` when the server is running. What lives here is the documentation that the auto-generator cannot produce — context, intent, and integration guidance.

## What belongs here

- Endpoint guides that explain the "why" behind API design choices
- Authentication and authorization flow documentation
- Integration guides for external consumers of this API
- Postman collections or Bruno request files
- Versioning and deprecation policy
- Rate limiting and error code reference

## What does not belong here

- Auto-generated OpenAPI specs (those are served live by FastAPI)
- Architecture decisions about the API design (those go in docs/ARDs/)
- Deployment or infrastructure docs (those go in docs/SOPs/)
