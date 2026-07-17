import unittest
from unittest.mock import Mock, patch

from fastapi.responses import JSONResponse

from backend.routes.health import liveness, readiness


class HealthRouteTests(unittest.TestCase):
    def test_liveness_identifies_running_release(self):
        result = liveness()
        self.assertEqual(result["status"], "ok")
        self.assertIn("release", result)

    def test_readiness_checks_database(self):
        db = Mock()
        result = readiness(db)
        self.assertEqual(result["status"], "ready")
        db.execute.assert_called_once()

    def test_database_failure_returns_503(self):
        db = Mock()
        db.execute.side_effect = RuntimeError("offline")

        result = readiness(db)

        self.assertIsInstance(result, JSONResponse)
        self.assertEqual(result.status_code, 503)

    @patch("backend.routes.health.APP_ENV", "production")
    @patch("backend.routes.health.DATABASE_URL", "sqlite:///local.db")
    def test_production_sqlite_is_not_ready(self):
        result = readiness(Mock())
        self.assertIsInstance(result, JSONResponse)
        self.assertEqual(result.status_code, 503)


if __name__ == "__main__":
    unittest.main()
