# FlowDesk Product Requirements — Draft

## Problem
Small teams need a centralized workspace for project tracking, task ownership and auditable approval decisions.

## Personas
- Workspace Owner: configure members and workspace permissions.
- Project Manager: organize projects, assign tasks, review requests.
- Member: manage assigned tasks and request approvals.

## MVP scope
1. Secure authentication and server-side workspace authorization.
2. Workspace/member lifecycle and project CRUD.
3. Task lifecycle with assignee, priority and status, including Kanban board.
4. Approval request, approve/reject transitions and immutable action history.
5. Basic dashboard and audit events.

## Non-goals for MVP
Microservices, Kafka, distributed orchestration, real-time notifications, rich reporting and third-party payments.

## Quality targets (to validate, not achieved yet)
- Reproducible local setup and automated CI.
- Automated race-condition tests for approval transitions.
- Accessibility-minded Angular UI and responsive layout.
- Traceable error handling without exposing sensitive data.
