# 🚀 Configuración de Postman para API E-commerce

Esta guía te ayudará a configurar Postman para probar todos los endpoints de la API E-commerce de forma completa y automatizada.

## 📋 Contenido del Paquete

- **`postman_collection.json`**: Colección completa con todos los endpoints
- **`postman_environment.json`**: Variables de entorno para desarrollo local
- **Este archivo**: Instrucciones de configuración

## 🔧 Instalación y Configuración

### Paso 1: Instalar Postman

Si no tienes Postman instalado:
- Descarga desde: https://www.postman.com/downloads/
- O usa la versión web: https://web.postman.com/

### Paso 2: Importar la Colección

1. **Abre Postman**
2. **Haz clic en "Import"** (botón en la esquina superior izquierda)
3. **Selecciona "Choose files"**
4. **Busca y selecciona** `postman_collection.json`
5. **Haz clic en "Import"**

✅ **Resultado**: Verás la colección "API E-commerce FastAPI" en tu sidebar

### Paso 3: Importar el Environment

1. **En Postman, haz clic en el ícono de engranaje** ⚙️ (arriba derecha)
2. **Selecciona "Import"**
3. **Busca y selecciona** `postman_environment.json`
4. **Haz clic en "Import"**

✅ **Resultado**: Verás "API E-commerce - Local Development" en la lista de environments

### Paso 4: Activar el Environment

1. **En el dropdown de environments** (esquina superior derecha)
2. **Selecciona** "API E-commerce - Local Development"

✅ **Resultado**: Las variables estarán disponibles para todas las requests

## 🏃‍♂️ Iniciar la API

Antes de probar, asegúrate de que la API esté corriendo:

```bash
# Desde el directorio del proyecto
docker compose up -d postgres
python main.py
```

Verifica que esté funcionando:
- 🌐 http://localhost:8000 (debería mostrar mensaje de bienvenida)
- 📚 http://localhost:8000/docs (documentación Swagger)

## 📁 Estructura de la Colección

### 🏠 Sistema
- **Endpoint de Bienvenida**: Verifica que la API responda
- **Health Check**: Verifica el estado de salud

### 👥 Usuarios
- **Crear Usuario**: Crea un nuevo usuario
- **Listar Usuarios**: Obtiene todos los usuarios (paginado)
- **Obtener Usuario por ID**: Busca usuario específico
- **Crear Usuario - Email Duplicado**: Prueba validación de error

### 🛍️ Productos
- **Crear Producto**: Crea un nuevo producto
- **Listar Productos**: Obtiene productos disponibles (paginado)
- **Obtener Producto por ID**: Busca producto específico
- **Crear Producto - Sin Descripción**: Prueba campos opcionales

### ❌ Pruebas de Error
- **Usuario No Encontrado (404)**: Prueba error de usuario inexistente
- **Producto No Encontrado (404)**: Prueba error de producto inexistente
- **Email Inválido (422)**: Prueba validación de formato de email

## 🧪 Ejecutar Pruebas

### Prueba Individual
1. **Selecciona cualquier request**
2. **Haz clic en "Send"**
3. **Revisa la respuesta y los tests automáticos**

### Ejecutar Toda la Colección
1. **Haz clic derecho en la colección**
2. **Selecciona "Run collection"**
3. **Haz clic en "Run API E-commerce FastAPI"**

✅ **Resultado**: Verás un reporte completo con todos los tests

## 🔍 Features Avanzados

### Tests Automáticos Incluidos
Cada request tiene tests que verifican:
- ✅ Status codes correctos
- ✅ Estructura de respuestas
- ✅ Tipos de datos
- ✅ Validaciones de negocio
- ✅ Tiempos de respuesta

### Variables Dinámicas
- **`{{created_user_id}}`**: Se actualiza automáticamente al crear usuarios
- **`{{created_product_id}}`**: Se actualiza automáticamente al crear productos
- **`{{base_url}}`**: URL base configurable por environment

### Scripts Pre/Post Request
- **Pre-request**: Configura variables automáticamente
- **Tests**: Valida respuestas y actualiza variables

## 🎯 Ejemplos de Uso

### Flujo Completo de Pruebas
```
1. Health Check → Verifica API funcionando
2. Crear Usuario → Obtiene ID automáticamente
3. Obtener Usuario por ID → Usa el ID creado
4. Crear Producto → Obtiene ID automáticamente
5. Listar Productos → Verifica que aparezca
6. Pruebas de Error → Valida manejo de errores
```

### Personalizar Tests
Puedes modificar los tests en la pestaña "Tests" de cada request:

```javascript
pm.test("Mi test personalizado", function () {
    const responseJson = pm.response.json();
    pm.expect(responseJson.name).to.include("Esperado");
});
```

## 🌍 Environments Adicionales

Puedes crear environments adicionales para:

### Environment de Producción
```json
{
  "base_url": "https://tu-api.com",
  "api_version": "1.0.0"
}
```

### Environment de Testing
```json
{
  "base_url": "http://localhost:8001",
  "api_version": "1.0.0-test"
}
```

## 🐛 Solución de Problemas

### Error: "Could not connect to server"
- ✅ Verifica que la API esté corriendo en `http://localhost:8000`
- ✅ Ejecuta `python main.py` desde el directorio del proyecto
- ✅ Verifica que PostgreSQL esté corriendo: `docker compose up -d postgres`

### Error: Variables no definidas
- ✅ Asegúrate de haber importado el environment
- ✅ Selecciona el environment correcto en el dropdown
- ✅ Verifica que `{{base_url}}` muestre `http://localhost:8000`

### Tests fallan
- ✅ Ejecuta primero "Health Check" para verificar conectividad
- ✅ Los tests pueden fallar si la base de datos está vacía
- ✅ Ejecuta la colección completa en orden para mejores resultados

## 📊 Reportes y Monitoreo

### Exportar Resultados
Después de ejecutar la colección:
1. **Haz clic en "Export Results"**
2. **Selecciona formato** (JSON/HTML)
3. **Guarda el reporte**

### Monitor Continuo
Postman Pro permite configurar monitores que ejecuten las pruebas automáticamente cada X minutos.

## 🔗 Enlaces Útiles

- **Documentación API**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **GitHub del Proyecto**: https://github.com/CristianZArellano/ecomerce_api_fast_API
- **Documentación Postman**: https://learning.postman.com/

## 📝 Notas Importantes

1. **Orden de Ejecución**: Algunos tests dependen de otros (ej: obtener usuario por ID necesita que se haya creado primero)

2. **Base de Datos**: Los tests crean datos reales en la base de datos. En producción usa una base de datos de pruebas separada.

3. **Variables Automáticas**: Las variables `created_user_id` y `created_product_id` se actualizan automáticamente para facilitar las pruebas.

4. **Personalización**: Puedes modificar los valores en el environment para personalizar los datos de prueba.

---

¡Ahora tienes todo configurado para probar la API de manera profesional! 🎉

Si tienes problemas, revisa la documentación en `API_DOCUMENTATION.md` o crea un issue en GitHub.