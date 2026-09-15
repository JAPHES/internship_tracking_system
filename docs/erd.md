# Entity Relationship Diagram

```mermaid
erDiagram
    USER ||--o| STUDENT_PROFILE : "has student identity"
    USER ||--o| SUPERVISOR_PROFILE : "has supervisor identity"
    USER ||--o{ PLACEMENT : "creates"
    STUDENT_PROFILE ||--o{ PLACEMENT : "is placed"
    SUPERVISOR_PROFILE ||--o{ PLACEMENT : "supervises"
    COHORT ||--o{ PLACEMENT : "groups"
    TRACK ||--o{ PLACEMENT : "categorizes"
    PLACEMENT ||--o{ WEEKLY_REPORT : "has"
    USER ||--o{ WEEKLY_REPORT : "reviews"

    USER {
        uuid id PK
        string email UK
        string first_name
        string last_name
        enum role
        boolean is_active
        boolean is_staff
        datetime date_joined
        datetime created_at
        datetime updated_at
    }

    STUDENT_PROFILE {
        uuid id PK
        uuid user_id FK,UK
        string registration_number UK
        string programme
        string department
        string phone_number
        datetime created_at
        datetime updated_at
    }

    SUPERVISOR_PROFILE {
        uuid id PK
        uuid user_id FK,UK
        string staff_number UK_nullable
        string department
        string phone_number
        datetime created_at
        datetime updated_at
    }

    COHORT {
        uuid id PK
        string name
        text description
        date start_date
        date end_date
        boolean is_active
        datetime created_at
        datetime updated_at
    }

    TRACK {
        uuid id PK
        string name UK
        text description
        boolean is_active
        datetime created_at
        datetime updated_at
    }

    PLACEMENT {
        uuid id PK
        uuid student_id FK
        uuid supervisor_id FK
        uuid track_id FK
        uuid cohort_id FK
        date start_date
        date end_date
        enum status
        uuid created_by_id FK
        datetime created_at
        datetime updated_at
    }

    WEEKLY_REPORT {
        uuid id PK
        uuid placement_id FK
        int week_number
        date week_start_date
        date week_end_date
        text activities_completed
        text skills_learned
        text challenges_faced
        enum status
        text supervisor_feedback
        datetime submitted_at
        datetime reviewed_at
        uuid reviewed_by_id FK
        datetime created_at
        datetime updated_at
    }
```

## Design decisions

- Profiles, rather than generic users, are referenced by placements. This makes
  invalid student/supervisor roles impossible once a valid profile exists.
- A conditional unique constraint prevents two non-completed placements for one
  student. Historical completed placements remain supported.
- Reports use a `(placement, week_number)` unique constraint; lifecycle methods
  centralize submit/review timestamps and transitions.
- Review attribution points to `User` so the audit record remains explicit even
  if profile details change.
