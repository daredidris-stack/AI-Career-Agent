import unittest
from datetime import timedelta

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.database.database import Base
from backend.core.time import utc_now
from backend.models.user import User
from backend.repositories.profile_repository import ProfileRepository


class ProfileRepositoryTests(unittest.TestCase):
    def setUp(self):
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        session_factory = sessionmaker(bind=engine)
        self.db = session_factory()

        user = User(
            email="profile-test@example.com",
            password_hash="test-hash",
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        self.repository = ProfileRepository(self.db)
        self.user_id = user.id

    def tearDown(self):
        self.db.close()

    def test_update_changes_fields_and_updated_at(self):
        profile = self.repository.create_profile(
            self.user_id,
            {"current_role": "Technician"},
        )
        original_timestamp = utc_now() - timedelta(days=1)
        profile.updated_at = original_timestamp
        self.db.commit()

        updated_profile = self.repository.update_profile(
            profile,
            {"current_role": "Cloud Engineer"},
        )

        self.assertEqual(
            updated_profile.current_role,
            "Cloud Engineer",
        )
        self.assertGreater(
            updated_profile.updated_at,
            original_timestamp,
        )


if __name__ == "__main__":
    unittest.main()
