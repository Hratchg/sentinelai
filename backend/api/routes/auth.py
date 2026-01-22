"""
Authentication API Endpoints

Handles user registration, login, and token management.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr, validator
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta
import logging

from backend.storage.database import get_db
from backend.storage.models import User
from backend.auth.security import (
    get_password_hash,
    authenticate_user,
    create_access_token,
    get_current_user,
    create_user_directory
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])


class UserRegistration(BaseModel):
    """User registration request."""
    username: str
    email: EmailStr
    password: str
    full_name: str = None

    @validator('username')
    def username_alphanumeric(cls, v):
        """Validate username is alphanumeric."""
        if not v.isalnum():
            raise ValueError('Username must be alphanumeric')
        if len(v) < 3:
            raise ValueError('Username must be at least 3 characters')
        if len(v) > 50:
            raise ValueError('Username must be less than 50 characters')
        return v.lower()

    @validator('password')
    def password_strength(cls, v):
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        return v


class UserResponse(BaseModel):
    """User information response."""
    user_id: str
    username: str
    email: str
    full_name: str = None
    created_at: datetime


class TokenResponse(BaseModel):
    """Token response after login."""
    access_token: str
    token_type: str
    user: UserResponse


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegistration,
    db: AsyncSession = Depends(get_db)
):
    """
    Register a new user account.

    Creates a new user with:
    - Unique username
    - Unique email
    - Hashed password
    - User-specific storage directories

    Returns JWT access token for immediate login.
    """
    # Check if username already exists
    result = await db.execute(
        select(User).where(User.username == user_data.username.lower())
    )
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )

    # Check if email already exists
    result = await db.execute(
        select(User).where(User.email == user_data.email)
    )
    existing_email = result.scalar_one_or_none()

    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create new user
    hashed_password = get_password_hash(user_data.password)

    new_user = User(
        username=user_data.username.lower(),
        email=user_data.email,
        hashed_password=hashed_password,
        full_name=user_data.full_name,
        is_active=True,
        is_superuser=False
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    # Create user-specific directories
    create_user_directory(new_user.id)

    logger.info(f"New user registered: {new_user.username} ({new_user.email})")

    # Create access token
    access_token = create_access_token(
        data={"sub": new_user.id, "username": new_user.username}
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse(
            user_id=new_user.id,
            username=new_user.username,
            email=new_user.email,
            full_name=new_user.full_name,
            created_at=new_user.created_at
        )
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """
    Login with username/email and password.

    Returns JWT access token valid for 30 days.
    """
    user = await authenticate_user(db, form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Update last login timestamp
    user.last_login_at = datetime.utcnow()
    await db.commit()

    # Create access token
    access_token = create_access_token(
        data={"sub": user.id, "username": user.username}
    )

    logger.info(f"User logged in: {user.username}")

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse(
            user_id=user.id,
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            created_at=user.created_at
        )
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Get current authenticated user information.

    Requires valid JWT token in Authorization header.
    """
    return UserResponse(
        user_id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        full_name=current_user.full_name,
        created_at=current_user.created_at
    )


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """
    Logout current user.

    Note: Since JWT is stateless, this is a no-op on the server side.
    Client should discard the token.
    """
    logger.info(f"User logged out: {current_user.username}")

    return {
        "message": "Successfully logged out",
        "detail": "Please discard your access token on the client side"
    }


@router.delete("/account")
async def delete_account(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete current user account.

    WARNING: This will permanently delete:
    - User account
    - All person records
    - All events
    - All video clips

    Gestures are kept (shared global data).
    """
    logger.warning(f"User account deletion requested: {current_user.username}")

    # Delete user (cascade will delete all related data)
    await db.delete(current_user)
    await db.commit()

    logger.info(f"User account deleted: {current_user.username}")

    return {
        "message": "Account successfully deleted",
        "username": current_user.username
    }
