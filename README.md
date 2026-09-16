# Internship Tracking System

A production-oriented Django REST Framework MVP for managing the complete
internship lifecycle of a student cohort: identities, direct placements,
weekly reports, supervisor feedback, and role-specific progress dashboards.

Repository target: `CDAM-task1-internship-tracking-Japhes`  
Django package: `internship_tracking`

## Problem statement

Spreadsheet-based internship coordination makes assignment ownership,
submission follow-up, feedback, and cohort reporting difficult to audit. This
system provides one secured source of truth for administrators, supervisors,
and students without introducing a public internship marketplace or an
application approval pipeline.

## Objectives

- Give students a clear placement and weekly reporting workflow.
- Give supervisors a scoped review queue and assigned-student view.
- Give administrators reliable placement management, cohort statistics, and
  overdue indicators.
- Supply a clean API foundation that can be extended after the MVP.

## Users and features

- **Students:** self-registration, JWT login, profile management, own placement,
  draft/submitted/reviewed reports, resubmission, feedback, and dashboard.
- **Supervisors:** profile management, assigned students, scoped report access,
  feedback/review action, and pending/reviewed dashboard.
- **Administrators:** account/profile/reference-data/placement management,
  report visibility, Django Admin, submission progress, and overdue students.

Authorization is enforced by backend role permissions, role-scoped querysets,
and ownership checks. See [requirements](docs/requirements.md), the
[endpoint matrix](docs/api-endpoints.md), and the [Mermaid ERD](docs/erd.md).

## Technology

Python 3.13, Django 5.2 LTS, Django REST Framework, PostgreSQL, Simple JWT,
django-filter, django-cors-headers, drf-spectacular, django-environ, psycopg,
Gunicorn, WhiteNoise, pytest, factory-boy, Ruff, and Coverage.

## Architecture

The API is one deployable Django service with modular bounded-context apps:

| App | Responsibility |
|---|---|
| `accounts` | UUID user, email authentication, roles, JWT, password changes |
| `students` | Student identity and academic/contact profile |
| `supervisors` | Supervisor identity, contact profile, assigned students |
| `cohorts` | Internship cohort dates and activation |
| `tracks` | Internship specialization reference data |
| `placements` | Direct student/supervisor/track/cohort assignment and lifecycle |
| `reports` | Weekly drafts, submission, review, feedback, resubmission |
| `dashboards` | Role-scoped aggregates and overdue calculations |
| `common` | UUID timestamps, pagination, errors, validation, health check, frontend templates |

Settings are split into `base`, `development`, `test`, and `production`.
Development defaults to Django's built-in SQLite database when `DATABASE_URL`
is absent. Production requires PostgreSQL. Transactional service functions lock
reports during submit and review transitions, while database constraints protect
dates and uniqueness.

### Overdue rule

Placement week 1 starts on the placement start date; subsequent weeks start at
seven-day intervals. A week end is capped at the placement end date. Once that
week end is earlier than today, the report is expected. It is overdue when no
`SUBMITTED` or `REVIEWED` report exists for that placement/week; a `DRAFT` does
not count. Only active placements contribute to the administrator at-risk list.

## Local installation

Prerequisites: Python 3.13+, Git, and PostgreSQL 14+.

### PowerShell

```powershell
git clone <your-repository-url>
cd CDAM-task1-internship-tracking-Japhes
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements-dev.txt
Copy-Item .env.example .env
```

If PowerShell blocks `Activate.ps1`, `manage.py` automatically uses the local
`.venv` when you run `python manage.py <command>` from the project directory.
You can also invoke it explicitly with `.\.venv\Scripts\python.exe manage.py`.

### macOS/Linux

```bash
git clone <your-repository-url>
cd CDAM-task1-internship-tracking-Japhes
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements-dev.txt
cp .env.example .env
```

Replace `<your-repository-url>` only after creating your own GitHub repository.

## PostgreSQL setup

Using `psql` as a PostgreSQL administrator:

```sql
CREATE USER internship_tracking_user WITH PASSWORD 'choose-a-local-password';
CREATE DATABASE internship_tracking OWNER internship_tracking_user;
```

Set this in the uncommitted `.env` file (URL-encode special password
characters):

```dotenv
DATABASE_URL=postgresql://internship_tracking_user:choose-a-local-password@localhost:5432/internship_tracking
USE_SQLITE=False
```

For the default local SQLite setup, set `USE_SQLITE=True`; any configured
`DATABASE_URL` is then ignored. Production settings always require PostgreSQL.

## Environment variables

| Variable | Purpose | Example/non-secret guidance |
|---|---|---|
| `DJANGO_SETTINGS_MODULE` | Settings module | `internship_tracking.settings.development` |
| `SECRET_KEY` | Django signing secret | Generate a long random value; never commit it |
| `DEBUG` | Debug mode | `True` locally, `False` in production |
| `ALLOWED_HOSTS` | Comma-separated hostnames | `localhost,127.0.0.1` |
| `CSRF_TRUSTED_ORIGINS` | Comma-separated HTTPS origins | Your deployed frontend/API origin |
| `CORS_ALLOWED_ORIGINS` | Allowed browser client origins | Your frontend origin |
| `DATABASE_URL` | PostgreSQL connection URL | Supplied by Render in production |
| `USE_SQLITE` | Local/test SQLite switch | `True` during initial local development |
| `ACCESS_TOKEN_LIFETIME_MINUTES` | JWT access lifetime | `15` |
| `REFRESH_TOKEN_LIFETIME_DAYS` | JWT refresh lifetime | `7` |
| `LOG_LEVEL` | Root log level | `INFO` |

