# NextHire AI roadmap handoff

## Project 1 continuation snapshot — July 26, 2026

This continuation began from `main` at `0418879` with an intentionally
uncommitted feature batch. The combined worktree passes the complete automated
release gate:

- 272 backend tests pass with `ResourceWarning` treated as an error.
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
   272-test release gate.
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
     and frontend lint/build. The combined worktree passes the 272-test release
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

Groups 1 through 4 are complete; retain the live Turnstile and provider
commercial-approval checks as deployment gates. Continue with group 5, then
run its targeted tests before `./scripts/verify_release.sh`.
After the five code groups are separately auditable, perform the remaining
credentialed, browser, document-render, provider, and staging-worker checks and
record their evidence here. Do not replace the July 17 beta assessment with
this automated snapshot; its manual smoke-test evidence and external launch
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
  minutes. Production requires an account plan and licence matching expected
  display, retention, and request volume. See the
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
