from fastapi import Request, HTTPException, status, Depends, Header
from fastapi.security import OAuth2PasswordBearer
from app.auth.jwt_handler import decode_token, TokenPayload
from app.utils.logger import log_security_event
from app.utils.database import SessionLocal, TokenBlacklist
from app.services.risk_service import RiskService
from typing import Optional

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

async def verify_zero_trust(request: Request, token: str = Depends(oauth2_scheme), x_device_fingerprint: Optional[str] = Header(None)) -> TokenPayload:
    payload = decode_token(token)
    current_ip = request.client.host

    if not payload or payload.type != "access":
        log_security_event("unknown", current_ip, "fail", "token_verification", "Invalid or non-access token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    # --- PHASE 1: REVOCATION CHECK ---
    db = SessionLocal()
    revoked = db.query(TokenBlacklist).filter(TokenBlacklist.jti == payload.jti).first()
    db.close()
    if revoked:
        log_security_event(payload.sub, current_ip, "fail", "token_verification", f"Revoked token used: {payload.jti}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session invalidated.")

    # --- PHASE 3: DYNAMIC RISK EVALUATION ---
    current_fingerprint = x_device_fingerprint or "unknown"
    risk_score = RiskService.calculate_risk_score(
        current_ip, 
        current_fingerprint, 
        payload.ip, 
        payload.fingerprint, 
        payload.sub
    )

    # Attach risk score to request for audit
    request.state.risk_score = risk_score
    
    # 3. Policy Enforcement based on Score
    # For general routes, we block if risk_score >= 60
    action = RiskService.get_action_for_score(risk_score, sensitivity="normal")
    
    if action == "BLOCK":
        log_security_event(payload.sub, current_ip, "fail", "risk_engine", f"Request Blocked. Risk Score: {risk_score}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Security Alert: Dynamic Risk Blocked this Request. Risk Score: {risk_score}",
        )
    elif action == "MONITOR":
        log_security_event(payload.sub, current_ip, "info", "risk_engine", f"High Risk Request Allowed. Risk Score: {risk_score}")

    return payload

# Role-Based Access Control Helper (with sensitivity layer)
def require_role(allowed_roles: list[str], sensitivity: str = "normal"):
    async def role_checker(request: Request, payload: TokenPayload = Depends(verify_zero_trust)):
        if payload.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access Denied: Insufficient Permissions",
            )
        
        # Re-evaluate with strict sensitivity for Admin routes
        risk_score = getattr(request.state, "risk_score", 0)
        action = RiskService.get_action_for_score(risk_score, sensitivity=sensitivity)
        
        if action == "BLOCK":
            log_security_event(payload.sub, request.client.host, "fail", "risk_engine", f"Admin Blocked. Risk: {risk_score}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Strict Security Policy: Risk ({risk_score}) exceeds threshold for this resource.",
            )
            
        return payload
    return role_checker
