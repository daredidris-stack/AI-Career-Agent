# NextHire AI roadmap handoff

## Project 1 continuation snapshot — July 26, 2026

This continuation began from `main` at `0418879` with an intentionally
uncommitted feature batch. The five feature groups are now separated into
auditable commits, and the complete implementation passes the automated
release gate:

- 290 backend tests pass with `ResourceWarning` treated as an error.
- Alembic upgrades an empty database through `20260728_0007`, reports no
  schema drift, downgrades to base, and upgrades to head again.
- Frontend lint and the production Vite build pass.
- `git diff --check` passes.

The Alembic blocker was that `migrations/env.py` loads model metadata through
`backend.models`, but `JobListing` and `JobSyncState` were not imported by that
package. `backend/models/__init__.py` now imports and exports both models. This
verifies the repository implementation. Credentialed production services and
the deployment-specific checks listed below remain separate release gates.

### Completed feature batch

The original dirty worktree was reviewed and separated into these bounded
groups:

1. **Login protection and Google identity — code verified**
   - Google ID-token verification, account linking, login UI, Turnstile
     verification, and migration `20260720_0005`.
   - 36 focused auth tests pass. An independently reconstructed staged
     snapshot passes 203 backend tests, its complete Alembic cycle with no
     drift, and frontend lint/build. The combined worktree passes the full
     282-test release gate.
   - Google client IDs are configured on both sides and match. A local browser
     smoke test rendered Google sign-in, exercised the password-login error
     path against the API, and found no browser console errors.
   - Google auto-linking is limited to authoritative Gmail/Workspace
     identities. Turnstile rejects published dummy secrets in production and
     fails closed without an allowed hostname.
   - Live Turnstile remains a deployment check because no local site key,
     secret, or hostname allowlist is currently configured.
2. **Profile intake and resume cleanup — code and browser verified**
   - Resume-driven profile autofill, normalized target-role suggestions, and
     removal of markdown/template artifacts from uploaded resume text.
   - 27 focused route, service, resume-reader, and cleanup tests pass. An
     independently reconstructed staged snapshot passes 219 backend tests, its
     complete Alembic cycle with no drift, frontend lint/build, and the staged
     diff whitespace check.
   - An authenticated local browser smoke test completed real PDF and DOCX
     uploads against `qwen3:8b`. Both requests returned 200, empty profile
     fields were populated, a manually entered current role was preserved,
     target-role choices updated the form, and reloading confirmed that autofill
     does not save before the user presses the profile save button.
3. **ATS resume templates and deterministic Word export — code and render verified**
   - Three bundled templates, catalog/selection service, structured tailoring,
     export rendering, and the Resume Tailor/Document Library UI changes.
   - 23 focused template, tailoring, route, and export tests pass. An
     independently reconstructed staged snapshot passes 229 backend tests, its
     complete Alembic cycle with no drift, frontend lint/build, and the staged
     diff whitespace check.
   - Representative one-page exports were generated through the production
     export service for ATS Professional, ATS Modern, and ATS Classic. Every
     rendered page was inspected at full resolution and showed clean margins,
     typography, bullets, section flow, and page boundaries with no clipping,
     overlap, missing glyphs, placeholders, or broken layout.
   - Regenerating the three source templates produced identical unpacked OOXML
     package contents; only ZIP container metadata differed.
