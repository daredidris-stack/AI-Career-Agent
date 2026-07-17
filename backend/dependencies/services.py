from fastapi import Depends

from backend.dependencies.repositories import (
    get_user_repository,
    get_profile_repository,
)

from backend.repositories.user_repository import (
    UserRepository,
)

from backend.repositories.profile_repository import (
    ProfileRepository,
)

from backend.services.auth_service import (
    AuthService,
)

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


def get_auth_service(
    repo: UserRepository = Depends(
        get_user_repository
    ),
):

    return AuthService(repo)



def get_profile_service(
    repo: ProfileRepository = Depends(
        get_profile_repository
    ),
):

    return ProfileService(repo)


def get_resume_service():
    return ResumeService()


def get_job_search_service(
    repo: ProfileRepository = Depends(
        get_profile_repository
    ),
):
    return JobSearchService(repo)


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
