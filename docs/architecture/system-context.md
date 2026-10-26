# System Context — Draft

```mermaid
flowchart TB
  U[Workspace member] --> W[Angular SPA]
  W -->|HTTPS / REST| A[Spring Boot modular monolith]
  A --> P[(PostgreSQL)]
```

The browser never reads the database directly. Authentication and authorization are planned for M1 and must be enforced by the API when implemented; Sprint 0 has no protected business endpoints. Redis and messaging are deferred until a measured use case justifies them.
