# 🛍️ API E-commerce con FastAPI

Una API REST moderna para e-commerce construida con FastAPI, PostgreSQL y SQLAlchemy. Perfecta para aprender desarrollo web con Python de forma práctica y escalable.

![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=FastAPI&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2CA5E0?style=for-the-badge&logo=docker&logoColor=white)

## ✨ Características

- ⚡ **FastAPI**: Framework moderno y rápido para APIs
- 🗄️ **PostgreSQL**: Base de datos robusta con SQLAlchemy async
- 📝 **Documentación automática**: Swagger UI y ReDoc integrados
- ✅ **Validación de datos**: Con Pydantic schemas
- 🐳 **Docker**: Configuración completa para desarrollo
- 📊 **Paginación**: Listados con skip/limit
- 🛡️ **Manejo de errores**: Respuestas HTTP consistentes

## 🚀 Inicio Rápido

### Prerrequisitos

- Python 3.10+
- Docker y Docker Compose
- Git

### Instalación

1. **Clona el repositorio:**
```bash
git clone https://github.com/CristianZArellano/ecomerce_api_fast_API.git
cd ecomerce_api_fast_API
```

2. **Instala las dependencias:**
```bash
pip install -r requirements.txt
```

3. **Configura el entorno:**
```bash
# Crea los directorios necesarios
mkdir -p data/postgres data/redis

# El archivo .env ya está configurado con valores por defecto
```

4. **Inicia la base de datos:**
```bash
docker compose up -d postgres
```

5. **Ejecuta la API:**
```bash
python main.py
```

¡La API estará disponible en http://localhost:8000! 🎉

## 📚 Documentación

### Documentación Interactiva
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Documentación Detallada
- **[API_DOCUMENTATION.md](./API_DOCUMENTATION.md)**: Guía completa con ejemplos
- **[CLAUDE.md](./CLAUDE.md)**: Guía para desarrollo con Claude Code

## 🔗 Endpoints Principales

### Sistema
- `GET /` - Bienvenida
- `GET /health` - Health check

### Usuarios
- `POST /users/` - Crear usuario
- `GET /users/` - Listar usuarios
- `GET /users/{id}` - Obtener usuario

### Productos
- `POST /products/` - Crear producto
- `GET /products/` - Listar productos
- `GET /products/{id}` - Obtener producto

## 🧪 Ejemplos de Uso

### Crear un usuario
```bash
curl -X POST \"http://localhost:8000/users/\" \\
  -H \"Content-Type: application/json\" \\
  -d '{\"name\": \"Juan Pérez\", \"email\": \"juan@ejemplo.com\"}'
```

### Crear un producto
```bash
curl -X POST \"http://localhost:8000/products/\" \\
  -H \"Content-Type: application/json\" \\
  -d '{
    \"name\": \"Laptop Dell\", 
    \"description\": \"Laptop para desarrollo\", 
    \"price\": 999.99, 
    \"stock\": 10
  }'
```

### Listar productos
```bash
curl http://localhost:8000/products/
```

## 🏗️ Arquitectura

```
api_ecomerce/
├── app/
│   ├── __init__.py          # Paquete de la aplicación
│   ├── config.py           # Configuración con Pydantic Settings
│   ├── database.py         # Conexión y sesión de base de datos
│   ├── models.py           # Modelos SQLAlchemy (User, Product)
│   ├── schemas.py          # Esquemas Pydantic para validación
│   └── crud.py             # Operaciones CRUD
├── main.py                 # Aplicación FastAPI principal
├── requirements.txt        # Dependencias Python
├── docker-compose.yml      # Servicios de base de datos
└── README.md              # Este archivo
```

## 🛠️ Tecnologías Utilizadas

### Backend
- **FastAPI 0.116.1**: Framework web moderno
- **SQLAlchemy 2.0.43**: ORM async para Python
- **asyncpg 0.29.0**: Driver PostgreSQL async
- **Pydantic 2.11.7**: Validación de datos

### Base de Datos
- **PostgreSQL 15**: Base de datos principal
- **Redis 7**: Cache y sesiones (opcional)

### DevOps
- **Docker Compose**: Orquestación de servicios
- **Uvicorn**: Servidor ASGI de alto rendimiento

## 🔧 Desarrollo

### Comandos útiles

```bash
# Iniciar servicios
docker compose up -d

# Ver logs de la base de datos
docker compose logs -f postgres

# Reiniciar la API (con auto-reload)
python main.py

# Verificar el estado
curl http://localhost:8000/health
```

### Estructura de la base de datos

**Tabla Users:**
- id (Primary Key)
- name (VARCHAR)
- email (VARCHAR, Unique)
- is_active (Boolean)
- created_at (Timestamp)

**Tabla Products:**
- id (Primary Key)
- name (VARCHAR)
- description (TEXT)
- price (Float)
- stock (Integer)
- is_available (Boolean)
- created_at (Timestamp)

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📋 TODO / Próximas Funcionalidades

- [ ] Sistema de autenticación JWT
- [ ] Relaciones entre modelos (Orders, OrderItems)
- [ ] Upload de imágenes para productos
- [ ] Sistema de categorías
- [ ] Filtros y búsqueda avanzada
- [ ] Rate limiting
- [ ] Tests automatizados
- [ ] CI/CD con GitHub Actions
- [ ] API de pagos
- [ ] Notificaciones por email

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo [LICENSE](LICENSE) para más detalles.

## 👨‍💻 Autor

**Cristian Arellano**
- GitHub: [@CristianZArellano](https://github.com/CristianZArellano)
- Proyecto: [ecomerce_api_fast_API](https://github.com/CristianZArellano/ecomerce_api_fast_API)

---

⭐ ¡No olvides darle una estrella al proyecto si te resultó útil!

## 🚨 Notas Importantes

- Este es un proyecto educativo, no recomendado para producción sin ajustes de seguridad
- Las credenciales están en archivos de configuración para facilitar el aprendizaje
- Para producción, usa variables de entorno seguras y autenticación robusta