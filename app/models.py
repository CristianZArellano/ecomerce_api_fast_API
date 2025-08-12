
from sqlalchemy import Boolean, Column, DateTime, Float, Index, Integer, String, Text
from sqlalchemy.sql import func

from app.database import Base


class User(Base):
    __tablename__ = "users"

    # Campos básicos
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)

    # NUEVO: Campo para la contraseña encriptada
    password_hash = Column(String(128), nullable=False)

    # Campos de estado
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)  # NUEVO: Para distinguir administradores

    # Campos de tiempo
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # NUEVO: Campos para tokens
    last_login = Column(DateTime(timezone=True), nullable=True)

    # Índices para optimizar búsquedas
    __table_args__ = (
        Index("idx_user_email_active", "email", "is_active"),
        Index("idx_user_created_at", "created_at"),
    )


class Product(Base):
    __tablename__ = "products"

    # Campos básicos
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)  # Cambiado de String(500) a Text para más caracteres
    price = Column(Float, nullable=False)

    # Campos de inventario
    stock = Column(Integer, default=0)
    is_available = Column(Boolean, default=True)

    # NUEVO: Campos adicionales para e-commerce
    category = Column(String(50), nullable=True)
    sku = Column(String(50), unique=True, nullable=True)  # Stock Keeping Unit
    weight = Column(Float, nullable=True)  # Para shipping

    # Campos de tiempo
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Índices para optimizar búsquedas
    __table_args__ = (
        Index("idx_product_available_category", "is_available", "category"),
        Index("idx_product_price", "price"),
        Index("idx_product_stock", "stock"),
        Index("idx_product_created_at", "created_at"),
    )


# NUEVO: Modelo para sesiones de usuarios (para manejar refresh tokens)
class UserSession(Base):
    __tablename__ = "user_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    refresh_token_hash = Column(String(128), nullable=False)
    device_info = Column(String(200), nullable=True)  # Info del dispositivo/navegador
    ip_address = Column(String(45), nullable=True)  # IPv4 o IPv6
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)
    last_used = Column(DateTime(timezone=True), server_default=func.now())

    # Índices para optimizar búsquedas
    __table_args__ = (
        Index("idx_session_user_active", "user_id", "is_active"),
        Index("idx_session_expires", "expires_at"),
    )
