from typing import Dict, Optional, Any
from app.models.user import UserInDB, UserCreate
from app.utils.security import get_password_hash, verify_password

# --- In-memory mock DB for initial development ---
fake_users_db: Dict[str, UserInDB] = {
    "admin@zero.trust": UserInDB(
        email="admin@zero.trust",
        hashed_password=get_password_hash("admin123"),
        role="admin"
    ),
    "user@zero.trust": UserInDB(
        email="user@zero.trust",
        hashed_password=get_password_hash("user123"),
        role="user"
    )
}

def get_user_by_email(email: str) -> Optional[UserInDB]:
    return fake_users_db.get(email)

def authenticate_user(email: str, password: str) -> Optional[UserInDB]:
    user = get_user_by_email(email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user
