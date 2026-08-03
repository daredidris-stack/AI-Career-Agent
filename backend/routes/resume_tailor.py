from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from backend.dependencies.auth import get_current_user
from backend.dependencies.services import get_ai_usage_service, get_resume_tailor_service
from backend.models.user import User
from backend.services.ai_usage_service import AIUsageService, reserve_ai_usage
from backend.services.resume_tailor_service import (
    ProfileRequiredError,
    ResumeTailorError,
    ResumeTailorService,
)
from backend.services.resume_template_service import list_resume_templates
from backend.services.malware_scan_service import (
    MalwareScannerUnavailableError,
)
from backend.services.resume_parser_service import (
    ResumeParserUnavailableError,
)


router = APIRouter(
    prefix="/resume",
    tags=["Resume"],
)


@router.get("/templates")
def get_resume_templates(
    _current_user: User = Depends(get_current_user),
):
    return list_resume_templates()


@router.post("/tailor-upload")
async def tailor_resume_upload(
    file: UploadFile | None = File(None),
    job_description: str = Form(...),
    template_id: str = Form("auto"),
    current_user: User = Depends(get_current_user),
    service: ResumeTailorService = Depends(
        get_resume_tailor_service
    ),
    usage: AIUsageService = Depends(get_ai_usage_service),
):
    reserve_ai_usage(usage, current_user.id, "resume_tailor")
    try:
        return await service.tailor_for_user(
            user_id=current_user.id,
            file=file,
            job_description=job_description,
            template_id=template_id,
        )
    except ProfileRequiredError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        ) from error
    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error
    except MalwareScannerUnavailableError as error:
        raise HTTPException(
            status_code=503,
            detail=str(error),
        ) from error
    except ResumeParserUnavailableError as error:
        raise HTTPException(
            status_code=503,
            detail=str(error),
        ) from error
    except ResumeTailorError as error:
        raise HTTPException(
            status_code=502,
            detail=str(error),
        ) from error
