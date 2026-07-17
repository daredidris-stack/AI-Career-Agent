# Billing operations

Billing is disabled by default. The interface exposes the Free plan and shows Pro as unavailable until `STRIPE_SECRET_KEY` and `STRIPE_PRO_PRICE_ID` are configured. No price is hard-coded in the application; product owners create and approve the recurring price in Stripe.

## Activation checklist

1. Complete legal approval for price, currency, taxes, renewal, cancellation, refund, trial, and consumer disclosures.
2. Create a recurring Stripe Price and set its ID as `STRIPE_PRO_PRICE_ID`.
3. Store the restricted production secret key as `STRIPE_SECRET_KEY` in the hosting secret manager.
4. Register `POST /billing/webhook` in Stripe and subscribe to `customer.subscription.created`, `customer.subscription.updated`, and `customer.subscription.deleted`.
5. Store the signing secret as `STRIPE_WEBHOOK_SECRET`.
6. Run Stripe test-mode checkout, renewal, failed-payment, cancellation, portal, duplicate-webhook, and refund scenarios before enabling live mode.

Only a verified webhook changes account entitlements. Browser redirects never promote an account. Active and trialing subscriptions receive the Pro AI allowance; other statuses revert to Free limits.

## Operational controls

- Restrict Stripe dashboard access and require multifactor authentication.
- Rotate exposed keys immediately and review webhook delivery logs.
- Reconcile application subscription state against Stripe on a schedule before commercial scale.
- Alert on webhook failures and do not log payment payloads or customer financial information.
- Keep pricing and entitlement changes versioned and tested.
