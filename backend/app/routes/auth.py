from fastapi import APIRouter, Depends, HTTPException, status, Request, Header
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from app.services.user_service import authenticate_user
from app.auth.jwt_handler import create_access_token, create_refresh_token, decode_token, Token
from app.utils.logger import log_security_event
from app.utils.database import SessionLocal, TokenBlacklist
from slowapi import Limiter
from slowapi.util import get_remote_address
from typing import Optional

limiter = Limiter(key_func=get_remote_address)
router = APIRouter(prefix="/auth", tags=["auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

@router.post("/login", response_model=Token)
@limiter.limit("5/minute")
async def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), x_device_fingerprint: Optional[str] = Header(None)):
    ip = request.client.host
    user = authenticate_user(form_data.username, form_data.password)

    if not user:
        log_security_event(form_data.username, ip, "fail", "login_attempt", "Incorrect username or password")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_agent = request.headers.get("user-agent", "unknown")
    fingerprint = x_device_fingerprint or "unknown"

    # Generate Dual Tokens with Fingerprint
    token_data = {
        "sub": user.email,
        "role": user.role,
        "ip": ip,
        "device": user_agent,
        "fingerprint": fingerprint
    }
    access_token = create_access_token(data=token_data)
    refresh_token = create_refresh_token(data=token_data)

    log_security_event(user.email, ip, "success", "login_attempt", f"Fingerprint: {fingerprint[:20]}...")  
    return {
        "access_token": access_token, 
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/refresh", response_model=Token)
async def refresh(request: Request, refresh_token: str, x_device_fingerprint: Optional[str] = Header(None)):
    ip = request.client.host
    payload = decode_token(refresh_token)

    if not payload or payload.type != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    # Check revocation & Replay Protection
    db = SessionLocal()
    used = db.query(TokenBlacklist).filter(TokenBlacklist.jti == payload.jti).first()
    if used:
        db.close()
        log_security_event(payload.sub, ip, "fail", "token_replay", f"Refresh token reused: {payload.jti}")
        raise HTTPException(status_code=401, detail="Token has been used or revoked.")

    # Strict Context Validation for Refresh
    current_fingerprint = x_device_fingerprint or "unknown"
    if payload.fingerprint != current_fingerprint:
         db.close()
         log_security_event(payload.sub, ip, "fail", "context_mismatch", f"Refresh Fingerprint Mismatch.")
         raise HTTPException(status_code=403, detail="Context Mismatch. Please login again.")

    # Mark as used to prevent replay
    db.add(TokenBlacklist(jti=payload.jti, user_sub=payload.sub, token_type="refresh", is_used=True))
    db.commit()
    db.close()

    # Issue new pair
    token_data = {
        "sub": payload.sub,
        "role": payload.role,
        "ip": ip,
        "device": request.headers.get("user-agent", "unknown"),
        "fingerprint": current_fingerprint
    }
    return {
        "access_token": create_access_token(data=token_data),
        "refresh_token": create_refresh_token(data=token_data),
        "token_type": "bearer"
    }

@router.post("/logout")
async def logout(token: str = Depends(oauth2_scheme)):
    payload = decode_token(token)
    if payload:
        db = SessionLocal()
        db.add(TokenBlacklist(jti=payload.jti, user_sub=payload.sub, token_type=payload.type))
        db.commit()
        db.close()
    return {"message": "Successfully logged out"}
