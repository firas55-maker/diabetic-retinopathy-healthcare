from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional, List
from auth_utils import decode_token
from models import User, RoleEnum
from database import get_db

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user from JWT token"""
    token = credentials.credentials
    token_data = decode_token(token)

    if token_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(User).filter(User.email == token_data.email).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user

def require_role(*allowed_roles: str):
    """Dependency to require specific role(s)"""
    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role.value not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required roles: {', '.join(allowed_roles)}"
            )
        return current_user

    return role_checker

# Specific role dependencies
async def require_doctor(current_user: User = Depends(require_role(RoleEnum.DOCTOR.value))) -> User:
    """Require doctor role"""
    return current_user

async def require_technical_staff(current_user: User = Depends(require_role(RoleEnum.TECHNICAL_STAFF.value))) -> User:
    """Require technical staff role"""
    return current_user

async def require_admin(current_user: User = Depends(require_role(RoleEnum.ADMIN.value))) -> User:
    """Require admin role"""
    return current_user

async def require_doctor_or_admin(current_user: User = Depends(require_role(RoleEnum.DOCTOR.value, RoleEnum.ADMIN.value))) -> User:
    """Require doctor or admin role"""
    return current_user
