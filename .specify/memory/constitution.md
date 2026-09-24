# B2C Analytics Dashboard & Partners: Constitution

## Core Principles

### I. Cloudflare Pages & Git Synchronization (NON-NEGOTIABLE)
Everything deployed to Cloudflare Pages MUST unconditionally and simultaneously be committed and pushed to Git (`origin main`). No production deployment may exist without corresponding Git version control.

### II. Historical Data Preservation (IMMUTABLE PAST)
All updates for the active month must strictly preserve closed historical months (`2026-01` through `2026-08`). Under no circumstances may historical dealer and deal volumes be overwritten or truncated.

### III. Security & Zero Secret Leakage (ABSOLUTE CONFIDENTIALITY)
No plaintext credentials, compensation details (salaries, monetary bonus grids), API tokens, or user passwords may ever be stored in tracked repository files, public documentation, or client-side assets. All secrets must reside exclusively in secure environment variables, Cloudflare Worker Secrets/Bindings, or local untracked configs (`config.local.json`).

### IV. Lead Analytics Integrity & No Double Counting
Transferred leads (`trans_leads`) are sourced exclusively from the transactional registry `sys_db_partners` (`Type === 'Лид'`). Merging or summing with geo-aggregates (`lead_geo_dealers`) is strictly prohibited to prevent data bloat and conversion distortion.

### V. Quality Gates & Regression Prevention
Before any deployment or release, all automated tests (24+) must pass cleanly (`python -m unittest discover tests`). No regression in KAM mappings, rooftop hierarchies, or data pipelines is permitted.

## Governance
This Constitution supersedes all ad-hoc instructions. Any architectural change requires an approved spec-kit artifact suite (`spec.md`, `plan.md`, `tasks.md`).

**Version**: 1.0.0 | **Ratified**: 2026-09-24 | **Last Amended**: 2026-09-24
