# Implementation Plan: Hide Auth Credentials & Secure Production Perimeter

**Branch**: `001-hide-auth-credentials` | **Date**: 2026-09-24 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `specs/001-hide-auth-credentials/spec.md`

## Summary
Implement edge-level authentication middleware for Cloudflare Pages (`functions/_middleware.js`), remove all hardcoded plain text credentials from `README.md` and repository files, and transition credential management to untracked local config (`config.local.json`) and Cloudflare Environment Secrets.

## Technical Context
- **Language / Runtime**: JavaScript (Cloudflare Pages Functions / V8 Worker runtime), Python 3.11 (deployment & test pipelines).
- **Core Technology**: Cloudflare Pages Functions (`functions/_middleware.js`), Web Cryptography API (`crypto.subtle`), HTTP Basic Authentication (RFC 7617).
- **Secrets Management**: Untracked `config.local.json` (git-ignored) & Cloudflare Environment Secrets (`AUTH_USER`, `AUTH_PASS`).
- **Testing**: Python unittest (`tests/test_auth_security.py`), local Node.js edge middleware simulation tests.
- **Constraints**: No latency degradation (< 50ms at edge), zero plain text credentials in Git, full backward compatibility with auto-deploy.

## Constitution Check
- [x] Principle I (Cloudflare & Git Sync): Deployment and Git commits remain 100% synchronized via `deploy_to_cloudflare.py`.
- [x] Principle II (Historical Preservation): No data files or historical deals are touched.
- [x] Principle III (Security & Zero Secret Leakage): Directly eliminates plaintext credentials from version control.
- [x] Principle IV (Lead Analytics Integrity): Does not modify lead calculations.
- [x] Principle V (Quality Gates): Requires new automated security tests + all 24 existing tests passing.

## Architecture & Blueprint

### 1. Cloudflare Pages Perimeter Protection (`functions/_middleware.js`)
Cloudflare Pages deploys serverless functions located in the `functions/` directory. By implementing `functions/_middleware.js`, every incoming HTTP request to `dashbord-partners1.pages.dev` (including HTML, JS, JSON data files, and assets) passes through this middleware before static delivery:
- Extract `Authorization` header.
- Decode `Basic <base64>` credentials safely.
- Compare username and password against configured secrets using constant-time SHA-256 digest comparison:
  ```javascript
  async function timingSafeEqual(a, b) {
    const enc = new TextEncoder();
    const hashA = await crypto.subtle.digest('SHA-256', enc.encode(a));
    const hashB = await crypto.subtle.digest('SHA-256', enc.encode(b));
    const bufA = new Uint8Array(hashA);
    const bufB = new Uint8Array(hashB);
    if (bufA.length !== bufB.length) return false;
    let diff = 0;
    for (let i = 0; i < bufA.length; i++) diff |= bufA[i] ^ bufB[i];
    return diff === 0;
  }
  ```
- If unauthenticated: return `401 Unauthorized` with header `WWW-Authenticate: Basic realm="B2C Analytics Dashboard"`.
- If authenticated: proceed via `context.next()`.

### 2. Sanitizing Repository Documentation & Scripts
- **`README.md`**: Replace `Basic Auth: director / password` with generic instruction: `Доступ защищён авторизацией (выдаётся администратором проекта)`.
- **`deploy_to_cloudflare.py`**: Mask the sensitive URLs or outputs; avoid announcing open unauthenticated links.
- **`scratch/deploy_worker_with_kv.py`**: Pull credentials dynamically from `config.local.json` or `env` instead of hardcoding literals.

### 3. Local Untracked Configuration (`config.local.json`)
Support `auth_user` and `auth_pass` in `config.local.json` for deployment automation, which is strictly in `.gitignore`.

### 4. Automated Verification (`tests/test_auth_security.py`)
Add automated tests verifying:
- No plain text passwords exist in tracked `.md`, `.js`, `.py`, `.html` files.
- `functions/_middleware.js` correctly enforces 401 when unauthenticated.
- `functions/_middleware.js` verifies valid credentials.

## Complexity Tracking
*No constitution violations. Minimal complexity using Cloudflare standard Pages Functions.*
