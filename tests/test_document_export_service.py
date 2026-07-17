import unittest
from io import BytesIO
from types import SimpleNamespace
from zipfile import ZipFile

from backend.services.document_export_service import export_document


class DocumentExportServiceTests(unittest.TestCase):
    def setUp(self):
        self.document = SimpleNamespace(
            title="Cloud Engineer Resume",
            content="Summary\nAWS and Linux experience",
        )

    def test_exports_valid_pdf(self):
        content, media_type, filename = export_document(self.document, "pdf")

        self.assertTrue(content.startswith(b"%PDF"))
        self.assertEqual(media_type, "application/pdf")
        self.assertEqual(filename, "cloud-engineer-resume.pdf")

    def test_exports_valid_docx(self):
        content, media_type, filename = export_document(self.document, "docx")

        with ZipFile(BytesIO(content)) as archive:
            self.assertIn("word/document.xml", archive.namelist())
        self.assertIn("wordprocessingml.document", media_type)
        self.assertEqual(filename, "cloud-engineer-resume.docx")

    def test_rejects_unknown_export_format(self):
        with self.assertRaises(ValueError):
            export_document(self.document, "exe")


if __name__ == "__main__":
    unittest.main()
