from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any

class UserBase(BaseModel):
    email: EmailStr
    role: str = "user"  # "admin" or "user"

class UserCreate(UserBase):
    password: str

class UserInDB(UserBase):
    hashed_password: str
    last_login_ip: Optional[str] = None
    device_info: Optional[Dict[str, Any]] = None

class UserResponse(UserBase):
    id: Optional[int] = None
    last_login_ip: Optional[str] = None
    device_info: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True
