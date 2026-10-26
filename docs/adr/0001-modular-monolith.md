# ADR-0001: Start with a modular monolith

- **Status:** Accepted for initial architecture
- **Date:** 2026-10-23

## Context
FlowDesk is a portfolio MVP with tightly related identity, project, task and approval workflows. Networked services would multiply deployment, debugging and consistency complexity before traffic or organizational scale demand it.

## Decision
Implement a single Spring Boot deployable with explicit feature packages, application-layer transaction boundaries, isolated domain logic and PostgreSQL as the source of truth. Build separate frontend and backend apps in one monorepo.

## Consequences
- **Benefits:** simpler local onboarding, transactions, refactoring and integration testing.
- **Trade-offs:** service-level independent scaling/deployment is unavailable; careless package dependencies can erode modularity.
- **Review trigger:** real evidence of deployment/scaling/team ownership constraints, not technology fashion.
