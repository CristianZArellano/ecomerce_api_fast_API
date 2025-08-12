"""
Excepciones personalizadas para la API E-commerce
"""
from typing import Any


class EcommerceException(Exception):
    """Excepción base para la aplicación"""

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        error_code: str = "INTERNAL_ERROR",
        details: dict[str, Any] | None = None
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


# Excepciones de autenticación
class AuthenticationException(EcommerceException):
    """Errores de autenticación"""

    def __init__(self, message: str = "Authentication failed", details: dict[str, Any] | None = None):
        super().__init__(
            message=message,
            status_code=401,
            error_code="AUTH_FAILED",
            details=details
        )


class InvalidTokenException(AuthenticationException):
    """Token inválido o expirado"""

    def __init__(self, message: str = "Invalid or expired token"):
        super().__init__(
            message=message,
            details={"error_type": "token_invalid"}
        )


class TokenExpiredException(AuthenticationException):
    """Token expirado"""

    def __init__(self, message: str = "Token has expired"):
        super().__init__(
            message=message,
            details={"error_type": "token_expired"}
        )


class AuthorizationException(EcommerceException):
    """Errores de autorización"""

    def __init__(self, message: str = "Insufficient permissions", details: dict[str, Any] | None = None):
        super().__init__(
            message=message,
            status_code=403,
            error_code="INSUFFICIENT_PERMISSIONS",
            details=details
        )


# Excepciones de usuario
class UserException(EcommerceException):
    """Errores relacionados con usuarios"""
    pass


class UserNotFoundException(UserException):
    """Usuario no encontrado"""

    def __init__(self, user_id: int | None = None, email: str | None = None):
        details = {}
        if user_id:
            details["user_id"] = user_id
        if email:
            details["email"] = email

        super().__init__(
            message="User not found",
            status_code=404,
            error_code="USER_NOT_FOUND",
            details=details
        )


class UserAlreadyExistsException(UserException):
    """Usuario ya existe"""

    def __init__(self, email: str):
        super().__init__(
            message=f"User with email '{email}' already exists",
            status_code=409,
            error_code="USER_ALREADY_EXISTS",
            details={"email": email}
        )


class InvalidCredentialsException(AuthenticationException):
    """Credenciales inválidas"""

    def __init__(self, message: str = "Invalid email or password"):
        super().__init__(
            message=message,
            details={"error_type": "invalid_credentials"}
        )


class UserInactiveException(AuthenticationException):
    """Usuario inactivo"""

    def __init__(self, user_id: int):
        super().__init__(
            message="User account is inactive",
            details={"user_id": user_id, "error_type": "user_inactive"}
        )


# Excepciones de productos
class ProductException(EcommerceException):
    """Errores relacionados con productos"""
    pass


class ProductNotFoundException(ProductException):
    """Producto no encontrado"""

    def __init__(self, product_id: int | None = None, sku: str | None = None):
        details = {}
        if product_id:
            details["product_id"] = product_id
        if sku:
            details["sku"] = sku

        super().__init__(
            message="Product not found",
            status_code=404,
            error_code="PRODUCT_NOT_FOUND",
            details=details
        )


class ProductAlreadyExistsException(ProductException):
    """Producto ya existe"""

    def __init__(self, sku: str):
        super().__init__(
            message=f"Product with SKU '{sku}' already exists",
            status_code=409,
            error_code="PRODUCT_ALREADY_EXISTS",
            details={"sku": sku}
        )


class InsufficientStockException(ProductException):
    """Stock insuficiente"""

    def __init__(self, product_id: int, requested: int, available: int):
        super().__init__(
            message=f"Insufficient stock. Requested: {requested}, Available: {available}",
            status_code=409,
            error_code="INSUFFICIENT_STOCK",
            details={
                "product_id": product_id,
                "requested_quantity": requested,
                "available_quantity": available
            }
        )


class ProductNotAvailableException(ProductException):
    """Producto no disponible"""

    def __init__(self, product_id: int):
        super().__init__(
            message="Product is not available for purchase",
            status_code=409,
            error_code="PRODUCT_NOT_AVAILABLE",
            details={"product_id": product_id}
        )


