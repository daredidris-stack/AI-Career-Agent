import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.database.database import Base
from backend.models.career_document import CareerDocument
from backend.models.profile import Profile
from backend.models.user import User
from backend.repositories.user_data_repository import UserDataRepository


class UserDataRepositoryTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        Base.metadata.create_all(self.engine)
        self.db = sessionmaker(bind=self.engine)()
        first = User(email="first@example.com", password_hash="hash")
        second = User(email="second@example.com", password_hash="hash")
        self.db.add_all([first, second])
        self.db.commit()
        self.first_id = first.id
        self.second_id = second.id

    def tearDown(self):
        self.db.close()
        self.engine.dispose()

    def test_export_snapshot_is_scoped_to_authenticated_owner(self):
        self.db.add_all([
            Profile(user_id=self.first_id, city="First city"),
            Profile(user_id=self.second_id, city="Private city"),
            CareerDocument(
                user_id=self.first_id,
                kind="resume",
                title="First resume",
                content="First content",
            ),
            CareerDocument(
                user_id=self.second_id,
                kind="resume",
                title="Private resume",
                content="Private content",
            ),
        ])
        self.db.commit()

        result = UserDataRepository(self.db).snapshot(self.first_id)

        self.assertEqual(result["profile"].city, "First city")
        self.assertEqual(
            [document.title for document in result["career_documents"]],
            ["First resume"],
        )


if __name__ == "__main__":
    unittest.main()
