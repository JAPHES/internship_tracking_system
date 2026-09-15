# Internship Tracking System Requirements

## Product scope

The Internship Tracking System is an internal cohort-management REST API. It
manages student and supervisor identities, internship cohorts and tracks,
direct placements, weekly reporting, supervisor feedback, and progress
dashboards. It deliberately excludes a public opportunity marketplace and an
application/approval workflow.

## Roles and authorization

- **Student:** self-register, manage their own profile, see their own placement,
  create/edit/submit their own weekly reports, and see feedback and dashboard
  metrics.
- **Supervisor:** manage their own profile, see only assigned students and their
  reports, review submitted reports, and see supervisor dashboard metrics.
- **Administrator:** manage accounts, profiles, cohorts, tracks, and placements;
  inspect all reports; and see cohort-wide dashboard metrics and overdue users.

Every domain queryset is scoped by role. Mutating actions additionally use
role- and object-level permissions. Client-side visibility is never treated as
authorization.

## Core functional requirements

1. Email/password authentication uses a UUID-backed custom user and JWT access
   and refresh tokens.
2. Student registration creates a user and `StudentProfile` atomically.
   Supervisor and administrator accounts are administrator-created.
3. A student can have at most one current (`PLACED` or `ACTIVE`) placement.
4. Placements assign a student to one supervisor, track, and cohort and carry
   their own dates and lifecycle status.
5. A weekly report is unique per placement and week number. Students can edit
   their reports and submit drafts or previously reviewed reports. Resubmitting
   preserves the latest feedback while clearing review attribution/timestamp.
6. Only the assigned supervisor can review a submitted report.
7. Dashboards expose role-relevant aggregate data without leaking other users'
   objects.

## Overdue definition

Week `n` starts on `placement.start_date + 7 * (n - 1)` and ends six days
later, capped at the placement end date. It becomes expected after that week end
has passed. An expected week is overdue when no report in `SUBMITTED` or
`REVIEWED` state exists for that placement/week. Drafts do not satisfy the
submission requirement. A student is at risk when one or more expected weeks
are overdue.

## Non-functional requirements

- PostgreSQL is the production database. SQLite is available only when
  `USE_SQLITE=True` is explicitly configured for local development/testing.
- Configuration and secrets come from environment variables.
- OpenAPI schema and Swagger UI document the versioned API.
- Validation is present in serializers, models, and database constraints where
  each layer can enforce it reliably.
- List endpoints are paginated and support relevant filtering, search, and
  ordering.
- Static files are served through WhiteNoise and the production server is
  Gunicorn behind HTTPS-aware proxy settings.
- Automated tests cover authentication, authorization, lifecycle rules,
  dashboards, and health checks.

## MVP acceptance criteria

- All routes listed in `docs/api-endpoints.md` are reachable with documented
  permissions.
- `python manage.py check`, migration drift checks, migrations, `pytest`, and
  `ruff check .` complete successfully in the supported environment.
- Demo data, a Postman collection, Render configuration, and complete setup
  documentation are included without real credentials or secrets.

## Explicitly deferred

Public listings, opportunity applications/approvals, payments, real-time chat,
video, complex notifications, a mobile client, AI feedback generation,
multi-tenancy, and microservices are future work.
