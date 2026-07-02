# NEXT_AGENT.md

# Next Agent Operating Instructions

This repository is already designed and partially implemented.

Do **NOT** redesign the project.

Do **NOT** restart the implementation.

Continue from the current repository state.

---

# Source of Truth

Always use these files in this order:

1. `PROJECT_HANDOFF.md`
2. `agent_state.json`
3. Current repository source code

Do not rely on assumptions.

The repository is the source of truth.

---

# Architecture Lock

The following decisions are FINAL.

Do not change them without explicit user approval.

## Frontend

* Next.js (App Router)
* TypeScript
* Tailwind CSS
* shadcn/ui
* Dark / Light mode
* Responsive design

## Backend

* FastAPI
* SQLAlchemy 2.x
* Alembic

## Database

* PostgreSQL
* pgvector

## AI

* Provider abstraction
* DeepSeek as default provider
* Runtime provider switching

## RAG

Lightweight Agentic RAG

Pipeline:

User Query

↓

Professional Scope Filter

↓

Query Planner

↓

Hybrid Retrieval

* pgvector
* BM25

↓

RRF Fusion

↓

Reranker

↓

Context Builder

↓

LLM

↓

Citation Validation

↓

Response

---

# Translation Strategy

Translation tables are separate.

Never duplicate multilingual columns inside entity tables.

---

# Admin

Single administrator only.

No multi-user admin system.

No RBAC.

---

# Project Philosophy

This project is a professional AI-powered portfolio website.

Goals:

* Fast
* Minimal
* Modern
* Maintainable
* Production-ready
* Easy to extend

Avoid unnecessary complexity.

---

# Scope Rules

Only implement features described in the specification.

Do NOT introduce:

* analytics
* notifications
* dashboards
* recommendation systems
* caching frameworks
* background workers
* monitoring systems
* additional authentication providers
* optional integrations

unless explicitly requested by the user.

---

# Implementation Rules

Before writing code:

* Read `PROJECT_HANDOFF.md`
* Read `agent_state.json`

Then determine the first unfinished task.

Implement only that task.

Continue sequentially.

Never jump ahead.

---

# Refactoring Rules

Do not rewrite working code.

Refactor only if:

* required to complete a feature
* required to fix a bug
* required for correctness

Never refactor for personal preference.

---

# Testing Rules

Test only the code you modify.

Avoid repository-wide test execution unless requested.

Avoid expensive verification loops.

---

# Token Efficiency Rules

Minimize repository reads.

Do not reread files already loaded unless they changed.

Do not reread the specification unless required.

Keep responses concise.

Spend tokens on implementation instead of explanations.

---

# State Management

`agent_state.json` is mandatory.

Update it:

* after every completed logical component
* before every response
* before stopping work

The state file must always match the repository.

---

# Git Rules

Prefer small logical commits.

Do not modify unrelated files.

Do not rename directories without necessity.

---

# If Blocked

If an architectural decision is required:

Stop.

Explain the options briefly.

Wait for user approval.

Do not guess.

---

# Completion Rule

When a package is finished:

1. Update `PROJECT_HANDOFF.md`
2. Update `agent_state.json`
3. Report:

   * completed work
   * remaining work
   * modified files
   * known limitations

Then stop and wait for the next instruction.

---

# Golden Rule

Continue the existing project.

Do not redesign it.

Do not restart it.

Do not expand its scope.

Implement the next unfinished task with the smallest correct change.
Priority Rule

When the project reaches approximately 80% backend completion, new packages must prioritize completing the core business logic over auxiliary CRUD improvements.

Core architecture always has higher priority than convenience features.

Do not spend implementation packages on low-impact improvements while critical architecture remains incomplete.