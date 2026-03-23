from fastapi import APIRouter, Depends
from app.middleware.zero_trust import verify_zero_trust, require_role
from app.auth.jwt_handler import TokenPayload

router = APIRouter(prefix="/api", tags=["protected"])

@router.get("/dashboard")
async def get_dashboard(payload: TokenPayload = Depends(verify_zero_trust)):
    return {
        "message": f"Welcome to the Zero Trust Dashboard, {payload.sub}!",
        "role": payload.role,
        "context": {
            "ip": payload.ip,
            "device": payload.device
        }
    }

@router.get("/admin")
async def get_admin_portal(payload: TokenPayload = Depends(require_role(["admin"]))):
    return {
        "message": "Access granted to admin portal",
        "secret_data": "Zero Trust Security is the future."
    }

@router.get("/data")
async def get_public_data(payload: TokenPayload = Depends(verify_zero_trust)):
    return {
        "data": "This is sensitive data accessible to all authenticated users."
    }
