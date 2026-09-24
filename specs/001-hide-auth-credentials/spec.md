# Feature Specification: Hide Auth Credentials & Secure Production Perimeter

**Feature Branch**: `001-hide-auth-credentials`
**Created**: 2026-09-24
**Status**: Draft
**Input**: User description: "хочу, что бы логин и пароль для авторизации не были видны всем пользователям, т.к. они сейчас в открытом досутпе, можем это скрыть? запусти через spec-kit"

---

## 1. Problem Statement & Background
Currently, the authentication credentials (`director` / `password`) and Cloudflare API keys are exposed in plain text within tracked repository files (e.g. `README.md`, `deploy_to_cloudflare.py`, and `scratch/` scripts). 
Furthermore, while the proxy Worker (`dashbord-partners.beckelaguas723.workers.dev`) implements Basic Auth, the direct Cloudflare Pages URL (`dashbord-partners1.pages.dev`) remains completely open to the public without authentication. Any user with the direct link can view commercial KPI reports without entering credentials.

The goal of this feature is:
1. Completely remove all hardcoded plain text credentials from tracked repository documentation and code.
2. Establish secure perimeter protection so that the dashboard cannot be accessed without authorization.
3. Manage secrets exclusively through environment variables and untracked local configuration.

---

## 2. User Scenarios & Testing

### User Story 1 — Secure Documentation & Code Sanitization (Priority: P1)
As a project stakeholder or developer, I want all sensitive credentials (passwords, usernames, API tokens) removed from `README.md`, deployment scripts, and public documentation, so that repository viewers cannot see passwords in cleartext.

- **Why this priority**: Immediate vulnerability remediation. Credentials in plaintext violate Core Principle III of the Project Constitution.
- **Independent Test**: Run a global search across all tracked git files for `director`, `password`, and API tokens; zero occurrences should be returned in public documentation or code.

**Acceptance Scenarios**:
1. **Given** a user browses the GitHub repository or `README.md`, **When** inspecting project instructions and deployment links, **Then** no plain text passwords or tokens are displayed.
2. **Given** deployment logs outputted to terminal, **When** deployment completes, **Then** credentials are never printed to terminal or committed logs.

---

### User Story 2 — Enforce Edge Authentication Across the Perimeter (Priority: P1)
As an executive or system owner, I want the production dashboard to require authentication before showing any data, and ensure direct access to `pages.dev` or direct data files cannot bypass authorization.

- **Why this priority**: Prevents unauthorized leakage of company-confidential automotive sales, margin, and partner performance metrics.
- **Independent Test**: Access both `https://dashbord-partners.beckelaguas723.workers.dev` and `https://dashbord-partners1.pages.dev` in a clean incognito browser; both must return HTTP 401 Unauthorized until valid credentials are provided.

**Acceptance Scenarios**:
1. **Given** an unauthenticated visitor navigating to the dashboard, **When** they load the website or any JSON data asset, **Then** they are presented with a browser authentication prompt (HTTP 401 `Basic realm="B2C Dashboard"`).
2. **Given** a visitor enters invalid credentials, **When** submitted, **Then** access is denied with status 401.
3. **Given** an authorized user enters the correct credentials, **When** authenticated, **Then** the full dashboard interface and reports load normally.

---

### User Story 3 — Secret Management via Environment & Untracked Config (Priority: P2)
As a system administrator or maintainer, I want credentials and tokens configured via secure Cloudflare Worker Secrets/Bindings, environment variables, or local untracked `config.local.json`, so that rotating passwords does not require git commits with plain text secrets.

- **Why this priority**: Operational security and maintainability.
- **Independent Test**: Change the password in local configuration or Cloudflare secret; verify the new password is accepted and the old one is rejected without editing version-controlled code.

**Acceptance Scenarios**:
1. **Given** `config.local.json` contains authentication configuration, **When** deployment scripts run, **Then** credentials are read securely from local config or environment variables.
2. **Given** `config.local.json` is in `.gitignore`, **When** `git status` is executed, **Then** secret files are never staged or pushed to GitHub.

---

## 3. Requirements

### Functional Requirements
- **FR-001**: Remove all instances of plain text login/password from `README.md`, `deploy_to_cloudflare.py`, and repo docs.
- **FR-002**: Replace public credential references with safe placeholder instructions (e.g. "Доступ предоставляется администратором проекта").
- **FR-003**: Provide perimeter protection on Cloudflare Pages via Pages Functions middleware (`functions/_middleware.js`) using constant-time cryptographic hash comparison (SHA-256 via `crypto.subtle`) to prevent timing attacks.
- **FR-004**: Cloudflare Worker (`dashbord-partners`) must source credentials from Worker Environment Secrets (`AUTH_USER`, `AUTH_PASS`) or Cloudflare KV rather than hardcoded literals.
- **FR-005**: All direct calls to data assets (`data.json`, etc.) must be gated behind the same authentication barrier.
- **FR-006**: Automated unit and deployment test suite must remain 100% green (all 24+ tests passing).

### Key Entities
- **Auth Credentials**: Consists of `username` (string) and `password` (string), compared as SHA-256 digests in edge runtime.
- **Auth Realm**: "B2C Dashboard" HTTP Basic Auth realm.
- **Secret Store**: Cloudflare Worker Environment Variables / Pages Environment Secrets / local `config.local.json`.

---

## 4. Success Criteria
- **SC-001**: 100% of tracked repository files are clean of plain text passwords and API tokens.
- **SC-002**: Any unauthenticated HTTP request to the dashboard domain returns HTTP 401.
- **SC-003**: Authorized users experience zero latency degradation (< 50ms auth validation overhead at edge).
- **SC-004**: All 24 unit tests pass without regressions.

---

## 5. Assumptions & Constraints
- Basic Auth via Cloudflare Edge (Workers / Pages Functions) is the desired mechanism to avoid complex identity provider overhead while providing instant perimeter security.
- The project owner (Boris) provides the desired login and password securely via private chat or `config.local.json`.
- Cloudflare Pages Functions are natively supported in the project root (`functions/`).
