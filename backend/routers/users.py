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
from backend.auth import CurrentUser

router = APIRouter()

@router.get('/{user_id}', response_model=UserPublic)
async def get_user(user_id : int, db : Annotated[AsyncSession, Depends(get_db)]): # dependency injection
    result = await db.execute(select(UserModel).where(UserModel.id == user_id))
    
    user = result.scalars().first()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.get('', response_model=List[UserPublic])
async def get_users(db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(UserModel))
    users = result.scalars().all()
    return users


@router.post('', response_model=UserPrivate, status_code=status.HTTP_201_CREATED)
async def create_user(user : UserCreate, db : Annotated[AsyncSession, Depends(get_db)]): # dependency injection
    result = await db.execute(select(UserModel).where(UserModel.username == user.username))
    
    existing_user = result.scalars().first() # gives value if not available returns None
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Username already exists")
    
    result = await db.execute(select(UserModel).where(UserModel.email == user.email))
    existing_email = result.scalars().first() # gives value if not available returns None
    if existing_email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Email already exists")
    
    new_user = UserModel(
        username = user.username,
        email = user.email,
        password_hash = hash_password(user.password)
    )
    db.add(new_user) # states the insert
    await db.commit() # executes the insert statement
    await db.refresh(new_user) # reload user obj from database
    return new_user


@router.delete('/{user_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id : int, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(UserModel).where(UserModel.id == user_id))
    user = result.scalars().first()
    
    if not user:
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    await db.delete(user)
    await db.commit()

    
@router.get("/{user_id}/posts", response_model=list[PostResponse])
async def get_user_posts(user_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(UserModel).where(UserModel.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    result = await db.execute(
                            select(PostModel)
                            .options(selectinload(PostModel.author))
                            .where(PostModel.user_id == user_id))
    posts = result.scalars().all()
    return posts

