import os
import unittest
from unittest.mock import patch

from backend.core.settings import resolve_app_release


class ReleaseSettingsTests(unittest.TestCase):
    def test_railway_git_commit_overrides_manual_release(self):
        with patch.dict(
            os.environ,
            {
                "RAILWAY_GIT_COMMIT_SHA": "railway-commit",
                "APP_RELEASE": "stale-manual-release",
            },
            clear=False,
        ):
            self.assertEqual(resolve_app_release(), "railway-commit")

    def test_manual_release_is_used_outside_railway(self):
        with patch.dict(
            os.environ,
            {"APP_RELEASE": "manual-release"},
            clear=False,
        ):
            os.environ.pop("RAILWAY_GIT_COMMIT_SHA", None)
            self.assertEqual(resolve_app_release(), "manual-release")

    def test_development_is_the_default_release(self):
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("RAILWAY_GIT_COMMIT_SHA", None)
            os.environ.pop("APP_RELEASE", None)
            self.assertEqual(resolve_app_release(), "development")


if __name__ == "__main__":
    unittest.main()
