import unittest
from datetime import datetime
from types import SimpleNamespace
from unittest.mock import Mock, patch

from backend.services.billing_service import BillingConfigurationError, BillingService


class BillingServiceTests(unittest.TestCase):
    def setUp(self):
        self.repository = Mock()
        self.user = SimpleNamespace(
            id=7,
            email="user@example.com",
            plan="free",
            stripe_customer_id=None,
            stripe_subscription_id=None,
            subscription_status=None,
            subscription_period_end=None,
        )

    @patch("backend.services.billing_service.STRIPE_PRO_PRICE_ID", None)
    @patch("backend.services.billing_service.STRIPE_SECRET_KEY", None)
    def test_checkout_is_disabled_without_configuration(self):
        with self.assertRaises(BillingConfigurationError):
            BillingService(self.repository).create_checkout(self.user)

    @patch("backend.services.billing_service.STRIPE_PRO_PRICE_ID", "price_pro")
    @patch("backend.services.billing_service.STRIPE_SECRET_KEY", "sk_test")
    @patch("backend.services.billing_service.stripe.checkout.Session.create")
    @patch("backend.services.billing_service.stripe.Customer.create")
    def test_checkout_creates_customer_and_subscription_session(
        self, create_customer, create_session
    ):
        create_customer.return_value = SimpleNamespace(id="cus_123")
        create_session.return_value = SimpleNamespace(url="https://checkout")

        url = BillingService(self.repository).create_checkout(self.user)

        self.assertEqual(url, "https://checkout")
        self.assertEqual(self.user.stripe_customer_id, "cus_123")
        self.repository.save.assert_called_with(self.user)

    @patch("backend.services.billing_service.STRIPE_WEBHOOK_SECRET", "whsec_test")
    @patch("backend.services.billing_service.stripe.Webhook.construct_event")
    def test_active_subscription_promotes_user(self, construct_event):
        construct_event.return_value = {
            "type": "customer.subscription.updated",
            "data": {"object": {
                "id": "sub_123",
                "customer": "cus_123",
                "status": "active",
                "current_period_end": 1_800_000_000,
            }},
        }
        self.repository.get_by_stripe_customer_id.return_value = self.user

        BillingService(self.repository).handle_webhook(b"{}", "signature")

        self.assertEqual(self.user.plan, "pro")
        self.assertEqual(self.user.stripe_subscription_id, "sub_123")
        self.assertIsInstance(self.user.subscription_period_end, datetime)


if __name__ == "__main__":
    unittest.main()
