# Veriqo

Veriqo is an AI-powered browser extension for detecting
potential phishing emails, explaining suspicious indicators,
and saving analysis history.

This is our CSP221A endterm group project.

## Project Purpose

Help users identify potentially suspicious emails and understand
the reasons behind an analysis.

The extension sends email content to a backend API. The backend
handles AI analysis, validates the results, and stores records
in a database.

## Team Members and Roles

- Kendra Lynne Abellana — DevOps Engineer
  - CI/CD workflows, environments, secrets, deployment,
    pipeline metrics, releases, and rollback.
- Developer members — Names and responsibilities to be added
  after the group confirms assignments.

The team has exactly one DevOps Engineer.
All other members are Developers.

## Technology Stack

### Confirmed Decisions

- Database engine: PostgreSQL.
- Email input: Selected/highlighted text.
- Source code and collaboration: GitHub.

### Proposed Tools — Awaiting Group Confirmation

- Browser: Chrome with Manifest V3.
- Interface: HTML, CSS, and JavaScript.
- Input action: Highlight text and select a context-menu action.
- Backend: Python 3.12, FastAPI, and Pydantic.
- PostgreSQL hosting: Neon.
- Database access: SQLAlchemy.
- Migrations: Alembic.
- AI: Gemini structured output, subject to instructor approval
  of any change from the DistilBERT proposal.
- Backend hosting: Render.
- CI/CD: GitHub Actions.
- Python linting: Ruff.
- Python testing: pytest and HTTPX.
- JavaScript linting: ESLint.
- JavaScript tooling runtime: Node.js 22.
- Build: Extension validation and packaging script.

Proposed tools will be marked confirmed after group agreement.
Runtime versions and commands will be verified against the
implemented application.

## Local Setup Instructions

Setup instructions will be added after the initial application
is implemented and its commands are tested.

The instructions will cover:

1. Installing dependencies.
2. Configuring environment variables.
3. Applying database migrations.
4. Starting the backend.
5. Installing the development extension.
6. Running checks and tests.

## Branch and Pull Request Workflow

- `main` contains code intended for deployment.
- Each task is tracked through a GitHub issue.
- Each task uses a separate branch.
- Changes enter `main` through a pull request.
- At least one teammate reviews each pull request.
- Required automated checks must pass before merging.
- Merged application changes deploy automatically once
  the deployment pipeline is configured.

Example branch names:

- `docs/project-setup`
- `feat/extension-popup`
- `feat/database-schema`
- `ci/initial-workflow`
- `fix/api-error-handling`

A task is complete after review, successful checks,
merging, and verification in the deployed environment.

## Environment Variables

The required variable names will be documented in
`.env.example` as the backend and AI integration are implemented.

Real secrets must never be committed to the repository.

AI keys and database credentials belong in the backend
environment, not in the browser extension.

## Live Backend URL

Not deployed yet.

The production URL will be added after the first successful
pipeline-triggered deployment.

## Current Status

Sprint 1 — Foundation and walking skeleton.

Current priorities:

- Repository setup and team roles.
- Project backlog.
- Database schema and migrations.
- Extension-to-backend connection.
- Automated install, lint, and build checks.
- First hosted deployment.
- One real backend AI test call.

