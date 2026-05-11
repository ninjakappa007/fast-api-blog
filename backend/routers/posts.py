from fastapi import FastAPI
import logging
from backend.schemas import *
from fastapi import HTTPException, status, Depends, APIRouter
from backend.models import PostModel, UserModel
from typing import Annotated
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from backend.database import Base, engine, get_db
from typing import List
from contextlib import asynccontextmanager
from fastapi.exception_handlers import http_exception_handler, request_validation_exception_handler
from backend.auth import CurrentUser

router = APIRouter()

@router.get('', response_model=list[PostResponse])
async def get_posts(db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(PostModel).options(selectinload(PostModel.author)))
    posts = result.scalars().all()
    return posts


# /api/posts
@router.post('', response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(post: PostCreate, current_user : CurrentUser, db: Annotated[AsyncSession, Depends(get_db)]):
    new_post = PostModel(
        title=post.title,
        content=post.content,
        user_id=current_user.id,
    )
    db.add(new_post)
    await db.commit()
    await db.refresh(new_post, attribute_names=["author"])
    return new_post


@router.get('/{post_id}', response_model=PostResponse)
async def get_post(post_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(PostModel).options(selectinload(PostModel.author)).where(PostModel.id == post_id))
    post = result.scalars().first()
    if post:
        return post
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")


@router.put('/{post_id}', response_model=PostResponse)
async def update_post_full(post_id, post_data: PostCreate, current_user: CurrentUser, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(PostModel)
                              .options(selectinload(PostModel))
                              .where(PostModel.id == post_id))
    post = result.scalars().first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    
    if post.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail = "You don't have permissions to edit this post")
    
    # full update
    post.title = post_data.title
    post.content = post_data.content
    post.user_id = current_user.id
    
    await db.commit()
    await db.refresh(post)
    return post


@router.patch('/{post_id}', response_model=PostResponse)
async def update_post(post_id, post_data: PostCreate, current_user : CurrentUser, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(PostModel).where(PostModel.id == post_id))
    post = result.scalars().first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    
    if post.user_id != current_user.id:
        raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, detail = "You dont have permission to edit this post")
    
    update_data = post_data.model_dump(exclude_unset=True)
    # exclude_unset=True filters the fields user actually send instead of populating with default fields
    
    for field, value in update_data.items():
        setattr(post, field, value) # obj, obj_key, obj_value
    
    db.commit()
    db.refresh(post, attribute_names=["author"])
    return post
    
    
@router.delete('/{post_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(post_id, current_user : CurrentUser, db : Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(PostModel).where(PostModel.id == post_id))
    post = result.scalars().first()
    
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    
    if post.user_id == current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You dont have permission to delete this post")
    await db.delete(post)
    await db.commit()