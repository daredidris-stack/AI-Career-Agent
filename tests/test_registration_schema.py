import unittest

from pydantic import ValidationError

from backend.models.schemas import RegisterRequest


class RegistrationSchemaTests(unittest.TestCase):
    def test_registration_requires_terms_acceptance(self):
        with self.assertRaises(ValidationError):
            RegisterRequest(
                email="user@example.com",
                password="long-enough-password",
                accept_terms=False,
            )

        request = RegisterRequest(
            email="user@example.com",
            password="long-enough-password",
            accept_terms=True,
        )
        self.assertTrue(request.accept_terms)


if __name__ == "__main__":
    unittest.main()
