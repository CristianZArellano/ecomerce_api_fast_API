# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a functional FastAPI-based e-commerce API with comprehensive features including JWT authentication, Redis caching, rate limiting, structured logging, and advanced middleware. The project uses:
- **FastAPI** for the web framework with custom OpenAPI documentation
- **PostgreSQL** with SQLAlchemy (async) for database operations
- **Redis** for intelligent caching and session management
- **JWT Authentication** with access and refresh tokens
- **Docker Compose** for local development environment
- **Structured Logging** in JSON format
- **Advanced Middleware** for security, rate limiting, and monitoring

## Development Commands

### Code Quality and Linting
```bash
# Run linter (Ruff)
ruff check .
ruff check --fix .

# Format code
ruff format .

# Type checking
mypy .

# Run all checks
ruff check . && mypy . && ruff format --check .
```

### Environment Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Create data directories (required for first run)
mkdir -p data/postgres data/redis

# Start database services
docker compose up -d postgres redis

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
docker-compose logs -f api
docker-compose logs -f postgres
docker-compose logs -f redis

# Stop services
docker-compose down

# Rebuild services
docker-compose up -d --build
```

### Testing and Debugging
```bash
# Test database connection
python -c "from app.config import get_settings; print(get_settings().database_url_computed)"

# Test Redis connection
python -c "from app.redis_client import redis_client; import asyncio; asyncio.run(redis_client.connect()); print('Redis connected')"

# Check health endpoint
curl http://localhost:8000/health

# View API documentation
# Visit http://localhost:8000/docs
```

## Architecture Overview

### Application Structure (`main.py`)
- **FastAPI Application**: Complete e-commerce API with custom OpenAPI documentation
- **Lifespan Management**: Async startup/shutdown with database and Redis initialization
- **Custom Middleware Stack**: Error handling, security headers, rate limiting, logging
- **Authentication System**: JWT-based with access and refresh tokens
- **CORS Configuration**: Environment-specific with security considerations

### Database Layer (`app/models.py`, `app/crud.py`)
- **Models**: User, Product, UserSession with optimized indexes
- **Async Operations**: Full SQLAlchemy async support with connection pooling
- **CRUD Operations**: Comprehensive user and product management with filtering
- **Security**: Password hashing, input validation, SQL injection protection

### Authentication & Authorization (`app/auth.py`)
- **JWT Tokens**: Access tokens (short-lived) and refresh tokens (long-lived)
- **Password Security**: bcrypt hashing with passlib
- **Role-based Access**: Admin and regular user permissions
- **Token Validation**: Dependency injection for route protection

### Redis Integration (`app/redis_client.py`)
- **Intelligent Caching**: Product listings and user sessions
- **Cache Keys**: Structured keys with TTL management
- **Cache Invalidation**: Strategic cache clearing on data updates
- **Session Storage**: User authentication state management

### Middleware Stack (`app/middleware.py`)
- **Rate Limiting**: Redis-backed with sliding window algorithm
- **Security Headers**: Comprehensive security header injection
- **Request Logging**: Structured JSON logging with request tracking
- **Error Handling**: Centralized exception handling with user-friendly responses

### Configuration System (`app/config.py`)
- **Environment-specific**: Development, Production, Testing configurations
- **Security Validation**: Enforced secure settings in production
- **Database URLs**: Automatic async/sync URL generation
- **Settings Management**: Pydantic Settings v2 with environment variables

### Project Structure
```
api_ecomerce/
├── app/
│   ├── auth.py           # JWT authentication system
│   ├── config.py         # Configuration management
│   ├── crud.py           # Database operations
│   ├── database.py       # Database connection setup
│   ├── exceptions.py     # Custom exception classes
│   ├── health.py         # Health check endpoints
│   ├── logging_config.py # Structured logging setup
│   ├── middleware.py     # Custom middleware stack
│   ├── models.py         # SQLAlchemy models
│   ├── redis_client.py   # Redis operations
│   └── schemas.py        # Pydantic schemas
├── main.py               # FastAPI application setup
├── requirements.txt      # Python dependencies
├── docker-compose.yml    # Development environment
├── mypy.ini             # Type checking configuration
├── pyproject.toml       # Ruff linting and formatting
└── .env                 # Environment variables
```

## Development Guidelines

### API Endpoints
The API provides these main endpoint groups:
- `/auth/*` - Authentication (register, login, refresh, profile)
- `/users/*` - User management (admin only for listing)
- `/products/*` - Product catalog with filtering and caching
- `/stats/` - Statistics and metrics (admin only)
- `/health/*` - Health checks and monitoring

### Authentication Flow
```python
# 1. Register user
POST /auth/register
{"name": "John Doe", "email": "john@example.com", "password": "secret123"}

# 2. Login to get tokens
POST /auth/login
{"email": "john@example.com", "password": "secret123"}

# 3. Use access_token in Authorization header
Authorization: Bearer {access_token}

# 4. Refresh when access_token expires
POST /auth/refresh
{"refresh_token": "{refresh_token}"}
```

### Database Operations
```python
# Creating new models - always use async CRUD functions
from app import crud, schemas

# Create user
user_data = schemas.UserCreate(name="John", email="john@example.com", password="secret")
user = await crud.create_user(db, user_data)

# Get products with filters
products = await crud.get_products(db, search="laptop", category="electronics")
```

### Redis Caching
```python
# Cache is automatically handled in endpoints
# Manual cache operations:
from app.redis_client import cache_products, get_cached_products

# Cache automatically expires and is invalidated on updates
cached_data = await get_cached_products(filters)
await cache_products(products, filters, expire_minutes=10)
```

### Environment Detection
Set `APP_ENV` environment variable:
- `development` (default): Debug mode, verbose logging, open CORS
- `production`: Security hardened, restricted CORS, minimal logging  
- `testing`: In-memory databases, debug logging

### Error Handling
Custom exceptions in `app/exceptions.py`:
- `UserAlreadyExistsException` - Email already registered
- `ValidationException` - Input validation errors
- `RateLimitExceededException` - Rate limit violations
- Automatic HTTP status code mapping

## Infrastructure Services

### PostgreSQL Configuration
- **Image**: postgres:15-alpine with performance optimizations
- **Indexes**: Optimized for user email lookups and product filtering
- **Connection Pooling**: Async connections with configurable pool size
- **Health Checks**: Built-in monitoring and automatic table creation

### Redis Configuration  
- **Image**: redis:7-alpine with custom configuration
- **Caching Strategy**: Intelligent TTL-based caching with filter-specific keys
- **Rate Limiting**: Sliding window algorithm for API throttling
- **Session Management**: JWT token validation and user session storage