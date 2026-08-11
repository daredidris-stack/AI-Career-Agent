# NextHire AI beta readiness report

**Assessment date:** July 17, 2026  
**Decision:** Conditionally ready for a controlled, invitation-only, non-commercial beta. Not approved for production or paid launch.

## Verified release evidence

- `./scripts/verify_release.sh` passes with 356 backend tests as of the August
  11 email-evidence and ClamAV deployment-preparation update.
- Commit `95c759f` was deployed from `codex/complete-user-facing-workflows` to
  an isolated Railway environment on August 2. Both application services and
  PostgreSQL reached Online; `/health/live` and `/health/ready` returned 200
  with release `95c759f` and a healthy production-database check.
- The temporary deployment completed registration, authenticated login,
  onboarding, profile creation, populated Help Center rendering, and support
  request persistence through the deployed interface. Its frontend and CORS
  URLs were isolated to staging, while saved-search email and malware scanning
  were explicitly disabled.
- The staging environment and its disposable data were deleted immediately
  after verification. Railway then showed the production API, PostgreSQL, and
  frontend services still Online; no production configuration was changed.
- Alembic upgrades from an empty database to the current revision, reports no schema drift, downgrades to base, and upgrades again successfully.
- Frontend lint and the production build pass. Route-level code splitting keeps every generated JavaScript chunk below the build advisory threshold.
- Authenticated navigation adapts to mobile widths with an accessible slide-out menu, compact header controls, responsive content padding, and a viewport-bounded account menu.
- Registration, authenticated login, profile creation, sign-out, and protected-route redirects were exercised through the local interface.
- A genuine PDF resume was analyzed and persisted with an 85% resume score and 80% ATS score.
- A render-verified genuine DOCX resume was uploaded through the interface, analyzed, and persisted with an 85% resume score and 80% ATS score.
- Authenticated PDF and DOCX document export requests completed successfully. Both one-page exports were rendered and visually inspected with no clipping, overlap, broken glyphs, or missing sections.
- A saved document was edited, its revision appeared in history, and restoring that revision recovered the original title and content.
- Document history can compare an earlier revision with the current version
  before restore.
- Job Match, Resume Tailor, and Cover Letter use the authenticated user's latest saved Resume Studio document instead of requiring duplicate resume input.
- Job Match returned a grounded 78% SRE match using saved resume and profile evidence.
- Worldwide job search returned 20 attributed listings from available providers. Missing provider credentials and provider failures degrade without failing the whole search.
- Himalayas location normalization accepts both object and string restriction payloads and ignores malformed entries without dropping the provider batch.
- Application creation, editing, status movement, archive filtering, deletion, and pipeline counters were exercised through the local interface.
- Application Tracker includes a monthly deadline, follow-up, and applied-date
  calendar.
- Saved jobs and saved searches are owner-scoped, and rerunning a saved search
  produces in-app alerts for previously unseen matches.
- Saved-search email alerts are separately gated at deployment and per search,
  require a verified account email, establish a no-email first-run baseline,
  record delivery status, retry without hiding unsent matches, and provide a
  signed public unsubscribe confirmation page. The scheduled worker exits
  after one bounded batch.
- On August 11, the Railway production API and hourly worker completed the
  Brevo activation sequence: disabled safe run, no-email first-run baseline,
  one delivered new-match email, GET-safe and POST-confirmed unsubscribe, and
  re-enablement with the next daily run scheduled. Automatic alerts are now
  complete for the controlled beta; a custom authenticated sender domain and
  ongoing deliverability monitoring remain public-launch gates.
- Help feedback creates owner-scoped support requests. Administrator operations
  routes require a configured email allowlist and expose aggregate status rather
  than secrets.
- Administrator support changes create append-only audit events with actor,
  target, request ID, status transition, and note-presence metadata. Application
  guards and database triggers reject update and deletion attempts, and the
  audit history never copies ticket or internal-note text.
- Registration retry behavior was exercised after a duplicate-account error;
  the stale error cleared before the successful state and password input was
  cleared.
