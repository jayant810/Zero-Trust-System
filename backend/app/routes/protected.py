from fastapi import APIRouter, Depends, Request
from app.middleware.zero_trust import require_role, TokenPayload

router = APIRouter(prefix="/api", tags=["api"])

@router.get("/dashboard")
async def get_dashboard(request: Request, payload: TokenPayload = Depends(require_role(["user", "admin"], sensitivity="normal"))):
    risk_score = getattr(request.state, "risk_score", 0)
    return {
        "message": "Welcome to your Secure Dashboard",
        "user": payload.sub,
        "role": payload.role,
        "risk_score": risk_score,
        "note": "A score < 60 is allowed for dashboard access."
    }

@router.get("/admin")
async def get_admin_portal(request: Request, payload: TokenPayload = Depends(require_role(["admin"], sensitivity="strict"))):
    risk_score = getattr(request.state, "risk_score", 0)
    return {
        "message": "Access granted to admin portal",
        "secret_data": "Zero Trust Security is the future.",
        "risk_score": risk_score,
        "note": "A score < 20 is required for admin access."
    }
