# Data Model — Preliminary

```mermaid
erDiagram
  USERS ||--o{ WORKSPACE_MEMBERS : belongs
  WORKSPACES ||--o{ WORKSPACE_MEMBERS : has
  WORKSPACES ||--o{ PROJECTS : owns
  PROJECTS ||--o{ TASKS : contains
  TASKS ||--o{ APPROVAL_REQUESTS : has
  APPROVAL_REQUESTS ||--o{ APPROVAL_ACTIONS : records
```

Tables beyond `app_users` are **planned only**; Flyway V1 contains the initial identity table. During M1/M2, define all FK constraints, uniqueness within workspace, soft-delete policy (if needed), indexes and auditing invariants. Never present the draft diagram as a deployed schema.