- Interview practice attempts are owner-scoped and use a transparent
  structure/evidence rubric that is explicitly not a technical-correctness or
  hiring-likelihood score.
- Apply Assistant provides copyable factual profile fields while retaining
  manual employer-form completion and final submission.
- Account export returned successfully. The disposable beta account was deleted, its credentials stopped working, and database checks found no orphaned profile, document, revision, analysis, application, or AI-usage records.
- Automated coverage rejects unsupported, spoofed, oversized, and empty resume files.
- Optional ClamAV scanning now runs before PDF/DOCX parsing for every upload
  workflow. Detection is generic, scanner failures return 503, and local
  behavior remains disabled by default until a private deployed scanner passes
  the staged activation test.
- PDF/DOCX parsing now runs in a fresh asynchronously awaited subprocess with a
  secret-free environment, CPU/file/output/wall-time bounds, a Linux memory
  bound, cancellation cleanup, and no in-process fallback. Genuine PDF and
  DOCX subprocess tests pass; platform-level sandboxing remains a deployed
  staging check.
- A combined two-account regression test verifies owner isolation for profiles, analyses, documents, revisions, applications, and AI-usage events.
- Slow AI analysis no longer blocks unrelated API requests. Extended Qwen thinking is disabled for concise product responses.

## Open beta checks

These items should be completed before inviting a wider tester group. The
production Brevo sender, saved-search alert, unsubscribe, and Railway
scheduled-worker activation paths have passed:

- Exercise registration email verification and password reset against the
  production Brevo sender. The transactional channel is live, but the release
  handoff does not yet contain separate end-to-end evidence for both auth
  messages.
- Manually enter and persist an application follow-up reminder. Native date-time entry could not be completed reliably through browser automation.
- Exercise the Free-plan 429 response through the deployed interface and confirm a second account remains unaffected. Per-user accounting has automated coverage.
- Confirm the deployed AI timeout, retry, model, and capacity settings under concurrent beta usage. Local AI responses took roughly 12–30 seconds during smoke testing.

## Safe scope for invited testers

Invite a small, known group only. They may test profile management, PDF resume
analysis, skill-gap analysis, job discovery, saved jobs and searches,
saved-resume job matching, resume tailoring, cover-letter generation, document
comparison/history, interview practice scoring, application preparation and
calendar tracking, Help feedback, data export, and account deletion.

Use synthetic or non-sensitive resume data until production privacy operations and malware scanning are available. Tell testers that job listings come from identified third parties, must be verified on the provider site, and do not imply provider partnership or guaranteed employment outcomes.

Keep billing disabled. Do not market the service as production-ready, sell subscriptions, or promise continuous availability during this phase.

## External blockers to production

- Legal entity, launch jurisdictions, counsel-approved Terms and Privacy Notice, support/privacy contacts, subprocessors, accessibility review, retention, and international-transfer decisions.
- Written commercial-use review for every enabled job provider, including attribution, caching, rate limits, geography, and termination requirements.
- Custom production domain and authenticated email-sender domain, monitoring,
  alert routing, encrypted backups, secret management, incident ownership, and
  a completed restore drill. Railway hosting, PostgreSQL, Brevo delivery, and
  the scheduled alert worker are active for the controlled beta.
- Approved AI-provider commercial and privacy terms, production capacity, cost limits, and concurrency behavior.
- Deployed ClamAV capacity/signature monitoring plus platform-level egress,
  filesystem, process, and resource hardening for the isolated parser. The
  fail-closed scanner and subprocess integrations are complete but not yet
  proven in deployed staging.
- Stripe account configuration, approved prices, tax/refund/cancellation policy, signed webhook validation, reconciliation, and support ownership before billing is enabled.

## Recommended next milestone

Complete the remaining integration-specific staging checks: private ClamAV
scanning and outage behavior, hardened parser isolation, backup/restore,
registration/password email delivery, monitoring/alert routing, and concurrent
AI capacity. Fix any
evidence-backed failures before inviting a small cohort, then measure
activation, first successful resume analysis, first job search, first tracked
application, seven-day return, core-flow failures, AI timeouts, provider
availability, export/deletion completion, and support volume.
