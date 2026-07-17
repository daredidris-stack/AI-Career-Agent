from fastapi import Depends

from backend.dependencies.repositories import (
    get_user_repository,
    get_profile_repository,
    get_job_catalog_repository,
    get_resume_analysis_repository,
)

from backend.repositories.user_repository import (
    UserRepository,
)

from backend.repositories.profile_repository import (
    ProfileRepository,
)

from backend.repositories.job_catalog_repository import (
    JobCatalogRepository,
)

from backend.repositories.resume_analysis_repository import (
    ResumeAnalysisRepository,
)

from backend.services.auth_service import (
    AuthService,
)
from backend.services.email_service import EmailService

from backend.services.profile_service import (
    ProfileService,
)

from backend.services.resume_service import (
    ResumeService,
)

from backend.services.job_search_service import (
    JobSearchService,
)

from backend.services.resume_tailor_service import (
    ResumeTailorService,
)

from backend.services.cover_letter_service import (
    CoverLetterService,
)

from backend.services.job_match_service import (
    JobMatchService,
)

from backend.services.skill_gap_service import (
    SkillGapService,
)

from backend.services.analytics_service import (
    AnalyticsService,
)

from backend.services.dashboard_service import (
    DashboardService,
)


def get_auth_service(
    repo: UserRepository = Depends(
        get_user_repository
    ),
):
    return AuthService(repo, EmailService())



def get_profile_service(
    repo: ProfileRepository = Depends(
        get_profile_repository
    ),
):

    return ProfileService(repo)


def get_resume_service(
    profile_repo: ProfileRepository = Depends(
        get_profile_repository
    ),
    analysis_repo: ResumeAnalysisRepository = Depends(
        get_resume_analysis_repository
    ),
):
    return ResumeService(profile_repo, analysis_repo)


def get_job_search_service(
    repo: ProfileRepository = Depends(
        get_profile_repository
    ),
    analysis_repo: ResumeAnalysisRepository = Depends(
        get_resume_analysis_repository
    ),
):
    return JobSearchService(repo, analysis_repo)


def get_resume_tailor_service(
    repo: ProfileRepository = Depends(
        get_profile_repository
    ),
    resume_service: ResumeService = Depends(
        get_resume_service
    ),
):
    return ResumeTailorService(
        repo,
        resume_service,
    )


def get_cover_letter_service(
    repo: ProfileRepository = Depends(
        get_profile_repository
    ),
):
    return CoverLetterService(repo)


def get_job_match_service(
    repo: ProfileRepository = Depends(
        get_profile_repository
    ),
):
    return JobMatchService(repo)


def get_skill_gap_service(
    profile_repo: ProfileRepository = Depends(
        get_profile_repository
    ),
    job_catalog_repo: JobCatalogRepository = Depends(
        get_job_catalog_repository
    ),
    analysis_repo: ResumeAnalysisRepository = Depends(
        get_resume_analysis_repository
    ),
):
    return SkillGapService(
        profile_repo,
        job_catalog_repo,
        analysis_repo,
    )


def get_analytics_service(
    profile_repo: ProfileRepository = Depends(
        get_profile_repository
    ),
    job_catalog_repo: JobCatalogRepository = Depends(
        get_job_catalog_repository
    ),
    analysis_repo: ResumeAnalysisRepository = Depends(
        get_resume_analysis_repository
    ),
):
    return AnalyticsService(
        profile_repo,
        job_catalog_repo,
        analysis_repo,
    )


def get_dashboard_service(
    profile_repo: ProfileRepository = Depends(
        get_profile_repository
    ),
    analytics_service: AnalyticsService = Depends(
        get_analytics_service
    ),
    analysis_repo: ResumeAnalysisRepository = Depends(
        get_resume_analysis_repository
    ),
):
    return DashboardService(
        profile_repo,
        analytics_service,
        analysis_repo,
    )
