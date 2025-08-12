# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a FastAPI-based e-commerce API project in early development. The project uses:
- **FastAPI** for the web framework
- **PostgreSQL** with SQLAlchemy (async) for database operations
- **Redis** for caching and session management
- **Docker Compose** for local development environment
- **Pydantic Settings** for configuration management

## Development Commands

### Environment Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Create data directories (required for first run)
mkdir -p data/postgres data/redis

# Start database services
docker compose up -d postgres

# Run the FastAPI application
python main.py
# OR
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Docker Development
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild services
docker-compose up -d --build
```

### Database Operations
```bash
# Generate migration (when alembic is configured)
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Database connection test
python -c "from app.config import get_settings; print(get_settings().database_url_computed)"
```

## Architecture Overview

### Configuration System (`app/config.py`)
- Comprehensive settings management using Pydantic Settings v2
- Environment-specific configurations (Development, Production, Testing)
- Automatic environment variable loading from `.env` file
- Database and Redis URL computation with fallback logic
- Validation for security-critical settings

### Key Configuration Classes
- `Settings`: Base configuration with all application settings
- `DevelopmentSettings`: Debug mode, verbose logging, open CORS
- `ProductionSettings`: Security-focused, minimal logging
- `TestingSettings`: SQLite/memory databases for testing

### Database Architecture
- **Primary**: PostgreSQL with asyncpg driver (`postgresql+asyncpg://`)
- **Sync operations**: Automatic psycopg2 URL generation for migrations
- **Connection pooling**: Configurable pool size and overflow
- **Health checks**: Built into Docker Compose setup

### Caching Layer
- **Redis**: Primary cache and session store
- **Configuration**: Custom Redis config with persistence, memory limits
- **Connection**: Pool-based connections with retry logic

### Environment Variables
Key variables defined in `.env`:
- Database: `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, `POSTGRES_PORT`
- Redis: `REDIS_PORT`, `REDIS_PASSWORD`
- Application: `APP_ENV` (development|production|testing)

## Project Structure

```
api_ecomerce/
├── app/
│   ├── config.py          # Comprehensive configuration management
│   └── __init__.py        # (empty - ready for app factory)
├── main.py                # (empty - FastAPI app entry point)
├── requirements.txt       # Python dependencies
├── docker-compose.yml     # Local development environment
├── redis.config          # Redis server configuration
└── .env                  # Environment variables
```

## Development Guidelines

### Configuration Usage
```python
from app.config import get_settings

settings = get_settings()  # Auto-detects environment
database_url = settings.database_url_computed
redis_url = settings.redis_url_computed
```

### Environment Detection
The application automatically detects environment via `APP_ENV`:
- `development` (default): Debug mode, verbose logging
- `production`: Security hardened, minimal logging  
- `testing`: In-memory databases, debug logging

### Security Configuration
- Production requires secure `SECRET_KEY` (validated)
- CORS origins are environment-specific
- Database connections use connection pooling
- Redis can be password-protected via `REDIS_PASSWORD`

## Infrastructure Services

### PostgreSQL Configuration
- **Image**: postgres:15-alpine
- **Performance tuning**: Connection limits, shared buffers, work memory
- **Monitoring**: Statement logging, connection tracking
- **Persistence**: Named volume with local binding

### Redis Configuration  
- **Image**: redis:7-alpine
- **Persistence**: AOF enabled with auto-rewrite
- **Memory**: 256MB limit with LRU eviction
- **Performance**: TCP optimizations, snapshot scheduling