# 📚 API E-commerce - Documentación

Esta documentación describe todos los endpoints disponibles en la API E-commerce construida con FastAPI.

## 🚀 Información General

- **Base URL**: `http://localhost:8000`
- **Formato**: JSON
- **Framework**: FastAPI
- **Base de datos**: PostgreSQL

## 📋 Índice de Endpoints

### Sistema
- [GET /](#get-) - Endpoint de bienvenida
- [GET /health](#get-health) - Health check

### Usuarios
- [POST /users/](#post-users) - Crear usuario
- [GET /users/](#get-users) - Listar usuarios
- [GET /users/{id}](#get-usersid) - Obtener usuario específico

### Productos
- [POST /products/](#post-products) - Crear producto
- [GET /products/](#get-products) - Listar productos
- [GET /products/{id}](#get-productsid) - Obtener producto específico

---

## 🏠 Sistema

### GET /

Endpoint de bienvenida que retorna información básica de la API.

**Request:**
```http
GET /
```

**Response:**
```json
{
  "message": "¡Bienvenido a la API E-commerce!",
  "version": "1.0.0"
}
```

**Status Code:** `200 OK`

---

### GET /health

Health check para verificar el estado de la API.

**Request:**
```http
GET /health
```

**Response:**
```json
{
  "status": "ok",
  "message": "API funcionando correctamente"
}
```

**Status Code:** `200 OK`

---

## 👥 Usuarios

### POST /users/

Crea un nuevo usuario en el sistema.

**Request:**
```http
POST /users/
Content-Type: application/json

{
  "name": "Juan Pérez",
  "email": "juan@ejemplo.com"
}
```

**Request Schema:**
```json
{
  "name": "string (requerido)",
  "email": "string (requerido, formato email válido)"
}
```

**Response (éxito):**
```json
{
  "id": 1,
  "name": "Juan Pérez",
  "email": "juan@ejemplo.com",
  "is_active": true,
  "created_at": "2025-08-12T11:02:03.361908Z"
}
```

**Status Code:** `200 OK`

**Errores posibles:**
- `400 Bad Request` - Email ya registrado
- `422 Unprocessable Entity` - Datos inválidos

**Ejemplo de error:**
```json
{
  "detail": "Email already registered"
}
```

---

### GET /users/

Obtiene una lista paginada de todos los usuarios.

**Request:**
```http
GET /users/?skip=0&limit=100
```

**Query Parameters:**
- `skip` (opcional): Número de registros a omitir (default: 0)
- `limit` (opcional): Número máximo de registros a retornar (default: 100)

**Response:**
```json
[
  {
    "id": 1,
    "name": "Juan Pérez",
    "email": "juan@ejemplo.com",
    "is_active": true,
    "created_at": "2025-08-12T11:02:03.361908Z"
  },
  {
    "id": 2,
    "name": "María García",
    "email": "maria@ejemplo.com",
    "is_active": true,
    "created_at": "2025-08-12T11:05:15.123456Z"
  }
]
```

**Status Code:** `200 OK`

---

### GET /users/{id}

Obtiene un usuario específico por su ID.

**Request:**
```http
GET /users/1
```

**Path Parameters:**
- `id`: ID del usuario (integer)

**Response (éxito):**
```json
{
  "id": 1,
  "name": "Juan Pérez",
  "email": "juan@ejemplo.com",
  "is_active": true,
  "created_at": "2025-08-12T11:02:03.361908Z"
}
```

**Status Code:** `200 OK`

**Errores posibles:**
- `404 Not Found` - Usuario no encontrado

**Ejemplo de error:**
```json
{
  "detail": "Usuario no encontrado"
}
```

---

## 🛍️ Productos

### POST /products/

Crea un nuevo producto en el sistema.

**Request:**
```http
POST /products/
Content-Type: application/json

{
  "name": "Laptop Dell",
  "description": "Laptop para desarrollo",
  "price": 999.99,
  "stock": 10
}
```

**Request Schema:**
```json
{
  "name": "string (requerido)",
  "description": "string (opcional)",
  "price": "float (requerido)",
  "stock": "integer (opcional, default: 0)"
}
```

**Response (éxito):**
```json
{
  "id": 1,
  "name": "Laptop Dell",
  "description": "Laptop para desarrollo",
  "price": 999.99,
  "stock": 10,
  "is_available": true,
  "created_at": "2025-08-12T11:02:08.412563Z"
}
```

**Status Code:** `200 OK`

**Errores posibles:**
- `422 Unprocessable Entity` - Datos inválidos (precio negativo, etc.)

---

### GET /products/

Obtiene una lista paginada de todos los productos disponibles.

**Request:**
```http
GET /products/?skip=0&limit=100
```

**Query Parameters:**
- `skip` (opcional): Número de registros a omitir (default: 0)
- `limit` (opcional): Número máximo de registros a retornar (default: 100)

**Nota:** Solo retorna productos con `is_available = true`

**Response:**
```json
[
  {
    "id": 1,
    "name": "Laptop Dell",
    "description": "Laptop para desarrollo",
    "price": 999.99,
    "stock": 10,
    "is_available": true,
    "created_at": "2025-08-12T11:02:08.412563Z"
  },
  {
    "id": 2,
    "name": "Mouse Inalámbrico",
    "description": "Mouse ergonómico",
    "price": 25.50,
    "stock": 50,
    "is_available": true,
    "created_at": "2025-08-12T11:10:30.789012Z"
  }
]
```

**Status Code:** `200 OK`

---

### GET /products/{id}

Obtiene un producto específico por su ID.

**Request:**
```http
GET /products/1
```

**Path Parameters:**
- `id`: ID del producto (integer)

**Response (éxito):**
```json
{
  "id": 1,
  "name": "Laptop Dell",
  "description": "Laptop para desarrollo",
  "price": 999.99,
  "stock": 10,
  "is_available": true,
  "created_at": "2025-08-12T11:02:08.412563Z"
}
```

**Status Code:** `200 OK`

**Errores posibles:**
- `404 Not Found` - Producto no encontrado

**Ejemplo de error:**
```json
{
  "detail": "Producto no encontrado"
}
```

---

## 🔄 Esquemas de Datos

### User Schema

**UserCreate (Request):**
```json
{
  "name": "string",
  "email": "string (formato email)"
}
```

**User (Response):**
```json
{
  "id": "integer",
  "name": "string",
  "email": "string",
  "is_active": "boolean",
  "created_at": "string (ISO 8601 datetime)"
}
```

### Product Schema

**ProductCreate (Request):**
```json
{
  "name": "string",
  "description": "string | null",
  "price": "float",
  "stock": "integer (default: 0)"
}
```

**Product (Response):**
```json
{
  "id": "integer",
  "name": "string",
  "description": "string | null",
  "price": "float",
  "stock": "integer",
  "is_available": "boolean",
  "created_at": "string (ISO 8601 datetime)"
}
```

---

## ⚠️ Códigos de Error

| Código | Descripción | Ejemplo |
|--------|-------------|---------|
| `200` | OK | Operación exitosa |
| `400` | Bad Request | Email ya registrado |
| `404` | Not Found | Usuario/Producto no encontrado |
| `422` | Unprocessable Entity | Datos de entrada inválidos |
| `500` | Internal Server Error | Error del servidor |

---

## 🧪 Ejemplos con cURL

### Crear usuario
```bash
curl -X POST "http://localhost:8000/users/" \
  -H "Content-Type: application/json" \
  -d '{"name": "Juan Pérez", "email": "juan@ejemplo.com"}'
```

### Obtener todos los usuarios
```bash
curl -X GET "http://localhost:8000/users/"
```

### Crear producto
```bash
curl -X POST "http://localhost:8000/products/" \
  -H "Content-Type: application/json" \
  -d '{"name": "Laptop Dell", "description": "Laptop para desarrollo", "price": 999.99, "stock": 10}'
```

### Obtener producto específico
```bash
curl -X GET "http://localhost:8000/products/1"
```

---

## 🚀 Documentación Interactiva

FastAPI genera automáticamente documentación interactiva:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

Estas interfaces permiten:
- ✅ Probar endpoints directamente
- ✅ Ver esquemas de datos
- ✅ Explorar respuestas de ejemplo
- ✅ Generar código cliente

---

## 🔧 Notas de Desarrollo

1. **Validaciones automáticas**: FastAPI valida automáticamente los tipos de datos
2. **Documentación auto-generada**: Los esquemas se generan desde los modelos Pydantic
3. **Paginación**: Los endpoints de listado soportan `skip` y `limit`
4. **Filtros**: Los productos solo muestran items con `is_available = true`
5. **Transacciones**: La base de datos usa transacciones automáticas con rollback en errores