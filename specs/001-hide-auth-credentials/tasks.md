# Tasks: Hide Auth Credentials & Secure Production Perimeter

**Input**: Design documents from `specs/001-hide-auth-credentials/`
**Prerequisites**: [plan.md](./plan.md) (required), [spec.md](./spec.md) (required)

## Phase 1: Setup & Foundational Security

- [x] T001 Create `functions/` and `site/functions/` directories for Cloudflare Pages Functions.
- [x] T002 Verify `.gitignore` enforces untracked status for `config.local.json`, `.env`, and secret archives.

## Phase 2: User Story 1 — Documentation & Code Sanitization (Priority: P1)

**Goal**: Remove all plain text passwords, usernames, and secret tokens from version-controlled files.
**Independent Test**: Grep repository for hardcoded plaintext credentials; return zero results in tracked documentation.

- [x] T003 [US1] Sanitize `README.md`: replace plain text `Basic Auth: director / password` with secure access policy.
- [x] T004 [US1] Sanitize `deploy_to_cloudflare.py`: mask credentials and direct URLs in terminal logs.
- [x] T005 [US1] Sanitize `scratch/deploy_worker_with_kv.py` and `scratch/update_worker.py`: source credentials dynamically from `config.local.json` / environment variables.

## Phase 3: User Story 2 — Edge Perimeter Protection (Priority: P1)

**Goal**: Enforce HTTP Basic Auth across the entire Cloudflare Pages domain (`dashbord-partners1.pages.dev`).
**Independent Test**: Send unauthenticated HTTP request to `https://dashbord-partners1.pages.dev`; verify response is HTTP 401 with `WWW-Authenticate` header.

- [x] T006 [US2] Implement `functions/_middleware.js` with RFC 7617 Basic Auth and constant-time SHA-256 digest comparison (`crypto.subtle`).
- [x] T007 [US2] Mirror `functions/_middleware.js` into `site/functions/_middleware.js` for seamless Cloudflare Pages bundle packaging.
- [x] T008 [US2] Support environment secrets `AUTH_USER` and `AUTH_PASS` with secure fallback logic.

## Phase 4: User Story 3 — Secret Management & Quality Verification (Priority: P2)

**Goal**: Validate zero secret leakage, ensure automated tests pass, and publish secured release.
**Independent Test**: Run `python -m unittest discover tests` and verify all tests pass with zero regressions.

- [x] T009 [US3] Add automated security test in `tests/test_auth_security.py` verifying no credentials leaked in tracked code or markdown files.
- [x] T010 [US3] Run full test suite: `python -m unittest discover tests` (all 29 tests pass).
- [ ] T011 [US3] Deploy secured bundle via `deploy_to_cloudflare.py` and synchronize to Git `origin main`.