Generate a secret locally without printing or committing it into project files,
for example with Python's `secrets.token_urlsafe(64)` in an interactive shell,
then paste it into `.env` or the hosting provider's secret field.

## Database and administrator commands

```bash
python manage.py makemigrations --check
python manage.py migrate
python manage.py createsuperuser
```

`createsuperuser` prompts for email, first name, last name, and a password. The
custom manager assigns the `ADMIN` role and staff/superuser flags.

## Demo data

Load or refresh development-only sample data:

```bash
python manage.py seed_demo_data
```

The command creates one admin, two supervisors, six students, one active cohort,
four tracks, active placements, and mixed report states. Development credentials:

- Admin: `admin@demo.local` / `DemoAdmin123!`
- Supervisor: `supervisor1@demo.local` / `DemoSupervisor123!`
- Student: `student1@demo.local` / `DemoStudent123!`

Never use these credentials in a public or production deployment. Demo seeding
is intentionally not part of the Render build.

## Run and use the system

```bash
python manage.py runserver
```

- Frontend home: `http://127.0.0.1:8000/`
- Sign in: `http://127.0.0.1:8000/login/`
- Student registration: `http://127.0.0.1:8000/register/`
- Role dashboard: `http://127.0.0.1:8000/dashboard/`
- System guide: `http://127.0.0.1:8000/system-guide/`
- Swagger UI: `http://127.0.0.1:8000/api/docs/`
- OpenAPI schema: `http://127.0.0.1:8000/api/schema/`
- Health check: `http://127.0.0.1:8000/api/v1/health/`
- Django Admin: `http://127.0.0.1:8000/admin/`

The frontend signs in through the JWT API and keeps tokens in browser session
storage, so closing the browser session clears them. It automatically selects
the student, supervisor, or administrator dashboard based on the authenticated
role. Backend permissions remain authoritative for every request.

For direct API use, obtain tokens by posting `email` and `password` to
`/api/v1/auth/token/`, then send `Authorization: Bearer <access-token>`. Import
`postman/Internship-Tracking-System.postman_collection.json` into Postman and
set its `base_url`/resource ID variables.

## Testing and quality

Tests use the dedicated test settings module and an explicit isolated SQLite
database:

```bash
python manage.py check
python manage.py makemigrations --check
pytest
coverage run -m pytest
coverage report -m
ruff check .
ruff format --check .
```

The supplied development environment uses SQLite, so these commands do not
require a local PostgreSQL server.

## Render deployment

1. Push this repository to your own GitHub account.
2. In Render, create a Blueprint and select the repository. `render.yaml`
   provisions the web service and PostgreSQL database.
3. Confirm `DJANGO_SETTINGS_MODULE=internship_tracking.settings.production`,
   `DEBUG=False`, and the managed `DATABASE_URL` connection.
4. Let Render generate `SECRET_KEY`; do not copy a development secret.
5. Set `ALLOWED_HOSTS` to the Render hostname. Set
   `CSRF_TRUSTED_ORIGINS` and `CORS_ALLOWED_ORIGINS` to full HTTPS origins,
   for example `https://your-service.onrender.com`.
6. Keep the token lifetime variables at their documented defaults or adjust
   them intentionally.
7. Deploy. `build.sh` installs packages, collects static assets, and runs
   migrations; Gunicorn starts the WSGI app. Render checks `/api/v1/health/`.
8. Create the first production administrator from a Render Shell with
   `python manage.py createsuperuser`.

Optional demo seeding must be invoked manually from a shell and is not
recommended on a public service.

## GitHub setup

The local repository is prepared for the required remote name. If no remote or
GitHub credentials exist, create an empty repository named
`CDAM-task1-internship-tracking-Japhes` in your own account, then run:

```bash
git remote add origin https://github.com/<your-username>/CDAM-task1-internship-tracking-Japhes.git
git branch -M main
git push -u origin main
```

Replace `<your-username>` yourself. No remote URL is assumed by this project.

## Screenshots

_Placeholder: add Swagger UI, Django Admin, and Postman response screenshots._

## Live URL

_Placeholder: add the verified Render URL after deployment._

## Future improvements

- Email reminders and a lightweight notification queue.
- Exportable cohort reports and richer time-series analytics.
- Audit-event history for administrative changes.
- Refresh-token rotation/blacklisting and optional MFA.
- Frontend accessibility and end-to-end browser tests.
- Object-storage attachments for approved report evidence.
- A mobile client after the API contract stabilizes.

Public marketplaces, payments, real-time chat/video, AI-authored feedback,
multi-tenancy, and microservices remain outside the MVP.
