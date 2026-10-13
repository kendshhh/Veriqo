# Veriqo
AI-powered browser extension that detects phishing emails, explains suspicious indicators, and saves analysis history through a backend API and database with automated CI/CD.

## Backend database

The backend uses Python 3.12, SQLAlchemy, Alembic, and PostgreSQL hosted on Neon.
Database models live in `backend/app/models.py`; migrations live in
`backend/migrations/versions/`.

| Table | Purpose | Relationship |
| --- | --- | --- |
| `users` | Unique email identity and creation timestamp | Owns many analyzed emails |
| `analyzed_emails` | Raw subject/body, classification, confidence, risk, indicators, and AI explanation | Belongs to a user through `user_id` |

IDs are generated UUIDs. Timestamps include the timezone. Email uniqueness ignores
case and surrounding spaces. Deleting a user also deletes their analyzed emails.
An index supports history ordered by creation time and ID.

Classification values are `Phishing`, `Spam`, and `Legitimate`. Risk levels are
`Low`, `Medium`, `High`, and `Critical`. Confidence is a finite percentage between
0 and 100. Threat indicators are a JSONB array of strings, defaulting to `[]`.
Raw content and explanations must be nonblank. Results are saved after analysis;
there are no pending/failed analysis records in this schema.

### Install

From the repository root:

```sh
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt -e .
```

Copy `.env.example` to `.env` only if you do not already have `.env`. Set
`DATABASE_URL` to your Neon PostgreSQL connection string, keeping its TLS query
parameters (for example, `sslmode=require`). The backend accepts `postgresql://`
and converts it to SQLAlchemy's psycopg driver internally. Never commit `.env`.

### Migrate and seed

```sh
alembic upgrade head
alembic current
python -m app.seed
```

These commands write to the database named by `DATABASE_URL`. Use a development
Neon database or branch for demo setup. Migrations run transactionally and Alembic
tracks revision `0001` in `alembic_version`; repeating `upgrade head` is safe.

Seeding explicitly adds one synthetic user (`demo@example.invalid`) and three
synthetic email results. It makes no AI calls, does not run automatically, and
can be repeated without adding duplicates or replacing existing records.
Demo user ID: `11111111-1111-4111-8111-111111111111`.

This initial migration expects a fresh database. If the earlier Drizzle migration
was already applied manually, use a fresh development database for Alembic; this
migration does not automatically adopt existing tables.

### Verify locally

```sh
ruff check backend scripts
ruff format --check backend scripts
python -m pytest -q
```

Without `TEST_DATABASE_URL`, PostgreSQL integration tests are explicitly skipped.
For complete verification, use a disposable PostgreSQL database:

```sh
TEST_DATABASE_URL=postgresql://USER:PASSWORD@localhost/veriqo_test python -m pytest -q
```

Tests create and remove only their own randomly named schema. They apply the
actual migration, verify models and constraints, repeat the seed, and test cascade
deletes. `TEST_DATABASE_URL` is never inferred from your Neon `DATABASE_URL`.

Alternatively, with local PostgreSQL binaries installed, this helper creates a
temporary cluster, runs every test, and stops/removes the cluster afterward:

```sh
PG_BIN=/opt/homebrew/opt/postgresql@16/bin python scripts/test_postgres.py -q
```

On other systems, point `PG_BIN` to the directory containing `initdb` and `pg_ctl`.
The helper binds only to localhost and does not start a persistent system service.

For future model changes, generate and review a new migration; do not rewrite
already-applied migration files:

```sh
alembic revision --autogenerate -m "describe the database change"
alembic upgrade head
alembic check
```

CI workflows and deployment configuration are maintained separately by DevOps.

### Existing development database created by Drizzle

If `alembic upgrade head` reports that `classification_result` already exists,
check whether the development database was previously initialized by Drizzle.
Alembic does not read Drizzle's migration history. Do not drop existing tables or
skip creation checks to conceal a mismatched schema.

Only after verifying that existing tables, enum values, defaults, constraints,
and indexes match revision `0001`, register that revision without recreating them:

```sh
alembic stamp 0001
alembic current
alembic upgrade head
alembic check
python -m app.seed
```

`stamp` writes Alembic's revision record; it does not run the migration or change
existing application records. `current` should show `0001 (head)`, and `check`
should report no new upgrade operations. A test covers this registration path
against the archived Drizzle schema and verifies that existing records survive.
If the schema differs, use a fresh development database or prepare a reviewed
migration to reconcile the differences before stamping.

### Current database stack

The active backend exclusively uses Neon PostgreSQL, SQLAlchemy with psycopg,
and Alembic. The previous Node database dependencies, configurations, and archived
SQL fixture have been removed. References to the earlier setup above describe
only the transition for already-existing development databases. The registration
test now uses SQLAlchemy to create its disposable existing schema; it does not
load an old migration file. Only Alembic manages backend migration revisions.

Existing Neon tables, data, and old migration-history records are preserved;
removing local tooling does not delete database objects. `DATABASE_URL` remains
the single application connection setting, and `TEST_DATABASE_URL` is used only
for explicitly selected integration-test databases.
