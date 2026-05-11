from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


# This config picks and set variables from .env and local env vars, also its case insensitive so SECRET_KEY == secret_key
class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file = 'backend/.env',
        env_file_encoding = 'utf-8'
    )
#   >>> import secrets
#   >> print(secrets.token_hex(32)) # generates secret key

    secret_key : SecretStr
    algorithm : str = 'HS256' # default value if we are not setting anything in .env or env vars
    access_token_expire_minutes : int = 30 # default value if we are not setting anything in .env or env vars
    
    
settings = Settings() # Loaded from .env file
