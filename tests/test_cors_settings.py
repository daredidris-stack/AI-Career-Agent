import unittest

from backend.core.settings import CORS_ALLOWED_ORIGINS


class CorsSettingsTests(unittest.TestCase):
    def test_development_origins_support_localhost_and_loopback(self):
        self.assertIn("http://localhost:5173", CORS_ALLOWED_ORIGINS)
        self.assertIn("http://127.0.0.1:5173", CORS_ALLOWED_ORIGINS)


if __name__ == "__main__":
    unittest.main()
