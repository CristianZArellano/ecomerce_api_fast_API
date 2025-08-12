from datetime import datetime

from sqlalchemy import and_, func, or_, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.auth import encrypt_password, verify_password
from app.models import Product, User
from app.schemas import ProductCreate, ProductUpdate, UserCreate, UserUpdate

# ============= FUNCIONES PARA USUARIOS =============


async def get_users(
    db: AsyncSession, skip: int = 0, limit: int = 100, search: str | None = None
) -> list[User]:
    """Obtiene una lista de usuarios con búsqueda opcional"""
    query = select(User)

    # Si hay búsqueda, buscar en nombre o email
    if search:
        search_filter = f"%{search}%"
        query = query.where(
            or_(User.name.ilike(search_filter), User.email.ilike(search_filter))
        )

    # Ordenar por fecha de creación (más recientes primero)
    query = query.order_by(User.created_at.desc())

    # Aplicar paginación
    query = query.offset(skip).limit(limit)

    result = await db.execute(query)
    return list(result.scalars().all())


async def get_user_by_id(db: AsyncSession, user_id: int) -> User | None:
    """Busca un usuario por su ID"""
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalars().first()


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    """Busca un usuario por su email"""
    result = await db.execute(select(User).where(User.email == email))
    return result.scalars().first()


async def create_user(db: AsyncSession, user: UserCreate) -> User:
    """Crea un nuevo usuario con contraseña encriptada"""
    try:
        # Crear el usuario con contraseña encriptada
        db_user = User(
            name=user.name,
            email=user.email,
            password_hash=encrypt_password(user.password),
            is_admin=user.is_admin,
        )

        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        return db_user

    except IntegrityError as e:
        await db.rollback()
        raise ValueError("Email ya registrado") from e


async def authenticate_user(
    db: AsyncSession, email: str, password: str
) -> User | None:
    """Verifica las credenciales del usuario y devuelve el usuario si son correctas"""
    # Buscar el usuario por email
    user = await get_user_by_email(db, email)

    if user is None:
        return None

    # Verificar la contraseña (CORREGIDO)
    if not verify_password(password, str(user.password_hash)):
        return None

    # Actualizar última conexión usando update() (CORREGIDO)
    await db.execute(
        update(User).where(User.id == user.id).values(last_login=datetime.utcnow())
    )
    await db.commit()

    # Refrescar el usuario para obtener los datos actualizados
    await db.refresh(user)

    return user


async def update_user(
    db: AsyncSession, user_id: int, user_update: UserUpdate
) -> User | None:
    """Actualiza un usuario existente"""
    # Buscar el usuario
    db_user = await get_user_by_id(db, user_id)
    if db_user is None:
        return None

    # Preparar los datos para actualizar (CORREGIDO)
    update_data = user_update.model_dump(exclude_unset=True)
    update_data["updated_at"] = datetime.utcnow()

    try:
        # Usar update() en lugar de setattr (CORREGIDO)
        await db.execute(update(User).where(User.id == user_id).values(**update_data))
        await db.commit()
        await db.refresh(db_user)
        return db_user

    except IntegrityError as e:
        await db.rollback()
        raise ValueError("Email ya registrado por otro usuario") from e


async def change_user_password(
    db: AsyncSession, user_id: int, current_password: str, new_password: str
) -> bool:
    """Cambia la contraseña de un usuario"""
    # Buscar el usuario
    db_user = await get_user_by_id(db, user_id)
    if db_user is None:
        return False

    # Verificar la contraseña actual (CORREGIDO)
    if not verify_password(current_password, str(db_user.password_hash)):
        return False

    # Cambiar la contraseña usando update() (CORREGIDO)
    await db.execute(
        update(User)
        .where(User.id == user_id)
        .values(
            password_hash=encrypt_password(new_password), updated_at=datetime.utcnow()
        )
    )
    await db.commit()
    return True


async def deactivate_user(db: AsyncSession, user_id: int) -> bool:
    """Desactiva un usuario (no lo borra, solo lo marca como inactivo)"""
    db_user = await get_user_by_id(db, user_id)
    if db_user is None:
        return False

    # Usar update() en lugar de asignación directa (CORREGIDO)
    await db.execute(
        update(User)
        .where(User.id == user_id)
        .values(is_active=False, updated_at=datetime.utcnow())
    )
    await db.commit()
    return True


# ============= FUNCIONES PARA PRODUCTOS =============


