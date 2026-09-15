# API Endpoints

All application endpoints use `/api/v1/`. Unless noted, send a JWT access token
as `Authorization: Bearer <token>`.

| Area | Routes | Access |
|---|---|---|
| Authentication | `POST auth/register/student/`, `POST auth/token/`, `POST auth/token/refresh/` | Public (throttled) |
| Account | `GET auth/me/`, `POST auth/change-password/` | Authenticated owner |
| Students | CRUD `students/`, `GET/PATCH students/me/` | Admin CRUD; student self read/update |
| Supervisors | CRUD `supervisors/`, `GET/PATCH supervisors/me/`, `GET supervisors/me/students/` | Admin CRUD; supervisor self/assigned students |
| Cohorts | CRUD `cohorts/` | Authenticated read; admin write |
| Tracks | CRUD `tracks/` | Authenticated read; admin write |
| Placements | CRUD `placements/`, `GET placements/me/` | Role-scoped read; admin write |
| Reports | CRUD `reports/`, `POST reports/{id}/submit/`, `POST reports/{id}/review/` | Role-scoped read; student authoring; assigned-supervisor review |
| Dashboards | `GET dashboard/student/`, `GET dashboard/supervisor/`, `GET dashboard/admin/` | Matching role |
| System | `GET health/`, `GET /api/schema/`, `GET /api/docs/` | Public |

List endpoints expose page-number pagination. Resource-specific filters,
case-insensitive search, and ordering parameters are described in Swagger.

Errors use this shape:

```json
{
  "error": {
    "code": "validation_error",
    "message": "The request could not be processed.",
    "details": {"field": ["A validation message."]}
  }
}
```
