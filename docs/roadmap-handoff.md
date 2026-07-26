# NextHire AI roadmap handoff

## Project 1 continuation snapshot — July 26, 2026

This continuation began from `main` at `0418879` with an intentionally
uncommitted feature batch. The combined worktree passes the complete automated
release gate:

- 267 backend tests pass with `ResourceWarning` treated as an error.
- Alembic upgrades an empty database through `20260721_0006`, reports no
  schema drift, downgrades to base, and upgrades to head again.
- Frontend lint and the production Vite build pass.
- `git diff --check` passes.

The Alembic blocker was that `migrations/env.py` loads model metadata through
`backend.models`, but `JobListing` and `JobSyncState` were not imported by that
package. `backend/models/__init__.py` now imports and exports both models. This
verifies the current combined worktree; it does not mean the uncommitted
features have been individually reviewed, committed, or exercised with
production credentials.

### Unfinished feature batch

Finish and review the dirty worktree in these bounded groups. Shared integration
files such as `.env.example`, `README.md`, `backend/core/settings.py`,
`backend/dependencies/services.py`, `frontend/src/services/api.ts`, and
`docker-compose.yml` should be staged by hunk with the feature they support.

1. **Login protection and Google identity — code verified**
   - Google ID-token verification, account linking, login UI, Turnstile
     verification, and migration `20260720_0005`.
   - 36 focused auth tests pass. An independently reconstructed staged
     snapshot passes 203 backend tests, its complete Alembic cycle with no
     drift, and frontend lint/build. The combined worktree passes the full
     267-test release gate.
   - Google client IDs are configured on both sides and match. A local browser
     smoke test rendered Google sign-in, exercised the password-login error
     path against the API, and found no browser console errors.
   - Google auto-linking is limited to authoritative Gmail/Workspace
     identities. Turnstile rejects published dummy secrets in production and
     fails closed without an allowed hostname.
   - Live Turnstile remains a deployment check because no local site key,
     secret, or hostname allowlist is currently configured.
2. **Profile intake and resume cleanup**
   - Resume-driven profile autofill, normalized target-role suggestions, and
     removal of markdown/template artifacts from uploaded resume text.
   - Automated service and route coverage passes.
   - Still requires browser testing with representative PDF and DOCX resumes.
3. **ATS resume templates and deterministic Word export**
   - Three bundled templates, catalog/selection service, structured tailoring,
     export rendering, and the Resume Tailor/Document Library UI changes.
   - Automated template, tailoring, and export coverage passes.
   - Still requires render inspection of representative exports from every
     template before calling the visual output release-ready.
4. **Worldwide provider and job-detail expansion**
   - Adzuna multi-market search, Jooble updates, TheirStack, SerpApi,
     Fantastic.jobs, USAJOBS, direct ATS feeds, direct employer feeds,
     job-title expansion, provider status reporting, and description
     enrichment.
   - Adapter, aggregation, route, and search-service coverage passes.
   - Still requires live configured-provider checks, result-count/status
     recording, cost/rate-limit review, and commercial-use approval.
5. **Persistent job catalog and ingestion**
   - `JobListing`/`JobSyncState`, repository, migration `20260721_0006`,
     ingestion service, sync worker, cached-search integration, retention, and
     the optional Compose worker.
   - Repository, ingestion, search, full migration-cycle, and schema-drift
     coverage passes.
   - Still requires a staging PostgreSQL migration, one-shot sync, scheduled
     worker observation, retry observation, and stale-listing retention check.

The untracked zero-byte file `env` is not referenced by the application or
tests. Keep it out of feature commits unless its purpose is clarified.

### Recommended continuation order

Group 1 is complete in code; retain its live Turnstile check as a deployment
gate. Continue with group 2, then review and commit one group at a time in the
order above, running its targeted tests before `./scripts/verify_release.sh`.
After the five code groups are separately auditable, perform the remaining
credentialed, browser, document-render, provider, and staging-worker checks and
record their evidence here. Do not replace the July 17 beta assessment with
this automated snapshot; its manual smoke-test evidence and external launch
blockers remain separate.

## Completed engineering foundation

- Authenticated profile, dashboard, career analytics, Resume Studio, document history/export, job search/matching, skill gap, tailoring, cover letters, and application tracking.
- Multi-provider job aggregation with filtering, pagination, deduplication, graceful provider failures, source attribution, and profile/resume-aware ranking.
- Registration, login protection, email verification, password recovery, token revocation, account deletion, versioned legal consent, and protected routes.
- PostgreSQL support, Alembic migrations, backup/restore guidance, tested schema upgrade/downgrade, deployment containers, health endpoints, request IDs, structured logs, and CI.
- AI timeouts, retries, structured-output requests, prompt caps, durable per-user Free/Pro allowances, and graceful ranking fallbacks.
- Owner-scoped persistence, secure upload limits/signature checks, complete data export, deletion coverage, and isolation tests.
- Stripe checkout, portal, signed subscription webhooks, entitlement state, and disabled-until-configured paid plans.
- Privacy-conscious dashboard analytics and commercial/legal operational checklists.

## External launch blockers

These cannot be completed honestly through repository code alone:

- Operating company identity, launch markets, counsel-approved legal documents, support/privacy contact, subprocessors, and jurisdiction-specific compliance.
- Written approval of each job provider’s commercial use and attribution requirements.
- Production hosting, domain, PostgreSQL, SMTP, monitoring, backup storage, secret manager, incident contacts, and restore drill.
- AI provider commercial/privacy approval and production capacity.
- Stripe account, approved product price, tax/refund/cancellation policy, webhook secret, live-mode testing, and reconciliation ownership.
- Malware scanning service for production resume uploads.

Until those items are resolved, run a controlled non-commercial beta, keep billing disabled, limit invited users, and avoid claims of provider partnership or guaranteed employment outcomes.

## Recommended next product work after beta evidence

1. Fix issues discovered in the controlled beta before expanding scope.
2. Add administrator authorization and audited aggregate operations reporting.
3. Add malware scanning and isolated asynchronous document processing.
4. Add saved job alerts and application follow-up notifications after email deliverability is proven.
5. Validate mobile navigation with beta users and address evidence-backed usability issues. Route-level code splitting is implemented and the production build has no large-bundle advisory.
6. Select further Resume Studio, interview, or learning features based on measured activation and retention rather than assumptions.
