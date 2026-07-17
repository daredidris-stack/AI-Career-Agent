# Product and operational analytics

The dashboard uses first-party records already required to deliver the product. It reports resume and ATS score history, document counts, application-pipeline stages, and the authenticated user’s AI request count for the last 30 days. It does not add third-party tracking scripts, cookies, resume content, profile content, or job descriptions to analytics.

Operational monitoring uses structured API logs, health endpoints, database metrics, migration status, AI timeout rates, provider availability, and Stripe webhook delivery. Central dashboards should show latency and error rates by route, readiness, job-source success, AI capacity, subscription webhook failures, and database health without exposing customer payloads.

Before adding a third-party analytics product, complete privacy and cookie review, configure data minimization and regional controls, document the vendor as a subprocessor, and obtain consent where required. Never send access tokens, emails, resume text, document text, job descriptions, or free-form profile fields as analytics properties.

Recommended beta funnel definitions:

1. Account created and email verified.
2. Profile completed.
3. First resume analyzed.
4. First job search completed.
5. First application tracked.
6. Resume tailored or cover letter generated.
7. User returns within seven days.

Aggregate business reporting should be built from privacy-reviewed, pseudonymous events with documented definitions. Admin-wide reporting is intentionally not exposed through customer API routes until an administrator authorization model and audit logging are implemented.
