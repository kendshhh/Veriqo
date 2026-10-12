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

The final technology stack is awaiting group confirmation.

The system will include:

- A browser extension interface.
- A backend API.
- An AI analysis component.
- A relational database.
- Automated checks and deployment.

Confirmed tools:

- GitHub — Source code and collaboration.

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
