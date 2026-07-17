# NextHire AI beta readiness report

**Assessment date:** July 17, 2026  
**Decision:** Conditionally ready for a controlled, invitation-only, non-commercial beta. Not approved for production or paid launch.

## Verified release evidence

- `./scripts/verify_release.sh` passes with 170 backend tests.
- Alembic upgrades from an empty database to the current revision, reports no schema drift, downgrades to base, and upgrades again successfully.
- Frontend lint and the production build pass. Route-level code splitting keeps every generated JavaScript chunk below the build advisory threshold.
- Registration, authenticated login, profile creation, sign-out, and protected-route redirects were exercised through the local interface.
- A genuine PDF resume was analyzed and persisted with an 85% resume score and 80% ATS score.
- Job Match, Resume Tailor, and Cover Letter use the authenticated user's latest saved Resume Studio document instead of requiring duplicate resume input.
- Job Match returned a grounded 78% SRE match using saved resume and profile evidence.
- Worldwide job search returned 20 attributed listings from available providers. Missing provider credentials and provider failures degrade without failing the whole search.
- Himalayas location normalization accepts both object and string restriction payloads and ignores malformed entries without dropping the provider batch.
- Application creation, editing, status movement, archive filtering, deletion, and pipeline counters were exercised through the local interface.
- Account export returned successfully. The disposable beta account was deleted, its credentials stopped working, and database checks found no orphaned profile, document, revision, analysis, application, or AI-usage records.
- Automated coverage rejects unsupported, spoofed, oversized, and empty resume files.
- A combined two-account regression test verifies owner isolation for profiles, analyses, documents, revisions, applications, and AI-usage events.
- Slow AI analysis no longer blocks unrelated API requests. Extended Qwen thinking is disabled for concise product responses.

## Open beta checks

These items should be completed before inviting a wider tester group:

- Exercise registration email verification and password reset against the selected SMTP provider. Automated service coverage is not a substitute for delivery testing.
- Upload a genuine DOCX resume through the deployed interface.
- Download generated PDF and DOCX documents and visually inspect them.
- Edit a saved document and manually verify revision history and restore.
- Manually enter and persist an application follow-up reminder. Native date-time entry could not be completed reliably through browser automation.
- Exercise the Free-plan 429 response through the deployed interface and confirm a second account remains unaffected. Per-user accounting has automated coverage.
- Confirm the deployed AI timeout, retry, model, and capacity settings under concurrent beta usage. Local AI responses took roughly 12–30 seconds during smoke testing.

## Safe scope for invited testers

Invite a small, known group only. They may test profile management, PDF resume analysis, skill-gap analysis, job discovery, saved-resume job matching, resume tailoring, cover-letter generation, document history, application tracking, data export, and account deletion.

Use synthetic or non-sensitive resume data until production privacy operations and malware scanning are available. Tell testers that job listings come from identified third parties, must be verified on the provider site, and do not imply provider partnership or guaranteed employment outcomes.

Keep billing disabled. Do not market the service as production-ready, sell subscriptions, or promise continuous availability during this phase.

## External blockers to production

- Legal entity, launch jurisdictions, counsel-approved Terms and Privacy Notice, support/privacy contacts, subprocessors, accessibility review, retention, and international-transfer decisions.
- Written commercial-use review for every enabled job provider, including attribution, caching, rate limits, geography, and termination requirements.
- Managed production hosting, domain, PostgreSQL, SMTP, monitoring, alert routing, encrypted backups, secret management, incident ownership, and a completed restore drill.
- Approved AI-provider commercial and privacy terms, production capacity, cost limits, and concurrency behavior.
- Production resume malware scanning and isolated asynchronous document processing.
- Stripe account configuration, approved prices, tax/refund/cancellation policy, signed webhook validation, reconciliation, and support ownership before billing is enabled.

## Recommended next milestone

Complete the open beta checks in a deployed staging environment, record results here, and fix evidence-backed failures before adding new roadmap features. After that, invite a small cohort and measure activation, first successful resume analysis, first job search, first tracked application, seven-day return, core-flow failures, AI timeouts, provider availability, export/deletion completion, and support volume.