4. **Worldwide provider and job-detail expansion — code and bounded live verified**
   - Adzuna multi-market search, Jooble updates, TheirStack, SerpApi,
     Fantastic.jobs, USAJOBS, direct ATS feeds, direct employer feeds,
     job-title expansion, provider status reporting, and description
   enrichment.
   - 59 focused adapter, aggregation, route, search-service, and description
     tests pass. Provider failures are isolated and credential-bearing request
     errors are replaced with generic messages.
   - An independently reconstructed staged snapshot passes 264 backend tests,
     its complete Alembic cycle through `20260720_0005` with no schema drift,
     and frontend lint/build. The combined worktree passes the 282-test release
     gate through migration `20260721_0006`.
   - A bounded live Worldwide search returned one job, direct listing URL, and
     description from each of Adzuna, Jooble, TheirStack, and Fantastic.jobs.
     SerpApi completed successfully with `no_results`, not `unavailable`.
     USAJOBS and the Greenhouse, Lever, Ashby, Microsoft, Apple, and Crossover
     sources correctly reported `not_configured`.
   - A separate live Amazon Jobs lookup returned a complete description through
     the authenticated in-app enrichment route.
   - Provider attribution and the final “Continue to listing on [provider]”
     action remain in the job-details dialog. Adzuna cards and details render
     the required “Jobs by Adzuna” logo treatment.
   - Commercial-use approval remains an external deployment gate; details are
     recorded in the provider release review below.
5. **Persistent job catalog and ingestion — code, migration, and isolated live worker verified**
   - `JobListing`/`JobSyncState`, repository, migration `20260721_0006`,
     ingestion service, sync worker, cached-search integration, retention, and
     the optional Compose worker.
   - 31 focused repository, ingestion, worker, search, and profile-target tests
     pass. An independently reconstructed staged snapshot passes 282 backend
     tests, its complete Alembic cycle through `20260721_0006` with no schema
     drift, frontend lint/build, and the staged diff whitespace check.
   - A bounded one-shot Fantastic.jobs sync against an isolated, freshly
     migrated SQLite database fetched and stored one listing and recorded a
     successful sync state. Cached search then returned that stored listing.
     A second watch-mode cycle skipped the target according to its next-run
     schedule without another provider request, and the worker stopped cleanly
     on interruption.
   - Tests verify five-minute failure retry scheduling, generic persisted/logged
     errors that do not expose provider credentials, stale and expired listing
     exclusion, retention deactivation, safe listing URLs, normalized UTC
     timestamps, duplicate-target suppression, cached provider status, and
     live-search fallback when the cache is unavailable.
   - The Compose definition gates the worker on API and database health. A
     complete isolated local Compose verification now passes as recorded below;
     deployed staging observation remains a separate release check.

### Post-merge PostgreSQL verification — July 27, 2026

- PostgreSQL 16.14 was installed and an isolated, empty, loopback-only cluster
  was created for engine-specific release verification. Because the cluster
  contained no prior data, no backup was required; the temporary runtime and
  data directory were removed after the checks.
- The complete Alembic chain upgraded successfully through `20260721_0006`
  using PostgreSQL transactional DDL. `alembic check` reported no schema drift,
  and `alembic current` reported `20260721_0006 (head)`.
- The API started against PostgreSQL, and both `/health/live` and
  `/health/ready` returned HTTP 200 with `ok` and `ready` status payloads.
- A bounded Fantastic.jobs synchronization fetched one result, created one
  active `job_listings` row, and recorded one successful `job_sync_states` row
  with a future next-sync time and no error. Repository search returned the
  stored listing with its cached marker and listing URL.
- A second one-shot cycle and the watch worker both skipped the target according
  to its persisted schedule, with no additional provider result fetched.
- This closes the local PostgreSQL engine-validation gap. It does not replace a
  migration, backup, health, and long-running worker observation in the actual
  deployed staging environment.

### Local Docker Compose verification — July 28, 2026

- Docker Desktop 29.6.2 and Docker Compose 5.3.1 built and started the isolated
  `nexthireverify` project without changing the already-running IncidentPilot
  services. A temporary override exposed the API on loopback port 18080 and the
  frontend on loopback port 15173.
- The PostgreSQL 17, API, frontend, and optional ingestion-worker containers all
  started. PostgreSQL and API health checks passed before the worker started.
  The frontend build context was reduced to 320.48 kB by adding
  `frontend/.dockerignore`; the backend context was 2.42 MB.
