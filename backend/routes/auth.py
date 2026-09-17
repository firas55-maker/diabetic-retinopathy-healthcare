from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import timedelta
from models import User, RoleEnum
from schemas import RegisterRequest, LoginRequest, TokenResponse, UserResponse
from auth_utils import hash_password, verify_password, create_access_token
from dependencies import get_current_user
from database import get_db
from config import settings

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    request: RegisterRequest,
    db: Session = Depends(get_db)
) -> TokenResponse:
    """
    Register a new user (doctor or technical_staff only)

    - **email**: User email address
    - **password**: Password (minimum 8 characters)
    - **full_name**: User's full name
    - **role**: "doctor" or "technical_staff"
    - **hospital_id**: UUID of the hospital
    - **specialty**: Optional specialty (recommended for doctors)
    """

    # Validate role
    allowed_roles = [RoleEnum.DOCTOR.value, RoleEnum.TECHNICAL_STAFF.value]
    if request.role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role. Allowed roles: {', '.join(allowed_roles)}"
        )

    # Check if email already exists
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create new user
    try:
        hashed_password = hash_password(request.password)
        new_user = User(
            email=request.email,
            hashed_password=hashed_password,
            full_name=request.full_name,
            role=RoleEnum(request.role),
            hospital_id=request.hospital_id,
            specialty=request.specialty
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        # Generate JWT token
        expires_delta = timedelta(hours=settings.JWT_EXPIRATION_HOURS)
        access_token = create_access_token(
            email=new_user.email,
            user_id=new_user.id,
            role=new_user.role.value,
            expires_delta=expires_delta
        )

        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=int(expires_delta.total_seconds())
        )
    except IntegrityError as e:
        db.rollback()
        # Check if it's a foreign key constraint on hospital_id
        if "hospital_id_fkey" in str(e):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The specified hospital_id does not exist"
            )
        # Re-raise other integrity errors with generic message
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid data provided"
        )

@router.post("/login", response_model=TokenResponse)
async def login(
    request: LoginRequest,
    db: Session = Depends(get_db)
) -> TokenResponse:
    """
    Login user and get JWT token

    - **email**: User email address
    - **password**: User password
    """

    # Find user by email
    user = db.query(User).filter(User.email == request.email).first()
    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # Generate JWT token
    expires_delta = timedelta(hours=settings.JWT_EXPIRATION_HOURS)
    access_token = create_access_token(
        email=user.email,
        user_id=user.id,
        role=user.role.value,
        expires_delta=expires_delta
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=int(expires_delta.total_seconds())
    )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
) -> UserResponse:
    """
    Get current authenticated user information

    Returns the profile of the currently authenticated user
    """
    return UserResponse.model_validate(current_user)
