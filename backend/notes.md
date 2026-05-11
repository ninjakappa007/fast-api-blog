# FastAPI Notes (Project Reference)

## Data Flow
1. User makes API call
2. ASGI server (Uvicorn) receives request
3. Pydantic validates incoming data (request body, query params)
4. SQLAlchemy stores/retrieves data from DB
5. Pydantic validates outgoing data (`response_model`)
6. ASGI server sends response

---

## Project Structure
```
backend/
├── main.py          # App entry, lifespan, router registration
├── config.py        # Settings from .env using pydantic-settings
├── database.py      # Async engine, session factory, Base, get_db
├── models.py        # SQLAlchemy ORM models
├── schemas.py       # Pydantic schemas (request/response validation)
├── auth.py          # JWT utils, password hashing, get_current_user dependency
├── routers/
│   ├── login.py     # Auth token endpoint, /me
│   ├── users.py     # CRUD for users
│   └── posts.py     # CRUD for posts
└── .env             # Environment variables
```

---

## Running the App
```bash
fastapi dev    # development with auto-reload
fastapi run    # production (no auto-reload)
```
- Swagger docs: http://localhost:8000/docs

---

## Core Concepts

### 1. App & Lifespan (main.py)
```python
@asynccontextmanager
async def lifespan(_app: FastAPI):
    # STARTUP: create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # SHUTDOWN: dispose engine
    await engine.dispose()

app = FastAPI(lifespan=lifespan)
```
- Replaces deprecated `@app.on_event("startup")` / `@app.on_event("shutdown")`
- Tables are created on startup (dev only — use Alembic for production migrations)

### 2. Routers
```python
app.include_router(login.router, prefix='/api', tags=['login'])
app.include_router(users.router, prefix='/api/users', tags=['users'])
app.include_router(posts.router, prefix='/api/posts', tags=['posts'])
```
- `prefix` — prepended to all routes in that router
- `tags` — groups endpoints in Swagger UI
- Route order matters: `/posts/me` must come BEFORE `/posts/{post_id}`

---

## Pydantic

### Schemas (Request Validation)
```python
class PostCreate(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    content: str = Field(min_length=1)
```
- Validates request body automatically
- Invalid data → 422 Unprocessable Entity with detailed errors

### Schemas (Response Validation)
```python
class PostResponse(PostBase):
    model_config = ConfigDict(from_attributes=True)  # REQUIRED for ORM objects
    id: int
    user_id: int
    date_posted: datetime
    author: UserPublic  # nested relationship
```
- `from_attributes=True` — allows Pydantic to read SQLAlchemy model attributes
- `response_model=PostResponse` on the route enforces output shape

### Key Pydantic Types
| Type | Use |
|------|-----|
| `EmailStr` | Email validation |
| `SecretStr` | Hides value in logs, access via `.get_secret_value()` |
| `Field(min_length=, max_length=)` | String constraints |
| `str \| None = None` | Optional field |

### ConfigDict Options
- `from_attributes=True` — read from ORM objects (replaces old `orm_mode`)
- `env_file='.env'` — for Settings classes (pydantic-settings)

---

## SQLAlchemy (Async)

### Database Setup (database.py)
```python
SQLALCHEMY_DB_URL = 'sqlite+aiosqlite:///./blog.db'

engine = create_async_engine(SQLALCHEMY_DB_URL, connect_args={"check_same_thread": False})
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
```
- `expire_on_commit=False` — prevents attributes from expiring after commit (important for async)
- `get_db` is a dependency that provides a session per request

### Models (models.py)
```python
class UserModel(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    posts: Mapped[list[PostModel]] = relationship(back_populates="author", cascade="all, delete-orphan")
```

### CRUD Operations
```python
# CREATE
db.add(new_post)
await db.commit()
await db.refresh(new_post, attribute_names=["author"])

# READ
result = await db.execute(select(PostModel).where(PostModel.id == post_id))
post = result.scalars().first()

# UPDATE
post.title = new_title
await db.commit()
await db.refresh(post)

# DELETE
await db.delete(post)
await db.commit()
```

### ⚠️ Relationships & Eager Loading
Async SQLAlchemy CANNOT lazy-load relationships. Always use:
```python
# selectinload — separate SELECT query for relationship (good for collections)
select(PostModel).options(selectinload(PostModel.author))

# joinedload — JOIN in same query (good for single objects)
select(PostModel).options(joinedload(PostModel.author))
```
Without this → `MissingGreenlet` error at response time.

---

## Dependency Injection

### How it works
```python
async def get_post(post_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
```
- `Depends(get_db)` — FastAPI calls `get_db()`, injects the result as `db`
- Works with generators (yield), async generators, and regular functions
- Dependencies can depend on other dependencies (chain)