- Inside the API container, `alembic current` reported
  `20260721_0006 (head)` and `alembic check` reported no new upgrade operations.
  `/health/live` and `/health/ready` returned HTTP 200 with `ok` and `ready`,
  and the frontend returned HTTP 200.
- A browser smoke test followed the protected-route redirect to `/login`,
  rendered the complete email/password sign-in form, and found no browser
  console errors.
- The worker ran with one bounded Fantastic.jobs target and a one-result cap.
  The provider returned HTTP 403 because the account's Jobs meter had exceeded
  its allowed limit. The worker isolated the failure, stored only the generic
  `Job ingestion failed.` message, scheduled a retry, skipped the not-yet-due
  target on a later poll, and did not expose the configured credential in its
  logs. Successful Compose ingestion remains blocked on renewed provider quota;
  the earlier isolated PostgreSQL verification proves the successful
  persistence path.
- `npm audit --omit=dev` reports two high-severity entries for the same
  React Router advisory in 7.18.1. The reviewed advisory states that it only
  affects unstable React Server Components APIs; this client-rendered
  `BrowserRouter` application imports none of those APIs. The registry's current
  `react-router-dom` release remains 7.18.1, while the advisory names 8.3.0 as
  patched. Monitor the package for a compatible patched release rather than
  downgrading to older versions with broader known advisories.
- After these Compose and build-context changes, `./scripts/verify_release.sh`
  passed all 282 backend tests, the complete Alembic upgrade/check/downgrade/
  re-upgrade cycle, frontend lint, the production frontend build, and the diff
  whitespace check.

### Apply Assistant foundation — July 28, 2026

- Migration `20260728_0007` adds owner-scoped resume and cover-letter
  references, provider metadata, and a reviewed-package timestamp to tracked
  applications.
- `POST /applications/prepare` requires two explicit confirmations, validates
  that the selected documents belong to the authenticated user and have the
  expected kinds, accepts only credential-free HTTPS application links, and
  records the package as `preparing`.
- Repeated preparation for the same job URL updates the existing application
  rather than creating duplicates. Already-applied, interview, offer, rejected,
  or archived statuses are never downgraded to `preparing`.
- The Jobs dialog now lets users select and download a saved resume and optional
  cover letter. The provider link appears only after the reviewed package is
  stored. The Application Tracker shows the selected document names and makes
  clear that NextHire has not submitted the employer form.
- An isolated authenticated browser test searched a seeded SQL-backed job,
  verified the action remained disabled until both confirmations were checked,
  saved the tailored resume and cover letter, exposed the correctly labeled
  provider link, and found one reviewed `preparing` application in the tracker.
  No browser console errors were recorded.
- The full release gate passes 290 backend tests, migration upgrade through
  `20260728_0007`, no schema drift, downgrade and re-upgrade, frontend lint,
  the production build, and the diff whitespace check.
- An empty ephemeral PostgreSQL 17 database also upgraded through
  `20260728_0007`, reported no schema drift, downgraded to base, and re-upgraded
  to head. Its temporary container and data were removed after verification.
- This is intentionally assisted apply, not a browser bot. It does not answer
  sensitive employer questions, bypass CAPTCHA or account security, or submit
  to external platforms. Direct ATS submission remains future work only where
  the employer provides credentials and written authorization.

### Recommended continuation order

Groups 1 through 5 are complete and separately auditable. Retain live Turnstile,
provider commercial approval and quota, and deployed staging checks as
deployment gates. Turnstile cannot be tested live in this workspace because its
backend secret, hostname allowlist, and frontend site key are not configured.
Next, perform the remaining production credential, deployment, and
launch-readiness checks. Do not replace the July 17 beta assessment with this
engineering snapshot; its manual smoke-test evidence and external launch
blockers remain separate.

### Provider release review — July 26, 2026

