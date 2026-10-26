# System Context — Draft

```mermaid
flowchart TB
  U[Workspace member] --> W[Angular SPA]
  W -->|HTTPS / REST| A[Spring Boot modular monolith]
  A --> P[(PostgreSQL)]
```

The browser never reads the database directly. Authentication and authorization are always enforced by the API. Redis and messaging are deferred until a measured use case justifies them.
