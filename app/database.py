from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.ext.declarative import declarative_base

from app.config import get_settings

settings = get_settings()

# Motor de base de datos
engine = create_async_engine(settings.database_url, echo=settings.DEBUG)

# Sesión de base de datos
async_session = async_sessionmaker(engine, expire_on_commit=False)

# Base para los modelos
Base = declarative_base()


# Dependencia para obtener la sesión de base de datos
async def get_database():
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
