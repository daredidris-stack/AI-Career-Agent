import unittest
from types import SimpleNamespace
from unittest.mock import Mock

from backend.services.career_document_service import (
    CareerDocumentService,
    DocumentNotFoundError,
)


class CareerDocumentServiceTests(unittest.TestCase):
    def setUp(self):
        self.repository = Mock()
        self.service = CareerDocumentService(self.repository)

    def test_create_serializes_metadata_and_assigns_owner(self):
        self.service.create_for_user(
            7,
            "resume",
            " My Resume ",
            " Resume text ",
            metadata={"score": 85},
        )

        values = self.repository.create.call_args.kwargs
        self.assertEqual(values["user_id"], 7)
        self.assertEqual(values["title"], "My Resume")
        self.assertEqual(values["metadata_json"], '{"score": 85}')

    def test_update_cannot_access_another_users_document(self):
        self.repository.get_for_user.return_value = None

        with self.assertRaises(DocumentNotFoundError):
            self.service.update_for_user(7, 99, "Title", "Content")

        self.repository.get_for_user.assert_called_once_with(99, 7)
        self.repository.save.assert_not_called()

    def test_delete_uses_owner_scoped_lookup(self):
        document = SimpleNamespace(id=4)
        self.repository.get_for_user.return_value = document

        self.service.delete_for_user(7, 4)

        self.repository.get_for_user.assert_called_once_with(4, 7)
        self.repository.delete.assert_called_once_with(document)

    def test_update_preserves_previous_version(self):
        document = SimpleNamespace(
            id=4, user_id=7, title="Old", content="Old content"
        )
        self.repository.get_for_user.return_value = document

        self.service.update_for_user(7, 4, "New", "New content")

        self.repository.create_revision.assert_called_once_with(document)
        self.repository.save.assert_called_once_with(document)
        self.assertEqual(document.title, "New")

    def test_restore_is_scoped_to_document_and_owner(self):
        document = SimpleNamespace(
            id=4, user_id=7, title="Current", content="Current"
        )
        revision = SimpleNamespace(title="Previous", content="Previous")
        self.repository.get_for_user.return_value = document
        self.repository.get_revision.return_value = revision

        restored = self.service.restore_version(7, 4, 9)

        self.repository.get_revision.assert_called_once_with(9, 4, 7)
        self.assertEqual(restored, self.repository.save.return_value)
        self.assertEqual(document.content, "Previous")


if __name__ == "__main__":
    unittest.main()
