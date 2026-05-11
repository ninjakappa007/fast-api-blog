from datetime import UTC, datetime, timedelta
import jwt
from fastapi.security import OAuth2PasswordBearer
from pwdlib import PasswordHash
from backend.config import settings


password_hash = PasswordHash.recommended()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='api/users/token')

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