- **Adzuna:** Worldwide search fans out across eight configured markets, so one
  user search can consume eight API requests. The default limits are 25
  requests/minute, 250/day, 1,000/week, and 2,500/month. Commercial evaluation
  is limited to 14 days unless Adzuna grants written consent or a licence.
  Production remains blocked on that approval and confirmation of the final
  logo asset. See the [Adzuna API terms](https://developer.adzuna.com/docs/terms_of_service).
- **Jooble:** The registered REST API is expressly designed to display Jooble
  search results in a site’s own UI, but the public documentation does not
  publish a quota or clearly grant this product’s ongoing commercial use.
  Confirm both with Jooble for the registered key before production. See the
  [Jooble REST API documentation](https://help.jooble.org/en/support/solutions/articles/60001448238-rest-api-documentation).
- **TheirStack:** Each returned job costs one API credit, including repeated
  requests. The adapter caps free-plan pages at 25 results; the free plan
  includes 200 API credits/month and has additional per-second, per-minute,
  hourly, and daily limits. Confirm that the selected subscription and licence
  permit the intended display and retention. See [credits](https://theirstack.com/en/docs/pricing/credits),
  [plans](https://theirstack.com/en/docs/pricing/plans), and
  [terms](https://theirstack.com/en/docs/legal/terms-and-conditions).
- **SerpApi:** One successful Google Jobs request consumes one search regardless
  of result count; up to ten jobs are returned per page and identical cached
  requests are free. The current free plan includes 250 searches/month. See the
  [Google Jobs API](https://serpapi.com/google-jobs-api) and
  [current pricing](https://serpapi.com/pricing).
- **Fantastic.jobs:** Active ATS responses consume one Jobs credit per returned
  record. The adapter caps responses at 20 and caches identical searches for 15
  minutes. The configured account returned `Jobs` meter quota exhaustion during
  the July 28 Compose verification. Production requires renewed quota plus an
  account plan and licence matching expected display, retention, and request
  volume. See the
  [endpoint documentation](https://developer.fantastic.jobs/documentation/endpoints/new-jobs).
- **USAJOBS:** API data is restricted to the requesting company and purpose on
  the registration form; other use requires prior written approval. Keep it
  disabled until a NextHire-specific key and approval exist. See the
  [USAJOBS terms](https://developer.usajobs.gov/guides/).
- **Employer ATS feeds:** Greenhouse GET job-board data is public, and Lever and
  Ashby document their postings feeds for organization career sites. Keep board
  identifiers empty until the relevant employer or account owner has approved
  aggregation. Microsoft, Apple, and Crossover use undocumented public
  career-site interfaces and are disabled unless explicitly opted in with
  `DIRECT_EMPLOYER_JOB_SOURCES`.

## Completed engineering foundation

- Authenticated profile, dashboard, career analytics, Resume Studio, document
  history/export, job search/matching, skill gap, tailoring, cover letters,
  reviewed application packages, and application tracking.
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
- Deployed staging PostgreSQL backup and migration plus extended
  ingestion-worker observation. The isolated local Compose path is verified,
  but it does not replace deployment-specific evidence.
- AI provider commercial/privacy approval and production capacity.
- Stripe account, approved product price, tax/refund/cancellation policy, webhook secret, live-mode testing, and reconciliation ownership.
- Malware scanning service for production resume uploads.

Until those items are resolved, run a controlled non-commercial beta, keep billing disabled, limit invited users, and avoid claims of provider partnership or guaranteed employment outcomes.

## Recommended next product work after beta evidence

1. Fix issues discovered in the controlled beta before expanding scope.
2. Add administrator authorization and audited aggregate operations reporting.
3. Add malware scanning and isolated asynchronous document processing.
4. Evaluate direct ATS application submission only through employer-authorized
   APIs with per-application consent, submission receipts, idempotency, and
   audit logs; do not automate restricted job platforms.
5. Add saved job alerts and application follow-up notifications after email deliverability is proven.
6. Validate mobile navigation with beta users and address evidence-backed usability issues. Route-level code splitting is implemented and the production build has no large-bundle advisory.
7. Select further Resume Studio, interview, or learning features based on measured activation and retention rather than assumptions.
