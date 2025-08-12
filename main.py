from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.config import get_settings
from app.database import get_database, engine, Base
from app import crud, schemas

settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    description="""
    ## API E-commerce con FastAPI

    Esta API proporciona endpoints para gestionar usuarios y productos en un sistema de e-commerce.

    ### Funcionalidades:
    * **Usuarios**: Crear y gestionar usuarios del sistema
    * **Productos**: Crear y gestionar catálogo de productos
    * **Validaciones**: Validación automática de datos con Pydantic
    * **Base de datos**: PostgreSQL con SQLAlchemy async

    ### Documentación adicional:
    Consulta el archivo `API_DOCUMENTATION.md` para ejemplos detallados.
    """,
    contact={
        "name": "API E-commerce",
        "url": "https://github.com/CristianZArellano/ecomerce_api_fast_API",
    },
    tags_metadata=[
        {
            "name": "sistema",
            "description": "Endpoints generales del sistema",
        },
        {
            "name": "usuarios",
            "description": "Operaciones CRUD para usuarios",
        },
        {
            "name": "productos",
            "description": "Operaciones CRUD para productos",
        },
    ]
)


@app.on_event("startup")
async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.get("/", tags=["sistema"], summary="Endpoint de bienvenida")
async def root():
    """
    Endpoint de bienvenida que retorna información básica de la API.
    
    Retorna la versión actual y un mensaje de bienvenida.
    """
    return {"message": "¡Bienvenido a la API E-commerce!", "version": settings.APP_VERSION}


@app.get("/health", tags=["sistema"], summary="Health check")
async def health_check():
    """
    Health check para verificar el estado de la API.
    
    Útil para monitoreo y verificación de que el servicio está operativo.
    """
    return {"status": "ok", "message": "API funcionando correctamente"}


# Endpoints de usuarios
@app.post("/users/", response_model=schemas.User, tags=["usuarios"], summary="Crear usuario")
async def create_user(user: schemas.UserCreate, db: AsyncSession = Depends(get_database)):
    """
    Crea un nuevo usuario en el sistema.
    
    - **name**: Nombre completo del usuario
    - **email**: Email único del usuario (debe ser válido)
    
    Retorna el usuario creado con su ID y fecha de creación.
    """
    try:
        return await crud.create_user(db=db, user=user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/users/", response_model=List[schemas.User], tags=["usuarios"], summary="Listar usuarios")
async def read_users(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_database)):
    """
    Obtiene una lista paginada de todos los usuarios.
    
    - **skip**: Número de registros a omitir (para paginación)
    - **limit**: Número máximo de registros a retornar (máx. 100)
    """
    return await crud.get_users(db, skip=skip, limit=limit)


@app.get("/users/{user_id}", response_model=schemas.User, tags=["usuarios"], summary="Obtener usuario")
async def read_user(user_id: int, db: AsyncSession = Depends(get_database)):
    """
    Obtiene un usuario específico por su ID.
    
    - **user_id**: ID único del usuario a buscar
    
    Retorna los datos completos del usuario o error 404 si no existe.
    """
    user = await crud.get_user_by_id(db, user_id=user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user


# Endpoints de productos
@app.post("/products/", response_model=schemas.Product, tags=["productos"], summary="Crear producto")
async def create_product(product: schemas.ProductCreate, db: AsyncSession = Depends(get_database)):
    """
    Crea un nuevo producto en el catálogo.
    
    - **name**: Nombre del producto
    - **description**: Descripción opcional del producto
    - **price**: Precio del producto (debe ser mayor a 0)
    - **stock**: Cantidad disponible en inventario
    
    El producto se crea como disponible por defecto.
    """
    return await crud.create_product(db=db, product=product)


@app.get("/products/", response_model=List[schemas.Product], tags=["productos"], summary="Listar productos")
async def read_products(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_database)):
    """
    Obtiene una lista paginada de productos disponibles.
    
    - **skip**: Número de registros a omitir (para paginación)
    - **limit**: Número máximo de registros a retornar (máx. 100)
    
    Solo retorna productos marcados como disponibles.
    """
    return await crud.get_products(db, skip=skip, limit=limit)


@app.get("/products/{product_id}", response_model=schemas.Product, tags=["productos"], summary="Obtener producto")
async def read_product(product_id: int, db: AsyncSession = Depends(get_database)):
    """
    Obtiene un producto específico por su ID.
    
    - **product_id**: ID único del producto a buscar
    
    Retorna los datos completos del producto o error 404 si no existe.
    """
    product = await crud.get_product_by_id(db, product_id=product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return product


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)