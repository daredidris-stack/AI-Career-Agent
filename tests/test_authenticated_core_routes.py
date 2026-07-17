import unittest

from fastapi.testclient import TestClient

from backend.main import app


class AuthenticatedCoreRouteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_dashboard_requires_authentication(self):
        response = self.client.get("/dashboard")

        self.assertEqual(response.status_code, 401)

    def test_job_search_requires_authentication(self):
        response = self.client.get("/jobs/search")

        self.assertEqual(response.status_code, 401)

    def test_job_match_requires_authentication(self):
        response = self.client.post(
            "/jobs/match",
            json={"resume": "Resume", "job_description": "Job"},
        )

        self.assertEqual(response.status_code, 401)

    def test_resume_analysis_requires_authentication(self):
        response = self.client.post(
            "/resume/analyze",
            files={"file": ("resume.txt", b"Resume", "text/plain")},
        )

        self.assertEqual(response.status_code, 401)

    def test_resume_tailor_requires_authentication(self):
        response = self.client.post(
            "/resume/tailor-upload",
            data={"job_description": "Job"},
            files={"file": ("resume.txt", b"Resume", "text/plain")},
        )

        self.assertEqual(response.status_code, 401)

    def test_cover_letter_requires_authentication(self):
        response = self.client.post(
            "/cover-letter",
            json={"resume": "Resume", "job_description": "Job"},
        )

        self.assertEqual(response.status_code, 401)


if __name__ == "__main__":
    unittest.main()
