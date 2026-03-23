from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from app.services.user_service import authenticate_user
from app.auth.jwt_handler import create_access_token, Token
from app.utils.logger import log_security_event

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login", response_model=Token)
async def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends()):
    ip = request.client.host
    user = authenticate_user(form_data.username, form_data.password)
    
    if not user:
        log_security_event(form_data.username, ip, "fail", "login_attempt", "Incorrect username or password")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Capture Contextual Data for Zero Trust
    user_agent = request.headers.get("user-agent", "unknown")

    # Generate Token with Context
    access_token = create_access_token(
        data={
            "sub": user.email, 
            "role": user.role, 
            "ip": ip, 
            "device": user_agent
        }
    )
    
    log_security_event(user.email, ip, "success", "login_attempt", f"Device: {user_agent}")
    return {"access_token": access_token, "token_type": "bearer"}
