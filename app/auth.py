from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud
from app.config import get_settings
from app.database import get_database

# Traer la configuración
settings = get_settings()

# Configurar el "encriptador" de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Configuración para los tokens JWT
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"

# Configurar el "verificador" de tokens
security = HTTPBearer()


def encrypt_password(password: str) -> str:
    """Convierte una contraseña normal en una encriptada"""
    return str(pwd_context.hash(password))


def verify_password(plain_password: str, encrypted_password: str) -> bool:
    """Verifica si una contraseña coincide con la encriptada"""
    return bool(pwd_context.verify(plain_password, encrypted_password))


def create_access_token(user_id: int) -> str:
    """Crea un 'pase de entrada' (token) para un usuario"""
    # Calcular cuándo expira el token
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    # Crear los datos del token
    token_data = {
        "sub": str(user_id),  # "sub" significa "subject" (el usuario)
        "exp": expire,  # "exp" significa "expires" (cuándo expira)
        "type": "access",  # tipo de token
    }

    # Crear el token encriptado
    token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)
    return str(token)


def create_refresh_token(user_id: int) -> str:
    """Crea un 'pase especial' para renovar el pase normal"""
    # Calcular cuándo expira (dura más tiempo)
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    # Crear los datos del token
    token_data = {
        "sub": str(user_id),
        "exp": expire,
        "type": "refresh",  # tipo diferente
    }

    # Crear el token encriptado
    token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)
    return str(token)


async def verify_token(token: str, expected_type: str = "access") -> int:
    """Verifica si un token es válido y devuelve el ID del usuario"""
    try:
        # Desencriptar el token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        # Verificar que sea del tipo correcto
        if payload.get("type") != expected_type:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Tipo de token incorrecto",
            )

        # Obtener el ID del usuario
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido"
            )

        return int(user_id)

    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e


async def get_current_user(
    credentials=Depends(security), db: AsyncSession = Depends(get_database)
):
    """Obtiene el usuario que está haciendo la petición"""
    # Extraer el token de las credenciales
    token = credentials.credentials

    # Verificar el token y obtener el ID del usuario
    user_id = await verify_token(token, "access")

    # Buscar el usuario en la base de datos
    user = await crud.get_user_by_id(db, user_id=user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado"
        )

    return user


async def get_current_active_user(current_user=Depends(get_current_user)):
    """Obtiene el usuario actual y verifica que esté activo"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Usuario inactivo"
        )
    return current_user
