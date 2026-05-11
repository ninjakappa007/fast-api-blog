from backend.schemas import *
from backend.models import UserModel, PostModel
from typing import Annotated
from fastapi import HTTPException, status, Depends, APIRouter
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from backend.database import Base, engine, get_db
from typing import List
from contextlib import asynccontextmanager
from datetime import timedelta
from fastapi.security import OAuth2PasswordRequestForm
from backend.auth import *
from backend.config import settings



router = APIRouter()

@router.post('/auth_token', response_model = Token)
async def login_for_auth_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db : Annotated[AsyncSession, Depends(get_db)]
):
    # Lookup user by email
    # OAuth2PasswordRequestForm uses "username" field, but we treat it as email 
    result = await db.execute(select(UserModel).where(UserModel.email == form_data.username))
    user = result.scalars().first()
    
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED,
                            detail = "Incorrect email or password",
                            headers = {"WWW-Authenticate": "Bearer"})
    
    # Create access token with user id as subject
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta = access_token_expires
    )
    refresh_token = create_refresh_token(data={"sub": str(user.id)})

    return Token(access_token = access_token, refresh_token = refresh_token, token_type = "bearer")


## get_current_user
@router.get("/me", response_model=UserPrivate)
async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get the currently authenticated user."""
    user_id = verify_access_token(token)
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Validate user_id is a valid integer (defense against malformed JWT)
    try:
        user_id_int = int(user_id)
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    result = await db.execute(
        select(UserModel).where(UserModel.id == user_id_int),
    )
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user
    
    