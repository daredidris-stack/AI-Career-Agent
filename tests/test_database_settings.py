import unittest

from backend.core.settings import normalize_database_url


class DatabaseSettingsTests(unittest.TestCase):
    def test_postgres_urls_use_psycopg_driver(self):
        self.assertEqual(
            normalize_database_url("postgres://db.example/career"),
            "postgresql+psycopg://db.example/career",
        )
        self.assertEqual(
            normalize_database_url("postgresql://db.example/career"),
            "postgresql+psycopg://db.example/career",
        )

    def test_sqlite_url_is_unchanged(self):
        value = "sqlite:///./career_agent.db"
        self.assertEqual(normalize_database_url(value), value)


if __name__ == "__main__":
    unittest.main()
