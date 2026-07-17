from datetime import UTC, datetime

import stripe

from backend.core.settings import (
    FRONTEND_URL,
    STRIPE_PRO_PRICE_ID,
    STRIPE_SECRET_KEY,
    STRIPE_WEBHOOK_SECRET,
)
from backend.repositories.user_repository import UserRepository


class BillingConfigurationError(Exception):
    pass


class BillingService:
    def __init__(self, repository: UserRepository):
        self.repository = repository
        stripe.api_key = STRIPE_SECRET_KEY

    @staticmethod
    def status(user) -> dict:
        return {
            "plan": user.plan or "free",
            "subscription_status": user.subscription_status,
            "subscription_period_end": user.subscription_period_end,
            "billing_enabled": bool(STRIPE_SECRET_KEY and STRIPE_PRO_PRICE_ID),
        }

    def create_checkout(self, user) -> str:
        self._require_checkout_configuration()
        if not user.stripe_customer_id:
            customer = stripe.Customer.create(
                email=user.email,
                metadata={"user_id": str(user.id)},
            )
            user.stripe_customer_id = customer.id
            self.repository.save(user)
        session = stripe.checkout.Session.create(
            customer=user.stripe_customer_id,
            mode="subscription",
            line_items=[{"price": STRIPE_PRO_PRICE_ID, "quantity": 1}],
            success_url=f"{FRONTEND_URL}/settings?billing=success",
            cancel_url=f"{FRONTEND_URL}/settings?billing=cancelled",
            client_reference_id=str(user.id),
        )
        return session.url

    def create_portal(self, user) -> str:
        if not STRIPE_SECRET_KEY or not user.stripe_customer_id:
            raise BillingConfigurationError("Billing portal is not available for this account.")
        session = stripe.billing_portal.Session.create(
            customer=user.stripe_customer_id,
            return_url=f"{FRONTEND_URL}/settings",
        )
        return session.url

    def handle_webhook(self, payload: bytes, signature: str | None) -> None:
        if not STRIPE_WEBHOOK_SECRET or not signature:
            raise BillingConfigurationError("Stripe webhook verification is not configured.")
        event = stripe.Webhook.construct_event(
            payload, signature, STRIPE_WEBHOOK_SECRET
        )
        if event["type"] not in {
            "customer.subscription.created",
            "customer.subscription.updated",
            "customer.subscription.deleted",
        }:
            return
        subscription = event["data"]["object"]
        user = self.repository.get_by_stripe_customer_id(subscription["customer"])
        if not user:
            return
        status = subscription["status"]
        user.subscription_status = status
        user.stripe_subscription_id = subscription["id"]
        period_end = subscription.get("current_period_end")
        user.subscription_period_end = (
            datetime.fromtimestamp(period_end, UTC).replace(tzinfo=None)
            if period_end else None
        )
        user.plan = "pro" if status in {"active", "trialing"} else "free"
        self.repository.save(user)

    @staticmethod
    def _require_checkout_configuration() -> None:
        if not STRIPE_SECRET_KEY or not STRIPE_PRO_PRICE_ID:
            raise BillingConfigurationError(
                "Paid plans are not available yet. Stripe must be configured first."
            )