# Excepciones de validación
class ValidationException(EcommerceException):
    """Errores de validación"""

    def __init__(self, message: str, field: str | None = None, details: dict[str, Any] | None = None):
        validation_details = details or {}
        if field:
            validation_details["field"] = field

        super().__init__(
            message=message,
            status_code=422,
            error_code="VALIDATION_ERROR",
            details=validation_details
        )


class InvalidEmailFormatException(ValidationException):
    """Formato de email inválido"""

    def __init__(self, email: str):
        super().__init__(
            message=f"Invalid email format: {email}",
            field="email",
            details={"provided_email": email}
        )


class PasswordTooWeakException(ValidationException):
    """Contraseña demasiado débil"""

    def __init__(self, requirements: dict[str, bool]):
        super().__init__(
            message="Password does not meet security requirements",
            field="password",
            details={"requirements": requirements}
        )


# Excepciones de rate limiting
class RateLimitException(EcommerceException):
    """Rate limit excedido"""

    def __init__(self, limit: int, window_seconds: int, retry_after: int):
        super().__init__(
            message=f"Rate limit exceeded: {limit} requests per {window_seconds} seconds",
            status_code=429,
            error_code="RATE_LIMIT_EXCEEDED",
            details={
                "limit": limit,
                "window_seconds": window_seconds,
                "retry_after": retry_after
            }
        )


# Excepciones de base de datos
class DatabaseException(EcommerceException):
    """Errores de base de datos"""

    def __init__(self, message: str = "Database operation failed", details: dict[str, Any] | None = None):
        super().__init__(
            message=message,
            status_code=500,
            error_code="DATABASE_ERROR",
            details=details
        )


class DatabaseConnectionException(DatabaseException):
    """Error de conexión a la base de datos"""

    def __init__(self, message: str = "Could not connect to database"):
        super().__init__(
            message=message,
            details={"error_type": "connection_failed"}
        )


class DatabaseTimeoutException(DatabaseException):
    """Timeout de base de datos"""

    def __init__(self, operation: str, timeout_seconds: int):
        super().__init__(
            message=f"Database operation '{operation}' timed out after {timeout_seconds} seconds",
            details={
                "operation": operation,
                "timeout_seconds": timeout_seconds,
                "error_type": "timeout"
            }
        )


# Excepciones de cache
class CacheException(EcommerceException):
    """Errores de cache"""

    def __init__(self, message: str = "Cache operation failed", details: dict[str, Any] | None = None):
        super().__init__(
            message=message,
            status_code=500,
            error_code="CACHE_ERROR",
            details=details
        )


class CacheConnectionException(CacheException):
    """Error de conexión al cache"""

    def __init__(self, message: str = "Could not connect to cache server"):
        super().__init__(
            message=message,
            details={"error_type": "connection_failed"}
        )


# Excepciones de negocio
class BusinessLogicException(EcommerceException):
    """Errores de lógica de negocio"""

    def __init__(self, message: str, details: dict[str, Any] | None = None):
        super().__init__(
            message=message,
            status_code=400,
            error_code="BUSINESS_LOGIC_ERROR",
            details=details
        )


class OrderException(BusinessLogicException):
    """Errores relacionados con órdenes"""
    pass


class PaymentException(BusinessLogicException):
    """Errores de pago"""

    def __init__(self, message: str, payment_id: str | None = None, details: dict[str, Any] | None = None):
        payment_details = details or {}
        if payment_id:
            payment_details["payment_id"] = payment_id

        super().__init__(
            message=message,
            details=payment_details
        )


class ExternalServiceException(EcommerceException):
    """Errores de servicios externos"""

    def __init__(self, service_name: str, message: str = "External service error",
                 details: dict[str, Any] | None = None):
        service_details = details or {}
        service_details["service_name"] = service_name

        super().__init__(
            message=f"{service_name}: {message}",
            status_code=502,
            error_code="EXTERNAL_SERVICE_ERROR",
            details=service_details
        )


class ConfigurationException(EcommerceException):
    """Errores de configuración"""

    def __init__(self, message: str, config_key: str | None = None):
        details = {}
        if config_key:
            details["config_key"] = config_key

        super().__init__(
            message=message,
            status_code=500,
            error_code="CONFIGURATION_ERROR",
            details=details
        )
