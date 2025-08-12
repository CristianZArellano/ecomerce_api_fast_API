from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Configuración básica de la app
    APP_NAME: str = "API E-commerce"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = "development"  # development, production, testing
    DEBUG: bool = True

    # Base de datos PostgreSQL
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "myuser"
    POSTGRES_PASSWORD: str = "secure_password_here"
    POSTGRES_DB: str = "mydatabase"
    POSTGRES_PORT: str = "5432"

    # JWT Authentication (nuevas configuraciones)
    SECRET_KEY: str = "ba7062a66cca657e2d72a1dba6620d0e86a85b0d6badf833c4ffbfc9b1b7d477"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Redis (nueva configuración)
    REDIS_URL: str = "redis://localhost:6379"

    # Rate Limiting (nueva configuración)
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60  # segundos

    @property
    def database_url(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
        "extra": "ignore",
    }


@lru_cache
def get_settings() -> Settings:
    return Settings()
