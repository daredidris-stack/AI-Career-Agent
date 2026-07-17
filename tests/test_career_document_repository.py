import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.database.database import Base
from backend.models.user import User
from backend.repositories.career_document_repository import (
    CareerDocumentRepository,
)


class CareerDocumentRepositoryTests(unittest.TestCase):
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
        self.repository = CareerDocumentRepository(self.db)

    def tearDown(self):
        self.db.close()
        self.engine.dispose()

    def test_documents_are_scoped_to_owner(self):
        document = self.repository.create(
            user_id=self.first_id,
            kind="resume",
            title="Cloud Resume",
            content="AWS experience",
            metadata_json="{}",
        )

        self.assertIsNone(
            self.repository.get_for_user(document.id, self.second_id)
        )
        self.assertEqual(
            self.repository.get_for_user(document.id, self.first_id).title,
            "Cloud Resume",
        )

    def test_list_can_filter_document_kind(self):
        for kind in ("resume", "cover_letter"):
            self.repository.create(
                user_id=self.first_id,
                kind=kind,
                title=kind,
                content="content",
                metadata_json="{}",
            )

        documents = self.repository.list_for_user(
            self.first_id, "cover_letter"
        )

        self.assertEqual([item.kind for item in documents], ["cover_letter"])

    def test_revision_lookup_is_scoped_to_owner(self):
        document = self.repository.create(
            user_id=self.first_id,
            kind="resume",
            title="Original",
            content="Version one",
            metadata_json="{}",
        )
        revision = self.repository.create_revision(document)
        self.db.commit()

        self.assertIsNone(self.repository.get_revision(
            revision.id, document.id, self.second_id
        ))
        self.assertEqual(
            self.repository.get_revision(
                revision.id, document.id, self.first_id
            ).content,
            "Version one",
        )


if __name__ == "__main__":
    unittest.main()
