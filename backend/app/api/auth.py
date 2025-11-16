"""
Authentication API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.config.database import get_db
from app.models.user import User
from app.middleware.auth import (
    verify_password,
    create_access_token,
    create_refresh_token,
    get_password_hash,
)
from app.config.settings import settings
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/api", tags=["Authentication"])


class TokenResponse(BaseModel):
    access: str
    refresh: str
    token_type: str = "bearer"
    user: Optional[dict] = None


class LoginRequest(BaseModel):
    username: str
    password: str


@router.post("/token", response_model=TokenResponse)
async def login(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    """Login endpoint - Get JWT tokens"""
    # Validate input
    if not request.username or not request.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username and password are required"
        )
    
    result = await db.execute(select(User).where(User.username == request.username))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password. Please check your credentials and try again.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password. Please check your credentials and try again.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account has been deactivated. Please contact support for assistance."
        )
    
    # Create tokens
    access_token = create_access_token(data={"sub": user.username})
    refresh_token = create_refresh_token(data={"sub": user.username})
    
    return TokenResponse(
        access=access_token,
        refresh=refresh_token,
        user={
            "id": user.id,
            "username": user.username,
            "email": user.email,
        }
    )


@router.post("/register")
async def register(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    """Register a new user (development only)"""
    # Validate input
    if not request.username or not request.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username and password are required"
        )
    
    # Validate username length
    if len(request.username) < 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username must be at least 3 characters long"
        )
    
    # Validate password strength
    if len(request.password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters long"
        )
    
    # Check if user already exists
    result = await db.execute(select(User).where(User.username == request.username))
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This username is already taken. Please choose a different username."
        )
    
    try:
        # Create new user
        password_hash = get_password_hash(request.password)
        user = User(
            username=request.username,
            email=None,
            password_hash=password_hash,
            is_active=True,
            is_superuser=False,
            is_staff=False,
        )
        
        db.add(user)
        await db.commit()
        await db.refresh(user)
        
        # Create tokens for immediate login
        access_token = create_access_token(data={"sub": user.username})
        refresh_token = create_refresh_token(data={"sub": user.username})
        
        return TokenResponse(
            access=access_token,
            refresh=refresh_token,
            user={
                "id": user.id,
                "username": user.username,
                "email": user.email,
            }
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating your account. Please try again."
        )


@router.post("/token/refresh")
async def refresh_token(refresh_token: str, db: AsyncSession = Depends(get_db)):
    """Refresh access token"""
    from jose import JWTError, jwt
    
    try:
        payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        token_type: str = payload.get("type")
        
        if username is None or token_type != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    access_token = create_access_token(data={"sub": user.username})
    
    return {"access": access_token, "token_type": "bearer"}

