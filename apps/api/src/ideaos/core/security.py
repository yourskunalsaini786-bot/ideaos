"""Security utilities: JWT, password hashing, Clerk integration."""
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from jose import jwt, JWTError
from passlib.context import CryptContext
from pydantic import BaseModel

from ideaos.core.config import get_settings

settings = get_settings()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class TokenData(BaseModel):
    """Decoded JWT token data."""
    sub: str  # user_id
    workspace_id: Optional[str] = None
    role: str = "member"
    email: Optional[str] = None
    exp: int
    iat: int


def create_access_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Create JWT access token."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc)})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(data: Dict[str, Any]) -> str:
    """Create JWT refresh token."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc), "type": "refresh"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str) -> TokenData:
    """Decode and validate JWT token."""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        return TokenData(**payload)
    except JWTError as e:
        raise ValueError(f"Invalid token: {e}")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


class ClerkUser(BaseModel):
    """Clerk user data from webhook."""
    id: str
    email_addresses: list[Dict[str, Any]]
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    image_url: Optional[str] = None
    public_metadata: Dict[str, Any] = {}
    private_metadata: Dict[str, Any] = {}
    created_at: int
    updated_at: int


def extract_clerk_user_data(payload: Dict[str, Any]) -> ClerkUser:
    """Extract user data from Clerk webhook payload."""
    user_data = payload.get("data", {})
    return ClerkUser(**user_data)