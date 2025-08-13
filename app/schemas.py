from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_validator

# ============= ESQUEMAS DE AUTENTICACIÓN =============


class UserLogin(BaseModel):
    """Formulario para iniciar sesión"""

    email: EmailStr
    password: str = Field(..., min_length=6, max_length=100)


class UserRegister(BaseModel):
    """Formulario para registrarse"""

    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=100)

    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError("El nombre no puede estar vacío")
        return v.strip()


class TokenResponse(BaseModel):
    """Respuesta cuando alguien inicia sesión correctamente"""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # segundos hasta que expire


class RefreshTokenRequest(BaseModel):
    """Formulario para renovar el token"""

    refresh_token: str


# ============= ESQUEMAS DE USUARIO =============


class UserBase(BaseModel):
    """Información básica del usuario (sin contraseña)"""

    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr


class UserCreate(BaseModel):
    """Para crear usuarios (incluye contraseña)"""

    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=100)
    is_admin: bool = False


class UserUpdate(BaseModel):
    """Para actualizar usuarios (todo opcional)"""

    name: str | None = Field(None, min_length=2, max_length=100)
    email: EmailStr | None = None
    is_active: bool | None = None
    is_admin: bool | None = None


class ChangePassword(BaseModel):
    """Para cambiar la contraseña"""

    current_password: str
    new_password: str = Field(..., min_length=6, max_length=100)


class User(UserBase):
    """Usuario completo (para mostrar, sin contraseña)"""

    id: int
    is_active: bool
    is_admin: bool
    created_at: datetime
    updated_at: datetime
    last_login: datetime | None = None

    model_config = {"from_attributes": True}


class UserProfile(BaseModel):
    """Perfil del usuario actual (con más detalles)"""

    id: int
    name: str
    email: str
    is_active: bool
    is_admin: bool
    created_at: datetime
    last_login: datetime | None = None

    model_config = {"from_attributes": True}


# ============= ESQUEMAS DE PRODUCTO =============


class ProductBase(BaseModel):
    """Información básica del producto"""

    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = Field(None, max_length=2000)
    price: float = Field(..., gt=0)  # gt=0 significa "mayor que 0"
    stock: int = Field(default=0, ge=0)  # ge=0 significa "mayor o igual que 0"
    category: str | None = Field(None, max_length=50)
    sku: str | None = Field(None, max_length=50)
    weight: float | None = Field(None, gt=0)

    @field_validator("price")
    @classmethod
    def validate_price(cls, v):
        if v <= 0:
            raise ValueError("El precio debe ser mayor que 0")
        # Redondear a 2 decimales
        return round(v, 2)

    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError("El nombre no puede estar vacío")
        return v.strip()


class ProductCreate(ProductBase):
    """Para crear productos"""

    pass


class ProductUpdate(BaseModel):
    """Para actualizar productos (todo opcional)"""

    name: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = Field(None, max_length=2000)
    price: float | None = Field(None, gt=0)
    stock: int | None = Field(None, ge=0)
    is_available: bool | None = None
    category: str | None = Field(None, max_length=50)
    sku: str | None = Field(None, max_length=50)
    weight: float | None = Field(None, gt=0)


class Product(ProductBase):
    """Producto completo (para mostrar)"""

    id: int
    is_available: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ============= ESQUEMAS DE RESPUESTA =============


class MessageResponse(BaseModel):
    """Respuesta simple con mensaje"""

    message: str
    success: bool = True


class ErrorResponse(BaseModel):
    """Respuesta de error"""

    message: str
    error_code: str | None = None
    details: dict | None = None


class PaginatedResponse(BaseModel):
    """Respuesta con paginación"""

    items: list
    total: int
    page: int
    page_size: int
    total_pages: int


# ============= ESQUEMAS DE VALIDACIÓN =============


class IDPathParam(BaseModel):
    """Para validar IDs en las URLs"""

    id: int = Field(..., gt=0, description="ID debe ser mayor que 0")


class PaginationParams(BaseModel):
    """Para validar parámetros de paginación"""

    skip: int = Field(default=0, ge=0, description="Elementos a saltar")
    limit: int = Field(
        default=100, ge=1, le=1000, description="Máximo elementos por página"
    )
