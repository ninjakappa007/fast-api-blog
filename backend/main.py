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

from backend.routers import posts, users, login

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
app.include_router(login.router, prefix='/api', tags=['login'])
app.include_router(users.router, prefix='/api/users', tags=['users'])
app.include_router(posts.router, prefix='/api/posts', tags=['posts'])

# app.mount("/static", StaticFiles(directory="static"), name="static")
# app.mount("/media", StaticFiles(directory="media"), name="media")


@app.get('/', response_model=list[PostResponse], name='home')
@app.get('/posts', response_model=list[PostResponse], name='posts')
async def homepage(db : Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(PostModel).options(selectinload(PostModel.author)))
    posts = result.scalars().all()
    return posts


    
    