### Reusable Type Aliases
```python
# Define once
CurrentUser = Annotated[UserModel, Depends(get_current_user)]

# Use everywhere
async def create_post(current_user: CurrentUser, ...):
```

### Common Dependencies in this project
| Dependency | Provides |
|-----------|----------|
| `Depends(get_db)` | AsyncSession |
| `Depends(oauth2_scheme)` | Bearer token string |
| `Depends(get_current_user)` | Authenticated UserModel |

---

## Authentication (JWT)

### Flow
1. User POSTs credentials to `/api/auth_token`
2. Server validates, returns `access_token` + `refresh_token`
3. Client sends `Authorization: Bearer <access_token>` on protected routes
4. `get_current_user` dependency extracts & verifies token

### OAuth2PasswordBearer
```python
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='api/auth_token')
```
- Tells FastAPI where the token endpoint is (for Swagger UI "Authorize" button)
- Extracts token from `Authorization: Bearer ...` header
- `tokenUrl` must match your actual login route path

### Token Creation
```python
def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, secret_key, algorithm=algorithm)
```
- Always include `"type"` claim to distinguish access vs refresh tokens
- `"sub"` claim holds user ID

### Protected Route
```python
@router.post('', response_model=PostResponse)
async def create_post(current_user: CurrentUser, ...):
    # current_user is already authenticated
    new_post = PostModel(user_id=current_user.id, ...)
```

---

## Configuration (pydantic-settings)

```python
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')
    secret_key: SecretStr          # REQUIRED — must be in .env
    algorithm: str = 'HS256'       # has default
    access_token_expire_minutes: int = 30

settings = Settings()
```
- Reads from `.env` file AND environment variables
- Case insensitive: `SECRET_KEY` in .env → `secret_key` in code
- `.env` path is relative to where you run the app (project root)
- No default = required (app crashes if missing)

---

## Error Handling

### HTTP Exceptions
```python
raise HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Post not found"
)
```

### Common Status Codes
| Code | When |
|------|------|
| 200 | Success (default for GET) |
| 201 | Created (set via `status_code=` param) |
| 204 | No Content (DELETE) |
| 400 | Bad request (duplicate username) |
| 401 | Unauthorized (bad token/credentials) |
| 403 | Forbidden (not your resource) |
| 404 | Not found |
| 422 | Validation error (Pydantic) |
| 500 | Server error (usually a bug) |

---

## Debugging Tips

| Error | Cause | Fix |
|-------|-------|-----|
| `MissingGreenlet` | Lazy-loading relationship in async | Add `selectinload()` / `joinedload()` |
| `ResponseValidationError` | Return data doesn't match `response_model` | Check schema fields, add `from_attributes=True` |
| 422 Unprocessable Entity | Request body/params failed validation | Check Pydantic schema constraints |
| `PydanticUserError: not fully defined` | `from __future__ import annotations` in models | Remove it, or use string refs in Annotated |
| Circular import | Router A imports from Router B and vice versa | Move shared code to a separate module (auth.py, dependencies.py) |
| Method Not Allowed (405) | Wrong decorator (`@router.app` instead of `@router.post`) | Use correct HTTP method decorator |
| Token URL mismatch | `tokenUrl` in OAuth2PasswordBearer doesn't match actual route | Make them match (include router prefix) |

---

## Django vs FastAPI Quick Reference

| Django | FastAPI |
|--------|---------|
| `models.py` (Django ORM) | `models.py` (SQLAlchemy) |
| `serializers.py` (DRF) | `schemas.py` (Pydantic) |
| `views.py` / `viewsets.py` | `routers/*.py` |
| `urls.py` | `app.include_router(...)` in main.py |
| `settings.py` | `config.py` (pydantic-settings + .env) |
| `request.user` | `current_user: CurrentUser` (dependency) |
| `makemigrations` / `migrate` | Alembic (`alembic revision --autogenerate`) |
| Lazy loading works | Must eagerly load (selectinload/joinedload) |
| `manage.py runserver` | `fastapi dev` |
| Middleware classes | `@app.middleware("http")` or Starlette middleware |
| `@login_required` | `Depends(get_current_user)` |
| Auto admin panel | None built-in (use SQLAdmin) |

---

## Useful Patterns

### Partial Update (PATCH)
```python
update_data = post_data.model_dump(exclude_unset=True)
for field, value in update_data.items():
    setattr(post, field, value)
```
- `exclude_unset=True` — only updates fields the client actually sent

### Multiple Decorators on One Route
```python
@app.get('/', response_model=list[PostResponse])
@app.get('/posts', response_model=list[PostResponse])
async def homepage(...):
```

### Computed Properties in Models
```python
@property
def image_path(self) -> str:
    if self.image_file:
        return f"/media/profile_pics/{self.image_file}"
    return "/static/profile_pics/default.jpg"
```
- Pydantic reads these via `from_attributes=True`
