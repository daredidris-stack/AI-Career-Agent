# Beta release checklist

This checklist is a release gate. A beta is ready only when every required engineering item passes and every external decision is either approved or the affected feature remains disabled.

## Automated release gate

Run from the repository root:

```bash
./scripts/verify_release.sh
```

The command runs all backend tests with resource warnings enforced, validates a complete migration upgrade/downgrade cycle with no schema drift, runs frontend lint and the production build, and checks the Git diff for whitespace errors. GitHub Actions runs the backend and frontend gates on every pull request and push to `main`.

## Required beta smoke test

- Register with accepted Terms and Privacy Notice, verify email, sign in, sign out, reset password, and confirm protected-route redirects.
- Create and edit a profile, then export account data.
- Upload genuine PDF and DOCX resumes; confirm oversized, empty, spoofed, and unsupported files fail safely.
- Analyze a resume and verify persisted scores, skills, document history, PDF/DOCX export, and revision restore.
- Run skill-gap, job search, job match, resume tailor, and cover-letter flows using the authenticated profile and resume evidence.
- Verify job-source attribution and provider failure handling.
- Create, edit, move, follow up, archive, and delete an application.
- Confirm dashboard resume/ATS history, application pipeline, document counts, and AI usage.
- Confirm Free AI limits return a clear 429 response and do not affect another account.
- Delete a test account and verify its profile, documents, revisions, analyses, applications, usage events, and subscription state are gone.
- Run two-account isolation tests against every owner-scoped resource.

## Production gate

- Managed PostgreSQL provisioned; migration and restore drill completed.
- Unique production JWT secret, exact HTTPS CORS origins, SMTP, monitoring, and encrypted backups configured.
- Health checks, structured logs, alert routing, incident owner, status communication, and rollback owner confirmed.
- AI provider capacity, privacy terms, retention, prompt limits, model version, fallback behavior, and cost limits approved.
- Every active job provider reviewed for commercial use, attribution, caching, rate limits, links, geography, and termination requirements.
- Legal entity, launch jurisdictions, Terms, Privacy Notice, subprocessors, retention, transfer mechanisms, consumer disclosures, accessibility, and support contact approved.
- If billing is enabled: approved Stripe price/tax/refund terms, signed webhooks, test-mode scenarios, reconciliation, and support procedures completed. Otherwise Stripe variables remain unset and Pro remains disabled.

## Rollback

Keep the prior API and frontend image tags. If a release fails, stop traffic to the new API, preserve logs and request IDs, restore the prior application images, and prefer a corrective forward migration. Restore a database only for confirmed data corruption and only from a verified backup, then reapply deletion requests made after that backup.

## Beta success criteria

Track activation (profile plus first resume analysis), first job search, first tracked application, seven-day return, core-flow success rate, API error rate, AI timeout rate, job-provider availability, support volume, and deletion/export completion. Do not include resume or profile content in product analytics.
