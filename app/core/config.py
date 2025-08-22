from pydantic_settings import BaseSettings
from typing import Optional
from dotenv import load_dotenv


load_dotenv()


class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    SMTP_SERVER: str
    SMTP_PORT: int
    SMTP_USERNAME: str
    SMTP_PASSWORD: str

    model_config = {
        "env_file": ".env",
        "extra": "ignore"
    }


settings = Settings()  # type: ignore
