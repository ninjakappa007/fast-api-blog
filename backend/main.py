from fastapi import FastAPI
import logging
from backend.schemas import *
from fastapi import HTTPException, status, Depends
from backend.models import UserModel, PostModel
from typing import Annotated
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from backend.database import Base, engine, get_db
from typing import List
from contextlib import asynccontextmanager
from fastapi.exception_handlers import http_exception_handler, request_validation_exception_handler

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(_app: FastAPI):
    # startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # shutdown
    await engine.dispose()


app = FastAPI(lifespan=lifespan)

# app.mount("/static", StaticFiles(directory="static"), name="static")
# app.mount("/media", StaticFiles(directory="media"), name="media")


@app.get('/', response_model=list[PostResponse], name='home')
@app.get('/posts', response_model=list[PostResponse], name='posts')
async def homepage(db : Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(PostModel).options(selectinload(PostModel.author)))
    posts = result.scalars().all()
    return posts


@app.post('/api/users', response_model=UserResponse, status_code=status.HTTP_201_CREATED)
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
    )
    db.add(new_user) # states the insert
    await db.commit() # executes the insert statement
    await db.refresh(new_user) # reload user obj from database
    return new_user

@app.get('/api/users/{user_id}', response_model=UserResponse)
async def get_user(user_id : int, db : Annotated[AsyncSession, Depends(get_db)]): # dependency injection
    result = await db.execute(select(UserModel).where(UserModel.id == user_id))
    
    user = result.scalars().first()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

@app.delete('/api/users.{user_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id : int, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(UserModel).where(UserModel.id == user_id))
    user = result.scalars().first()
    
    if not user:
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    await db.delete(user)
    await db.commit()

@app.get('/api/users', response_model=List[UserResponse])
async def get_users(db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(UserModel))
    users = result.scalars().all()
    return users
    
@app.get("/api/users/{user_id}/posts", response_model=list[PostResponse])
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

@app.get("/api/posts", response_model=list[PostResponse])
async def get_posts(db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(PostModel).options(selectinload(PostModel.author)))
    posts = result.scalars().all()
    return posts

@app.get("/api/posts/{post_id}", response_model=PostResponse)
async def get_post(post_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(PostModel).where(PostModel.id == post_id))
    post = result.scalars().first()
    if post:
        return post
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

@app.post('/api/posts', response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(post: PostCreate, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(UserModel).where(UserModel.id == post.user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    new_post = PostModel(
        title=post.title,
        content=post.content,
        user_id=post.user_id,
    )
    db.add(new_post)
    await db.commit()
    await db.refresh(new_post, attribute_names=["author"])
    return new_post

@app.put('/api/posts/{post_id}', response_model=PostResponse)
async def update_post_full(post_id, post_data: PostCreate, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(PostModel)
                              .options(selectinload(PostModel))
                              .where(PostModel.id == post_id))
    post = result.scalars().first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    
    if post_data.user_id != post.user_id:
        result = await db.execute(select(UserModel).where(UserModel.id == post_data.user_id))
        user = result.scalars().first()
        
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    # full update
    post.title = post_data.title
    post.content = post_data.content
    post.user_id = post_data.user_id
    
    await db.commit()
    await db.refresh(post)
    return post

@app.patch('/api/posts/{post_id}', response_model=PostResponse)
async def update_post(post_id, post_data: PostCreate, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(PostModel).where(PostModel.id == post_id))
    post = result.scalars().first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    
    update_data = post_data.model_dump(exclude_unset=True)
    # exclude_unset=True filters the fields user actually send instead of populating with default fields
    
    for field, value in update_data.items():
        setattr(post, field, value) # obj, obj_key, obj_value
    
    db.commit()
    db.refresh(post, attribute_names=["author"])
    return post
    
@app.delete('/api/posts/{post_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(post_id, db : Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(PostModel).where(PostModel.id == post_id))
    post = result.scalars().first()
    
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    await db.delete(post)
    await db.commit()
    
    