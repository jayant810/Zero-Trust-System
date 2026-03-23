from fastapi import Request, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from app.auth.jwt_handler import decode_token, TokenPayload
from app.utils.logger import log_security_event
from typing import Optional

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

async def verify_zero_trust(request: Request, token: str = Depends(oauth2_scheme)) -> TokenPayload:
    payload = decode_token(token)
    current_ip = request.client.host

    if not payload:
        log_security_event("unknown", current_ip, "fail", "token_verification", "Invalid or expired token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
    
    # --- ZERO TRUST CONTINUOUS VERIFICATION ---
    current_device = request.headers.get("user-agent", "unknown")

    # 1. IP Matching
    if payload.ip != current_ip:
        log_security_event(payload.sub, current_ip, "fail", "zero_trust_check", f"IP Mismatch. Expected {payload.ip}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Security Alert: IP Mismatch. Expected {payload.ip}, got {current_ip}",
        )
    
    # 2. Device Matching
    if payload.device != current_device:
        log_security_event(payload.sub, current_ip, "fail", "zero_trust_check", f"Device Mismatch. Expected {payload.device}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Security Alert: Device Change detected. Please re-authenticate.",
        )
    
    return payload

# Role-Based Access Control Helper
def require_role(allowed_roles: list[str]):
    async def role_checker(payload: TokenPayload = Depends(verify_zero_trust)):
        if payload.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access Denied: Insufficient Permissions",
            )
        return payload
    return role_checker
