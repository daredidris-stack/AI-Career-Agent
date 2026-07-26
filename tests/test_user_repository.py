import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.database.database import Base
from backend.repositories.user_repository import UserRepository


class UserRepositoryTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        Base.metadata.create_all(self.engine)
        self.db = sessionmaker(bind=self.engine)()
        self.repository = UserRepository(self.db)

    def tearDown(self):
        self.db.close()
        self.engine.dispose()

    def test_create_and_lookup_normalize_email_case(self):
        created = self.repository.create_user(
            email=" User@Gmail.COM ",
            password_hash="hash",
        )

        found = self.repository.get_by_email("USER@gmail.com")

        self.assertEqual(created.email, "user@gmail.com")
        self.assertEqual(found.id, created.id)


if __name__ == "__main__":
    unittest.main()
