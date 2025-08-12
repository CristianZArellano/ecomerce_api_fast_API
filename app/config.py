from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "API E-commerce"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Base de datos
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "myuser"
    POSTGRES_PASSWORD: str = "secure_password_here"
    POSTGRES_DB: str = "mydatabase"
    POSTGRES_PORT: str = "5432"
    
    @property
    def database_url(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
        "extra": "ignore",
    }


@lru_cache()
def get_settings() -> Settings:
    return Settings()