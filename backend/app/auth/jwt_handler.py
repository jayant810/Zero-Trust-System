from datetime import datetime, timedelta
import uuid
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from pydantic import BaseModel

# --- Configuration (Should be moved to environment variables later) ---
SECRET_KEY = "SUPER_SECRET_KEY_REPLACE_ME"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15  # Short-lived for Zero Trust
REFRESH_TOKEN_EXPIRE_DAYS = 7     # Long-lived refresh token

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class TokenPayload(BaseModel):
    sub: str = None  # user email
    role: str = None
    ip: str = None
    device: str = None
    fingerprint: str = None  # Enhanced Device Fingerprint
    jti: str = None  # Unique token ID
    type: str = "access" # 'access' or 'refresh'
    exp: Optional[int] = None

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({
        "exp": expire,
        "jti": str(uuid.uuid4()),
        "type": "access"
    })
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

    to_encode.update({
        "exp": expire,
        "jti": str(uuid.uuid4()),
        "type": "refresh"
    })
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_token(token: str) -> Optional[TokenPayload]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return TokenPayload(**payload)
    except (JWTError, Exception):
        return None
