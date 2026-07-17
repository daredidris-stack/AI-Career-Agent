# NextHire AI roadmap handoff

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
