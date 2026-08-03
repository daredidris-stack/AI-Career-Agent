from fastapi import APIRouter, Depends, HTTPException, Response

from backend.core.settings import AI_JOB_RANKING_ENABLED
from backend.dependencies.auth import get_current_user
from backend.dependencies.services import (
    get_ai_usage_service,
    get_job_alert_service,
    get_job_library_service,
    get_job_search_service,
)
from backend.models.schemas import (
    EmailAlertUnsubscribe,
    SavedJobCreate,
    SavedSearchAlertUpdate,
    SavedSearchCreate,
)
from backend.models.user import User
from backend.services.ai_usage_service import AIUsageService, reserve_ai_usage
from backend.services.job_alert_service import (
    InvalidUnsubscribeTokenError,
    JobAlertService,
)
from backend.services.job_library_service import (
    JobLibraryItemNotFoundError,
    JobLibraryService,
)
from backend.services.job_search_service import (
    JobSearchError,
    JobSearchInputError,
    JobSearchService,
)


router = APIRouter(prefix="/job-library", tags=["Job Library"])


@router.get("/saved-jobs")
def list_saved_jobs(
    current_user: User = Depends(get_current_user),
    service: JobLibraryService = Depends(get_job_library_service),
):
    return service.list_saved_jobs(current_user.id)


@router.post("/saved-jobs", status_code=201)
def save_job(
    request: SavedJobCreate,
    current_user: User = Depends(get_current_user),
    service: JobLibraryService = Depends(get_job_library_service),
):
    try:
        return service.save_job(current_user.id, request.model_dump())
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@router.delete("/saved-jobs/{saved_job_id}", status_code=204)
def delete_saved_job(
    saved_job_id: int,
    current_user: User = Depends(get_current_user),
    service: JobLibraryService = Depends(get_job_library_service),
):
    try:
        service.delete_saved_job(current_user.id, saved_job_id)
    except JobLibraryItemNotFoundError as error:
        raise HTTPException(status_code=404, detail="Saved job not found.") from error
    return Response(status_code=204)


@router.get("/searches")
def list_saved_searches(
    current_user: User = Depends(get_current_user),
    service: JobLibraryService = Depends(get_job_library_service),
):
    return service.list_searches(current_user.id)


@router.post("/searches", status_code=201)
def create_saved_search(
    request: SavedSearchCreate,
    current_user: User = Depends(get_current_user),
    service: JobLibraryService = Depends(get_job_library_service),
):
    return service.create_search(
        current_user.id,
        request.name,
        request.filters.model_dump(),
    )


@router.get("/email-alerts/status")
def get_email_alert_status(
    current_user: User = Depends(get_current_user),
    service: JobAlertService = Depends(get_job_alert_service),
):
    return service.status_for_user(current_user)


@router.get("/email-alerts/deliveries")
def list_email_alert_deliveries(
    current_user: User = Depends(get_current_user),
    service: JobAlertService = Depends(get_job_alert_service),
):
    return service.list_deliveries(current_user.id)


@router.patch("/searches/{saved_search_id}/email-alerts")
def update_saved_search_email_alerts(
    saved_search_id: int,
    request: SavedSearchAlertUpdate,
    current_user: User = Depends(get_current_user),
    service: JobAlertService = Depends(get_job_alert_service),
):
    try:
        return service.update_preferences(
            current_user,
            saved_search_id,
            request.enabled,
            request.frequency,
            request.timezone,
        )
    except JobLibraryItemNotFoundError as error:
        raise HTTPException(
            status_code=404,
            detail="Saved search not found.",
        ) from error
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@router.post("/email-alerts/unsubscribe")
def unsubscribe_from_saved_search_alert(
    request: EmailAlertUnsubscribe,
    service: JobAlertService = Depends(get_job_alert_service),
):
    try:
        return service.unsubscribe(request.token)
    except InvalidUnsubscribeTokenError as error:
        raise HTTPException(
            status_code=400,
            detail="This unsubscribe link is invalid.",
        ) from error


@router.delete("/searches/{saved_search_id}", status_code=204)
def delete_saved_search(
    saved_search_id: int,
    current_user: User = Depends(get_current_user),
    service: JobLibraryService = Depends(get_job_library_service),
):
    try:
        service.delete_search(current_user.id, saved_search_id)
    except JobLibraryItemNotFoundError as error:
        raise HTTPException(
            status_code=404,
            detail="Saved search not found.",
        ) from error
    return Response(status_code=204)


@router.post("/searches/{saved_search_id}/acknowledge")
def acknowledge_saved_search(
    saved_search_id: int,
    current_user: User = Depends(get_current_user),
    service: JobLibraryService = Depends(get_job_library_service),
):
    try:
        return service.acknowledge_search(
            current_user.id,
            saved_search_id,
        )
    except JobLibraryItemNotFoundError as error:
        raise HTTPException(
            status_code=404,
            detail="Saved search not found.",
        ) from error


@router.post("/searches/{saved_search_id}/run")
def run_saved_search(
    saved_search_id: int,
    current_user: User = Depends(get_current_user),
    library: JobLibraryService = Depends(get_job_library_service),
    search: JobSearchService = Depends(get_job_search_service),
    usage: AIUsageService = Depends(get_ai_usage_service),
):
    try:
        saved_search = library.get_search(
            current_user.id,
            saved_search_id,
        )
        filters = library.search_filters(saved_search)
        if AI_JOB_RANKING_ENABLED:
            reserve_ai_usage(
                usage,
                current_user.id,
                "job_search_ranking",
            )
        result = search.search_for_user(
            user_id=current_user.id,
            **filters,
            page=1,
            per_page=50,
        )
        saved_search_response = library.record_search_results(
            saved_search,
            result.get("jobs", []),
        )
        return {
            "saved_search": saved_search_response,
            "result": result,
        }
    except JobLibraryItemNotFoundError as error:
        raise HTTPException(
            status_code=404,
            detail="Saved search not found.",
        ) from error
    except JobSearchInputError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except JobSearchError as error:
        raise HTTPException(status_code=502, detail=str(error)) from error
