from fastapi import APIRouter, Depends, HTTPException, Query, Request

from backend.dependencies.auth import get_current_admin, get_current_user
from backend.dependencies.services import get_support_service
from backend.models.schemas import SupportTicketCreate, SupportTicketUpdate
from backend.models.user import User
from backend.services.support_service import (
    SupportService,
    SupportTicketNotFoundError,
)


router = APIRouter(tags=["Support and Operations"])


@router.get("/support/tickets")
def list_my_support_tickets(
    current_user: User = Depends(get_current_user),
    service: SupportService = Depends(get_support_service),
):
    return service.list_user_tickets(current_user.id)


@router.post("/support/tickets", status_code=201)
def create_support_ticket(
    request: SupportTicketCreate,
    current_user: User = Depends(get_current_user),
    service: SupportService = Depends(get_support_service),
):
    return service.create_ticket(
        current_user.id,
        request.category,
        request.subject,
        request.message,
    )


@router.get("/admin/operations")
def get_operations_summary(
    _admin: User = Depends(get_current_admin),
    service: SupportService = Depends(get_support_service),
):
    return service.operations_summary()


@router.get("/admin/support/tickets")
def list_support_tickets(
    status: str | None = Query(default=None, max_length=30),
    _admin: User = Depends(get_current_admin),
    service: SupportService = Depends(get_support_service),
):
    allowed_statuses = {"new", "in_progress", "resolved", "closed"}
    if status and status not in allowed_statuses:
        raise HTTPException(status_code=400, detail="Invalid ticket status.")
    return service.list_admin_tickets(status)


@router.patch("/admin/support/tickets/{ticket_id}")
def update_support_ticket(
    ticket_id: int,
    request: SupportTicketUpdate,
    http_request: Request,
    admin: User = Depends(get_current_admin),
    service: SupportService = Depends(get_support_service),
):
    try:
        return service.update_ticket(
            ticket_id,
            request.status,
            request.admin_note,
            admin.id,
            admin.email,
            getattr(http_request.state, "request_id", None),
        )
    except SupportTicketNotFoundError as error:
        raise HTTPException(
            status_code=404,
            detail="Support request not found.",
        ) from error


@router.get("/admin/audit-events")
def list_admin_audit_events(
    limit: int = Query(default=100, ge=1, le=200),
    _admin: User = Depends(get_current_admin),
    service: SupportService = Depends(get_support_service),
):
    return service.list_audit_events(limit)
