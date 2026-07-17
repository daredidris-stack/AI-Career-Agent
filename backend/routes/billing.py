from fastapi import APIRouter, Depends, Header, HTTPException, Request

from backend.dependencies.auth import get_current_user
from backend.dependencies.services import get_billing_service
from backend.models.user import User
from backend.services.billing_service import BillingConfigurationError, BillingService


router = APIRouter(prefix="/billing", tags=["Billing"])


@router.get("/status")
def billing_status(
    current_user: User = Depends(get_current_user),
    service: BillingService = Depends(get_billing_service),
):
    return service.status(current_user)


@router.post("/checkout")
def create_checkout(
    current_user: User = Depends(get_current_user),
    service: BillingService = Depends(get_billing_service),
):
    try:
        return {"url": service.create_checkout(current_user)}
    except BillingConfigurationError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error


@router.post("/portal")
def create_portal(
    current_user: User = Depends(get_current_user),
    service: BillingService = Depends(get_billing_service),
):
    try:
        return {"url": service.create_portal(current_user)}
    except BillingConfigurationError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error


@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    stripe_signature: str | None = Header(default=None, alias="Stripe-Signature"),
    service: BillingService = Depends(get_billing_service),
):
    try:
        service.handle_webhook(await request.body(), stripe_signature)
    except (BillingConfigurationError, ValueError) as error:
        raise HTTPException(status_code=400, detail="Invalid webhook.") from error
    return {"received": True}
