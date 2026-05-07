from fastapi import FastAPI
from pydantic import BaseModel
import logging
from backend.schemas import *
from fastapi import HTTPException, status, Depends
from contextlib import asynccontextmanager
from backend.models import UserModel, PostModel
from typing import Annotated
from sqlalchemy import select
from sqlalchemy.orm import Session
from backend.database import Base, engine, get_db
from fastapi.staticfiles import StaticFiles
from typing import List

logger = logging.getLogger(__name__)

# runs on startup
Base.metadata.create_all(bind=engine)

app = FastAPI()

# app.mount("/static", StaticFiles(directory="static"), name="static")
# app.mount("/media", StaticFiles(directory="media"), name="media")


@app.get('/', response_model=list[PostResponse], name='home')
@app.get('/posts', response_model=list[PostResponse], name='posts')
def homepage(db : Annotated[Session, Depends(get_db)]):
    result = db.execute(select(PostModel))
    posts = result.scalars().all()
    return posts


@app.post('/api/users', response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user : UserCreate, db : Annotated[Session, Depends(get_db)]): # dependency injection
    result = db.execute(select(UserModel).where(UserModel.username == user.username))
    
    existing_user = result.scalars().first() # gives value if not available returns None
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Username already exists")
    
    result = db.execute(select(UserModel).where(UserModel.email == user.email))
    existing_email = result.scalars().first() # gives value if not available returns None
    if existing_email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Email already exists")
    
    new_user = UserModel(
        username = user.username,
        email = user.email,
    )
    db.add(new_user) # states the insert
    db.commit() # executes the insert statement
    db.refresh(new_user) # reload user obj from database
    return new_user


@app.get('/api/users/{user_id}', response_model=UserResponse)
def get_user(user_id : int, db : Annotated[Session, Depends(get_db)]): # dependency injection
    result = db.execute(select(UserModel).where(UserModel.id == user_id))
    
    user = result.scalars().first()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@app.get('/api/users', response_model=List[UserResponse])
def get_users(db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(UserModel))
    users = result.scalars().all()
    return users
    
    
@app.get("/api/users/{user_id}/posts", response_model=list[PostResponse])
def get_user_posts(user_id: int, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(UserModel).where(UserModel.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    result = db.execute(select(PostModel).where(PostModel.user_id == user_id))
    posts = result.scalars().all()
    return posts


@app.get("/api/posts", response_model=list[PostResponse])
def get_posts(db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(PostModel))
    posts = result.scalars().all()
    return posts


@app.get("/api/posts/{post_id}", response_model=PostResponse)
def get_post(post_id: int, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(PostModel).where(PostModel.id == post_id))
    post = result.scalars().first()
    if post:
        return post
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")


@app.post('/api/posts', response_model=PostResponse, status_code=status.HTTP_201_CREATED)
def create_post(post: PostCreate, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(UserModel).where(UserModel.id == post.user_id))
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
    db.commit()
    db.refresh(new_post)
    return new_post