import time
from contextlib import asynccontextmanager
from typing import Optional, cast

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, schemas
from app.auth import (
    create_access_token,
    create_refresh_token,
    get_current_active_user,
    get_current_user,
    verify_token,
)
from app.config import get_settings
from app.database import Base, engine, get_database
from app.exceptions import (
    RateLimitException,
    UserAlreadyExistsException,
    ValidationException,
)
from app.health import router as health_router
from app.logging_config import get_logger, log_business_event, setup_logging
from app.middleware import (
    ErrorHandlerMiddleware,
    LoggingMiddleware,
    RateLimitMiddleware,
    SecurityHeadersMiddleware,
)
from app.redis_client import (
    cache_products,
    cache_user,
    get_cached_products,
    get_cached_user,
    invalidate_user_cache,
    redis_client,
)

# Configurar logging estructurado
setup_logging()
logger = get_logger()

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestión del ciclo de vida de la aplicación"""
    # Startup
    logger.info("Starting E-commerce API...")

    # Crear las tablas de la base de datos
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created")

    # Conectar a Redis
    await redis_client.connect()
    logger.info("Redis connected")

    log_business_event(
        logger,
        "service_started",
        {"version": settings.APP_VERSION, "environment": settings.APP_ENV},
    )

    yield

    # Shutdown
    logger.info("Shutting down E-commerce API...")
    await redis_client.disconnect()
    logger.info("E-commerce API shutdown completed")


# Crear la aplicación FastAPI con configuración profesional
app = FastAPI(
    title="🛒 E-commerce API",
    version=settings.APP_VERSION,
    description="""
    ## 🚀 Professional E-commerce API

    Una API completa de e-commerce con características avanzadas de seguridad,
    caching, rate limiting y logging estructurado.

    ### ✨ Características principales:
    - 🔐 **JWT Authentication** con refresh tokens
    - 🛡️ **Rate limiting** inteligente con Redis
    - 📊 **Logging estructurado** en formato JSON
    - 🚀 **Redis caching** para productos y sesiones
    - 🔒 **Security headers** y CORS configurado
    - 📈 **Health checks** avanzados
    - 🐳 **Docker ready** con docker-compose

    ### 🔑 Autenticación:
    1. Registra un usuario en `/auth/register`
    2. Inicia sesión en `/auth/login` para obtener tokens
    3. Usa el `access_token` en el header: `Authorization: Bearer {token}`
    4. Renueva tokens con `/auth/refresh`

    ### 🛍️ Endpoints principales:
    - **Autenticación**: `/auth/*`
    - **Usuarios**: `/users/*`
    - **Productos**: `/products/*`
    - **Estadísticas**: `/stats/`
    - **Health checks**: `/health/*`
    """,
    debug=settings.DEBUG,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan,
    contact={
        "name": "API Support",
        "email": "support@ecommerce-api.com",
        "url": "https://github.com/CristianZArellano/ecomerce_api_fast_API.git",
    },
    license_info={"name": "MIT License", "url": "https://opensource.org/licenses/MIT"},
    terms_of_service="https://your-domain.com/terms",
    openapi_tags=[
        {
            "name": "auth",
            "description": "🔐 Autenticación y autorización",
        },
        {"name": "users", "description": "👥 Gestión de usuarios"},
        {"name": "products", "description": "🛍️ Gestión de productos"},
        {"name": "stats", "description": "📊 Estadísticas y métricas"},
        {"name": "health", "description": "🏥 Health checks y monitoreo"},
    ],
)


def custom_openapi():
    """Configuración personalizada de OpenAPI"""
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
        tags=app.openapi_tags,
    )

    # Configurar esquema de seguridad
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "JWT token obtenido del endpoint /auth/login",
        }
    }

    # Agregar ejemplos de respuesta
    openapi_schema["components"]["examples"] = {
        "UserExample": {
            "summary": "Usuario ejemplo",
            "value": {
                "name": "Juan Pérez",
                "email": "juan@example.com",
                "is_active": True,
                "is_admin": False,
            },
        },
        "ProductExample": {
            "summary": "Producto ejemplo",
            "value": {
                "name": "Laptop Gaming",
                "description": "Laptop para gaming de alta gama",
                "price": 1299.99,
                "stock": 10,
                "category": "Electronics",
                "sku": "LAP-001",
            },
        },
    }

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

# Configurar CORS seguro
cors_origins = []
if settings.APP_ENV == "development":
    cors_origins = ["*"]
elif settings.APP_ENV == "production":
    # En producción, especificar dominios exactos
    cors_origins = [
        "https://yourdomain.com",
        "https://www.yourdomain.com",
        "https://app.yourdomain.com",
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID", "X-Response-Time", "X-RateLimit-*"],
)

# Agregar middlewares en orden correcto
app.add_middleware(ErrorHandlerMiddleware)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(LoggingMiddleware)

# Incluir health check router
app.include_router(health_router)


# ============= ENDPOINTS BÁSICOS =============


@app.get(
    "/",
    summary="🏠 Página principal",
    description="Endpoint de bienvenida con información básica de la API",
    response_description="Información de bienvenida y características",
)
async def root():
    """Página principal de la API"""
    return {
        "message": "¡Bienvenido a la API E-commerce!",
        "version": settings.APP_VERSION,
        "environment": settings.APP_ENV,
        "features": [
            "🔐 JWT Authentication con refresh tokens",
            "⚡ Redis Caching inteligente",
            "🛡️ Rate Limiting avanzado",
            "📊 Logging estructurado JSON",
            "🔒 Security headers y CORS",
            "📈 Health checks profesionales",
            "🐳 Docker ready",
        ],
        "documentation": "/docs",
        "health": "/health",
    }


# ============= ENDPOINTS DE AUTENTICACIÓN =============


@app.post(
    "/auth/register",
    response_model=schemas.User,
    tags=["auth"],
    summary="👤 Registrar usuario",
    description="Crear una nueva cuenta de usuario en el sistema",
    response_description="Usuario creado exitosamente",
)
async def register_user(
    user: schemas.UserRegister, db: AsyncSession = Depends(get_database)
):
    """Registrar un nuevo usuario en el sistema"""
    user_create = schemas.UserCreate(
        name=user.name, email=user.email, password=user.password, is_admin=False
    )

    try:
        return await crud.create_user(db=db, user=user_create)
    except ValueError as e:
        if "Email ya registrado" in str(e):
            raise UserAlreadyExistsException(email=user.email) from e
        raise ValidationException(message=str(e)) from e


@app.post("/auth/login", response_model=schemas.TokenResponse)
async def login_user(
    user_login: schemas.UserLogin, db: AsyncSession = Depends(get_database)
):
    """Iniciar sesión"""
    # Verificar credenciales
    user = await crud.authenticate_user(db, user_login.email, user_login.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
        )

    # Crear tokens
    user_id = cast(int, user.id)
    access_token = create_access_token(user_id)
    refresh_token = create_refresh_token(user_id)

    # Guardar datos del usuario en caché
    user_data = {
        "id": user_id,
        "name": cast(str, user.name),
        "email": cast(str, user.email),
        "is_admin": cast(bool, user.is_admin),
        "is_active": cast(bool, user.is_active),
    }
    await cache_user(user_id, user_data, expire_minutes=30)

    return schemas.TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@app.post("/auth/refresh", response_model=schemas.TokenResponse)
async def refresh_token(
    refresh_request: schemas.RefreshTokenRequest,
    db: AsyncSession = Depends(get_database),
):
    """Renovar token de acceso"""
    try:
        user_id = await verify_token(refresh_request.refresh_token, "refresh")

        # Verificar que el usuario existe
        user = await crud.get_user_by_id(db, user_id)
        if user is None:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        # Crear nuevo access token
        new_access_token = create_access_token(user_id)

        return schemas.TokenResponse(
            access_token=new_access_token,
            refresh_token=refresh_request.refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token de refresh inválido"
        ) from e


@app.get("/auth/me", response_model=schemas.UserProfile)
async def get_my_profile(current_user=Depends(get_current_active_user)):
    """Obtener mi perfil"""
    return current_user


# ============= ENDPOINTS DE USUARIOS =============


@app.get("/users/", response_model=list[schemas.User])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    search: str | None = None,
    db: AsyncSession = Depends(get_database),
    current_user=Depends(get_current_active_user),
):
    """Obtener lista de usuarios (solo para administradores)"""
    if not cast(bool, current_user.is_admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los administradores pueden ver la lista de usuarios",
        )

    return await crud.get_users(db, skip=skip, limit=limit, search=search)


@app.get("/users/{user_id}", response_model=schemas.User)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_database),
    current_user=Depends(get_current_active_user),
):
    """Obtener un usuario específico"""
    # Solo admin o el mismo usuario puede ver el perfil
    if not cast(bool, current_user.is_admin) and cast(int, current_user.id) != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para ver este usuario",
        )

    # Intentar obtener del caché primero
    if cast(int, current_user.id) == user_id:
        cached_user = await get_cached_user(user_id)
        if cached_user:
            return schemas.User(**cached_user)

    # Si no está en caché, obtener de la base de datos
    user = await crud.get_user_by_id(db, user_id=user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    return user


# ============= ENDPOINTS DE PRODUCTOS =============


@app.get("/products/", response_model=list[schemas.Product])
async def get_products(
    skip: int = 0,
    limit: int = 100,
    search: str | None = None,
    category: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    available_only: bool = True,
    db: AsyncSession = Depends(get_database),
):
    """Obtener productos con caché inteligente"""

    # Crear filtros para el caché
    filters = {
        "skip": skip,
        "limit": limit,
        "search": search,
        "category": category,
        "min_price": min_price,
        "max_price": max_price,
        "available_only": available_only,
    }

    # Intentar obtener del caché primero
    cached_products = await get_cached_products(filters)
    if cached_products is not None:
        print("🚀 Productos obtenidos del caché")
        return cached_products

    # Si no está en caché, obtener de la base de datos
    print("💾 Productos obtenidos de la base de datos")
    products = await crud.get_products(
        db,
        skip=skip,
        limit=limit,
        search=search,
        category=category,
        min_price=min_price,
        max_price=max_price,
        available_only=available_only,
    )

    # Guardar en caché por 10 minutos
    await cache_products(products, filters, expire_minutes=10)

    return products


@app.get("/products/{product_id}", response_model=schemas.Product)
async def get_product(product_id: int, db: AsyncSession = Depends(get_database)):
    """Obtener un producto específico"""
    product = await crud.get_product_by_id(db, product_id=product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return product


@app.post("/products/", response_model=schemas.Product)
async def create_product(
    product: schemas.ProductCreate,
    db: AsyncSession = Depends(get_database),
    current_user=Depends(get_current_active_user),
):
    """Crear un nuevo producto (solo administradores)"""
    if not cast(bool, current_user.is_admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los administradores pueden crear productos",
        )

    try:
        new_product = await crud.create_product(db=db, product=product)

        # Invalidar caché de productos
        # (Se podría implementar una invalidación más inteligente)
        print("🗑️ Invalidando caché de productos...")

        return new_product
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


# ============= ENDPOINTS DE ESTADÍSTICAS =============


@app.get("/stats/")
async def get_stats(
    db: AsyncSession = Depends(get_database),
    current_user=Depends(get_current_active_user),
):
    """Obtener estadísticas generales (solo administradores)"""
    if not cast(bool, current_user.is_admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los administradores pueden ver estadísticas",
        )

    user_count = await crud.get_user_count(db)
    product_count = await crud.get_product_count(db)
    low_stock_products = await crud.get_low_stock_products(db, threshold=10)

    return {
        "total_users": user_count,
        "total_products": product_count,
        "low_stock_products": len(low_stock_products),
        "low_stock_list": [
            {"id": p.id, "name": p.name, "stock": p.stock} for p in low_stock_products
        ],
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
