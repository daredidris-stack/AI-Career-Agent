# Saved-search email alert setup

Saved-search email delivery has two independent safety switches:

1. The deployment must set `JOB_ALERT_EMAIL_ENABLED=true`.
2. Each user must have a verified account email and explicitly enable an alert
   for an individual saved search.

Keep the deployment switch `false` until the sender, database migration,
scheduled worker, consent control, delivery record, and unsubscribe flow pass
in staging.

## 1. Create and verify the sender

Postmark is a suitable SMTP option, but the app remains provider-neutral. In
Postmark:

1. Create a server for the staging or production environment.
2. Verify either the exact sender address or its domain.
3. Use the server's SMTP credentials only in Railway variables. Never put them
   in a frontend variable, committed file, ticket, or support message.
4. Review the provider's current pricing, limits, and production-approval
   requirements before inviting users.

Postmark's current SMTP and sender documentation:

- [Send with SMTP](https://postmarkapp.com/developer/user-guide/send-email-with-smtp)
- [Manage sender signatures](https://postmarkapp.com/developer/user-guide/managing-your-account/managing-sender-signatures)
- [Test with a sandbox server](https://postmarkapp.com/developer/user-guide/sandbox-mode/server-sandbox-mode)

## 2. Configure the Railway API service

Set these server-side variables on the API service:

```env
SMTP_HOST=smtp.postmarkapp.com
SMTP_PORT=587
SMTP_USERNAME=<SMTP credential from Postmark>
SMTP_PASSWORD=<SMTP credential from Postmark>
SMTP_FROM_EMAIL=<verified sender address>
SMTP_USE_TLS=true
FRONTEND_URL=https://<public frontend host>
JOB_ALERT_EMAIL_ENABLED=false
JOB_ALERT_BATCH_SIZE=50
JOB_ALERT_RETRY_MINUTES=60
JOB_ALERT_SEND_HOUR=8
JOB_ALERT_MAX_JOBS_PER_EMAIL=10
```

The API and worker must use the same `DATABASE_URL`, `JWT_SECRET_KEY`,
`FRONTEND_URL`, SMTP settings, and `JOB_ALERT_*` settings. `FRONTEND_URL` must
be the public origin that serves `/email-preferences`; otherwise unsubscribe
links will point to the wrong site.

Deploy while `JOB_ALERT_EMAIL_ENABLED=false`, then confirm that migration
`20260729_0011` is current and the API health checks pass.

## 3. Add the Railway scheduled service

Create a second Railway service from the same repository and deployment image.
Override its start command with:

```bash
python -m backend.jobs.send_job_alerts
```

Give it the same variables described above. Configure a Railway cron schedule
of:

```text
0 * * * *
```

The schedule is hourly in UTC. Each invocation processes only searches whose
user-local daily or weekly delivery time is due, then exits. Railway cron
processes must terminate; Railway also skips a later invocation if the previous
one is still active. See [Railway cron jobs](https://docs.railway.com/cron-jobs)
and [Railway services](https://docs.railway.com/services).

With the deployment switch still `false`, run the service once and verify its
report says `configured: false` and sends no email.

## 4. Staged activation test

Use one disposable, verified account and one saved search:

1. Turn `JOB_ALERT_EMAIL_ENABLED=true` on both the API and scheduled service.
2. Confirm Operations shows both Email delivery and Saved-search email alerts
   as configured.
3. Open Job Library and confirm the alert is still off by default.
4. Explicitly enable a daily alert. Confirm its next scheduled time appears.
5. Run the worker once. The first run must establish the saved-search baseline
   and send no email.
6. Add or expose one safe test listing that was not in the baseline, make the
   search due, and run the worker again.
7. Confirm one email arrives, its listing opens the identified provider, and
   Recent email alert activity records a sent delivery.
8. Open the email's unsubscribe link. Confirm that merely opening the page
   changes nothing, then choose **Turn off this email alert**.
9. Confirm only that saved-search alert is disabled and a later worker run
   sends nothing.
10. Repeat a failed-delivery test and confirm the delivery record is failed,
    job matches are not marked as seen, and the search is eligible for retry.

Do not enable automatic alerts for a wider group until this exact path passes
with the deployed sender and public frontend.

## 5. Monitoring and rollback

Monitor the scheduled-service exit status and the Operations delivery totals.
Application logs record only generic failure types; SMTP credentials must never
appear in logs.

To stop all automatic saved-search email immediately, set:

```env
JOB_ALERT_EMAIL_ENABLED=false
```

Apply it to both the API and scheduled service. This preserves each user's
preference and delivery history but makes the controls unavailable and causes
the worker to exit without querying or sending. Disable the Railway cron
schedule as a second containment step if needed.
