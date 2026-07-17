import unittest
from types import SimpleNamespace

from backend.services.candidate_skills import (
    merge_candidate_skills,
    profile_with_skills,
)


class CandidateSkillsTests(unittest.TestCase):
    def test_merges_profile_and_resume_skills_without_duplicates(self):
        profile = SimpleNamespace(
            technical_skills="AWS, Linux",
            current_role="DCO",
            target_role="SRE",
            years_experience=4,
            professional_summary="Operations specialist",
        )

        skills = merge_candidate_skills(
            profile,
            ["Python", "aws", "Terraform"],
        )
        context = profile_with_skills(profile, skills)

        self.assertEqual(
            skills,
            ["AWS", "Linux", "Python", "Terraform"],
        )
        self.assertEqual(context["target_role"], "SRE")
        self.assertEqual(context["technical_skills"], skills)


if __name__ == "__main__":
    unittest.main()
