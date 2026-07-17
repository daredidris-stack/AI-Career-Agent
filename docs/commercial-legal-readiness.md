# Commercial legal readiness

The repository now exposes versioned Terms and Privacy pages, records the accepted terms version at registration, identifies the source of every job listing, and links users back to provider websites. These are engineering controls, not legal approval.

## Required decisions before paid or public launch

- Confirm the operating company’s legal name, registration address, contact channel, and launch jurisdictions.
- Have qualified counsel approve Terms of Use, Privacy Notice, cookie/analytics notice, refund and cancellation rules, warranty language, liability limits, dispute terms, and governing law.
- Build and publish a current subprocessor list, including hosting, email, analytics, payment, AI, monitoring, and support vendors.
- Document lawful bases, international data-transfer safeguards, data-subject request procedures, breach response, retention periods, and backup deletion handling.
- Review Jooble, Adzuna, Himalayas, RemoteOK, and Arbeitnow terms directly. Confirm commercial display, caching, ranking, attribution, link behavior, geographic coverage, rate limits, and logo/trademark permissions in writing where required.
- Never describe NextHire AI as partnered with, endorsed by, or affiliated with a provider unless a signed agreement permits it.
- Confirm that AI-provider terms permit processing resumes and career data and determine whether provider-side retention or training must be disabled contractually or technically.
- Complete accessibility and consumer-protection reviews for the target market.

## Provider implementation rules

Each normalized listing carries `source`, `source_homepage`, and `source_api_page`. The interface shows attribution and sends users to the original listing to verify details and apply. Provider status cards link to provider homepages. Do not remove these fields during future normalization or redesign.

Provider contracts can change. Legal and product owners should record review date, reviewer, applicable terms URL, approved use, required attribution, caching duration, and termination procedure in a maintained provider register.