async def get_products(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    search: str | None = None,
    category: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    available_only: bool = True,
) -> list[Product]:
    """Obtiene productos con filtros avanzados"""
    query = select(Product)

    # Filtrar solo disponibles si se requiere (CORREGIDO)
    if available_only:
        query = query.where(Product.is_available.is_(True))

    # Búsqueda por texto en nombre o descripción
    if search:
        search_filter = f"%{search}%"
        query = query.where(
            or_(
                Product.name.ilike(search_filter),
                Product.description.ilike(search_filter),
            )
        )

    # Filtrar por categoría
    if category:
        query = query.where(Product.category == category)

    # Filtrar por rango de precios
    if min_price is not None:
        query = query.where(Product.price >= min_price)
    if max_price is not None:
        query = query.where(Product.price <= max_price)

    # Ordenar por fecha de creación (más recientes primero)
    query = query.order_by(Product.created_at.desc())

    # Aplicar paginación
    query = query.offset(skip).limit(limit)

    result = await db.execute(query)
    return list(result.scalars().all())


async def get_product_by_id(db: AsyncSession, product_id: int) -> Product | None:
    """Busca un producto por su ID"""
    result = await db.execute(select(Product).where(Product.id == product_id))
    return result.scalars().first()


async def get_product_by_sku(db: AsyncSession, sku: str) -> Product | None:
    """Busca un producto por su SKU"""
    result = await db.execute(select(Product).where(Product.sku == sku))
    return result.scalars().first()


async def create_product(db: AsyncSession, product: ProductCreate) -> Product:
    """Crea un nuevo producto"""
    try:
        db_product = Product(**product.model_dump())
        db.add(db_product)
        await db.commit()
        await db.refresh(db_product)
        return db_product
    except IntegrityError as e:
        await db.rollback()
        raise ValueError("SKU ya existe") from e


async def update_product(
    db: AsyncSession, product_id: int, product_update: ProductUpdate
) -> Product | None:
    """Actualiza un producto existente"""
    # Buscar el producto
    db_product = await get_product_by_id(db, product_id)
    if db_product is None:
        return None

    # Preparar datos para actualizar (CORREGIDO)
    update_data = product_update.model_dump(exclude_unset=True)
    update_data["updated_at"] = datetime.utcnow()

    try:
        # Usar update() en lugar de setattr (CORREGIDO)
        await db.execute(
            update(Product).where(Product.id == product_id).values(**update_data)
        )
        await db.commit()
        await db.refresh(db_product)
        return db_product

    except IntegrityError as e:
        await db.rollback()
        raise ValueError("SKU ya existe") from e


async def delete_product(db: AsyncSession, product_id: int) -> bool:
    """Elimina un producto (marca como no disponible)"""
    db_product = await get_product_by_id(db, product_id)
    if db_product is None:
        return False

    # Usar update() en lugar de asignación directa (CORREGIDO)
    await db.execute(
        update(Product)
        .where(Product.id == product_id)
        .values(is_available=False, updated_at=datetime.utcnow())
    )
    await db.commit()
    return True


async def update_product_stock(
    db: AsyncSession, product_id: int, quantity: int
) -> Product | None:
    """Actualiza el stock de un producto"""
    db_product = await get_product_by_id(db, product_id)
    if db_product is None:
        return None

    # Obtener el stock actual - forzar el tipo correcto
    stock_value = getattr(db_product, 'stock', None)
    current_stock = int(stock_value) if stock_value is not None else 0
    new_stock_value = current_stock + quantity

    # Verificar que el nuevo stock no sea negativo
    if new_stock_value < 0:
        raise ValueError("Stock insuficiente")

    # Actualizar usando update()
    await db.execute(
        update(Product)
        .where(Product.id == product_id)
        .values(stock=new_stock_value, updated_at=datetime.utcnow())
    )
    await db.commit()
    await db.refresh(db_product)
    return db_product


# ============= FUNCIONES DE ESTADÍSTICAS =============


async def get_user_count(db: AsyncSession) -> int:
    """Cuenta el total de usuarios activos"""
    result = await db.execute(
        select(func.count(User.id)).where(User.is_active.is_(True))
    )
    count = result.scalar()
    return count if count is not None else 0


async def get_product_count(db: AsyncSession) -> int:
    """Cuenta el total de productos disponibles"""
    result = await db.execute(
        select(func.count(Product.id)).where(Product.is_available.is_(True))
    )
    count = result.scalar()
    return count if count is not None else 0


async def get_low_stock_products(
    db: AsyncSession, threshold: int = 10
) -> list[Product]:
    """Obtiene productos con stock bajo"""
    result = await db.execute(
        select(Product)
        .where(and_(Product.is_available.is_(True), Product.stock <= threshold))
        .order_by(Product.stock.asc())
    )
    return list(result.scalars().all())
