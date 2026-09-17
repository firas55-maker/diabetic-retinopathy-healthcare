from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from config import settings
import hashlib
import secrets

# Workaround for bcrypt/passlib compatibility issues
# Use a simpler hashing method for now
try:
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    BCRYPT_AVAILABLE = True
except Exception:
    BCRYPT_AVAILABLE = False
    pwd_context = None

class TokenData:
    """Token payload data"""
    def __init__(self, email: str, user_id: str, role: str):
        self.email = email
        self.user_id = user_id
        self.role = role

def hash_password(password: str) -> str:
    """Hash a password"""
    if BCRYPT_AVAILABLE and pwd_context:
        try:
            return pwd_context.hash(password)
        except Exception:
            pass
    # Fallback: use SHA256 with salt (not ideal, but works when bcrypt fails)
    salt = secrets.token_hex(16)
    hashed = hashlib.sha256((salt + password).encode()).hexdigest()
    return f"sha256${salt}${hashed}"

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    # Try bcrypt first if available
    if BCRYPT_AVAILABLE and pwd_context:
        try:
            # Check if this is a bcrypt hash (starts with $2a$, $2b$, or $2y$)
            if hashed_password.startswith('$2'):
                return pwd_context.verify(plain_password, hashed_password)
        except Exception:
            pass

    # Check if it's SHA256 fallback format
    if hashed_password.startswith('sha256$'):
        parts = hashed_password.split('$')
        if len(parts) == 3:
            salt = parts[1]
            stored_hash = parts[2]
            computed_hash = hashlib.sha256((salt + plain_password).encode()).hexdigest()
            return computed_hash == stored_hash

    # If bcrypt available, try it as last resort
    if BCRYPT_AVAILABLE and pwd_context:
        try:
            return pwd_context.verify(plain_password, hashed_password)
        except Exception:
            return False

    return False

def create_access_token(email: str, user_id: str, role: str, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    if expires_delta is None:
        expires_delta = timedelta(hours=settings.JWT_EXPIRATION_HOURS)

    expire = datetime.now(timezone.utc) + expires_delta
    to_encode = {
        "email": email,
        "user_id": str(user_id),
        "role": role,
        "exp": expire
    }

    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt

def decode_token(token: str) -> Optional[TokenData]:
    """Decode and validate JWT token"""
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        email: str = payload.get("email")
        user_id: str = payload.get("user_id")
        role: str = payload.get("role")

        if email is None or user_id is None or role is None:
            return None

        return TokenData(email=email, user_id=user_id, role=role)
    except JWTError:
        return None
