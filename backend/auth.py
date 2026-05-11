from datetime import UTC, datetime, timedelta
import jwt
from fastapi.security import OAuth2PasswordBearer
from pwdlib import PasswordHash
from backend.config import settings
from typing import Annotated
from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.models import UserModel, PostModel
from backend.database import get_db


password_hash = PasswordHash.recommended()

# Extracts bearer token from authorization header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='api/auth_token')

def hash_password(password : str) -> str:
    return password_hash.hash(password)

def verify_password(plain_password : str, hashed_password : str) -> bool:
    return password_hash.verify(plain_password, hashed_password)

def create_access_token(data : dict, expires_delta : timedelta | None = None) -> str:
    """ 
        Create a JWT access token
            Args:
                data -> claims to store inside jwt
                expires_delta -> optional custom expiry time, defaults to 30min configured in config.py
            Returns:
                str -> jwt access token
          
    """
    to_encode = data.copy() # using copy to prevent modifying original data
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(
            minutes = settings.access_token_expire_minutes
        )
    to_encode.update({
        "exp": expire,
        "type": "access"
        }) # adding exp to claims
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.secret_key.get_secret_value(),
        algorithm=settings.algorithm
    )
    return encoded_jwt

def verify_access_token(token : str) -> str | None:
    """ Verify access token and return the sub from claims if valid """
    try:
        payload = jwt.decode(
            token,
            settings.secret_key.get_secret_value(),
            algorithms = [settings.algorithm],
            options = {"require" : ["exp", "sub"]}
        )
        if payload.get("type") != "access":
            return None

    except jwt.InvalidTokenError:
        return None
    else:
        return payload.get("sub")

def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(days=7)

    to_encode.update({
        "exp": expire,
        "type": "refresh"
    })

    encoded_jwt = jwt.encode(
        to_encode,
        settings.secret_key.get_secret_value(),
        algorithm=settings.algorithm
    )
    return encoded_jwt

def verify_refresh_token(token : str) -> str | None:
    """ Verify refresh token and return the sub from claims if valid """
    try:
        payload = jwt.decode(
            token,
            settings.secret_key.get_secret_value(),
            algorithms = [settings.algorithm],
            options = {"require" : ["exp", "sub"]}
        )
        if payload.get("type") != "refresh":
            return None
        
    except jwt.InvalidTokenError:
        return None
    else:
        return payload.get("sub")
    
async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    user_id = verify_access_token(token)
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    result = await db.execute(select(UserModel).where(UserModel.id == int(user_id)))
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

    
"""
This creates a reusable type alias for dependency injection.

Breaking it down:
Depends(get_current_user) — tells FastAPI to run get_current_user (which likely extracts and validates the JWT token,
    then returns the user) before the route handler executes.
Annotated[UserModel, Depends(...)] — combines the type hint (UserModel) with the dependency metadata into one annotation.
CurrentUser = ... — saves it as a reusable alias so you don't repeat yourself.

Instead of writing this in every protected route:
async def get_posts(user: Annotated[UserModel, Depends(get_current_user)]):

You just write:
async def get_posts(user: CurrentUser):
"""
CurrentUser = Annotated[UserModel, Depends(get_current_user)]