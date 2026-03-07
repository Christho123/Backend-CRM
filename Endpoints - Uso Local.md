## Backend - CRM - Uso de Endpoints

### 1. Información general

- **Nombre del proyecto**: Backend - CRM
- **Base URL (local)**:

```text
http://127.0.0.1:8000/
```

- **Prefijo común de APIs**:

```text
http://127.0.0.1:8000/api/
```

- **Herramienta recomendada para pruebas**: Postman (colecciones locales).

### 2. Estructura del proyecto (resumen)

- **settings/**
  - `settings.py` (configuración principal Django/DRF/JWT)
  - `urls.py` (enrutador raíz)
- **architect/**
  - `views/auth.py` (login, registro, logout)
  - `views/user.py` (gestión de usuarios)
  - `views/permission.py` (permisos y roles)
  - `serializers/auth.py` (login + 2FA y registro)
- **users_profiles/**
  - `models/user.py` (usuario personalizado `AUTH_USER_MODEL`)
  - `models/user_verification_code.py` (códigos de verificación)
  - `views/user.py` (perfil propio, búsqueda de usuarios)
  - `views/profile.py` (perfil, configuración, estado de completitud)
  - `views/password.py` (cambio/reset de contraseña)
  - `views/verification.py` (códigos de verificación, cambio/verificación de email)
  - `services/verification_service.py` (envío/verificación de códigos)
- **types_documents/**
  - `models/document_type.py`
  - `views/document_type.py` (CRUD tipos de documento)
- **ubi_geo/**
  - `models/country.py`, `region.py`, `province.py`, `district.py`
  - `views/region.py`, `views/province.py`, `views/district.py`
- **employees/**
  - `models/employee.py`
  - `views/employee.py` (empleados y fotos)
- **products_configurations/**
  - `models/category.py`, `brand.py`, `supplier.py`, `product.py`
  - `views/category.py`, `views/brand.py`, `views/supplier.py`, `views/product.py`
- **audits/**
  - `models/audit_session.py`, `audit_event.py`
  - `views/audit.py` (auditoría de sesiones y eventos)
- **analytics/**
  - `views/analytics.py` (resúmenes y series de tiempo)

### 3. Primer paso obligatorio (crear superusuario)

En la raíz del proyecto (`Backend-CRM`), ejecutar en la terminal:

```bash
python manage.py createsuperuser
```

Este usuario se puede usar para:
- Acceder al panel `/admin/`.
- Probar endpoints protegidos con permisos de administrador (por ejemplo, auditoría y analytics).

---

## 4. Endpoints independientes (base del sistema)

### 4.1. Autenticación y Arquitectura (`/api/architect/`)

#### 4.1.1. Login con 2FA por email

- **URL**: `POST http://127.0.0.1:8000/api/architect/auth/login/`
- **Descripción**: Inicio de sesión con validación de contraseña y segundo factor enviado por email.
- **Autenticación previa**: No requerida (es el login).
- **Uso en Postman**:
  - Body → `raw` → JSON.

**Paso 1 – Enviar email y contraseña (sin código):**

```json
{
  "email": "usuario@example.com",
  "password": "MiClaveSegura123"
}
```

**Respuesta esperada (200 OK):**

```json
{
  "2fa_required": true,
  "challenge_id": 14,
  "email": "usuario@example.com",
  "message": "Se ha enviado un código de verificación a tu correo electrónico."
}
```

El código 2FA llegará al correo del usuario (6 dígitos) con asunto **"Código de acceso - Sistema CRM"**.

**Paso 2 – Confirmar código 2FA y recibir tokens:**

```json
{
  "email": "usuario@example.com",
  "password": "MiClaveSegura123",
  "code": "785386",
  "challenge_id": 14
}
```

**Respuesta exitosa (200 OK):**

```json
{
  "email": "usuario@example.com",
  "refresh": "REFRESH_TOKEN_JWT",
  "access": "ACCESS_TOKEN_JWT",
  "user_id": 1,
  "audit_session_id": 6,
  "2fa_verified": true
}
```

> **Nota**: A partir de aquí, todos los endpoints protegidos requieren el header:
> `Authorization: Bearer ACCESS_TOKEN_JWT`

#### 4.1.2. Registro de usuario

- **URL**: `POST http://127.0.0.1:8000/api/architect/auth/register/`
- **Autenticación**: No requerida.

**Body (JSON):**

```json
{
  "user_name": "csosa",
  "email": "nuevo.usuario@example.com",
  "document_number": "12345678",
  "password": "MiClaveSegura123",
  "password_confirm": "MiClaveSegura123"
}
```

**Respuesta (201 Created):**

```json
{
  "user_name": "csosa",
  "email": "nuevo.usuario@example.com",
  "document_number": "12345678"
}
```

#### 4.1.3. Logout

- **URL**: `POST http://127.0.0.1:8000/api/architect/auth/logout/`
- **Autenticación**: Requerida (Bearer token).

**Headers:**

```text
Authorization: Bearer ACCESS_TOKEN_JWT
Content-Type: application/json
```

**Body (JSON):**

```json
{
  "refresh": "REFRESH_TOKEN_JWT"
}
```

**Respuesta (200 OK):**

```json
{
  "message": "Sesión cerrada exitosamente"
}
```

#### 4.1.4. Gestión de usuarios (`/api/architect/users/`)

- **Autenticación**: Requerida.
- **Endpoints principales**:

| Método   | Endpoint                                   | Descripción                        |
|----------|--------------------------------------------|------------------------------------|
| GET      | `/api/architect/users/`                   | Listar usuarios                    |
| POST     | `/api/architect/users/`                   | Crear usuario                      |
| GET      | `/api/architect/users/{id}/`              | Ver usuario específico             |
| PUT/PATCH| `/api/architect/users/{id}/`              | Actualizar usuario                 |
| DELETE   | `/api/architect/users/{id}/`              | Eliminar usuario                   |
| POST     | `/api/architect/users/{id}/upload/`       | Subir foto de perfil               |
| PUT      | `/api/architect/users/{id}/upload/`       | Actualizar foto de perfil          |
| DELETE   | `/api/architect/users/{id}/upload/`       | Eliminar foto de perfil            |

**Ejemplo – Listar usuarios (GET):**

```http
GET http://127.0.0.1:8000/api/architect/users/
Authorization: Bearer ACCESS_TOKEN_JWT
```

**Respuesta:**

```json
[
  {
    "id": 1,
    "user_name": "admin",
    "email": "admin@example.com",
    "name": "Admin",
    "is_active": true,
    "photo_url": null
  }
]
```

**Ejemplo – Crear usuario (POST):**

```json
{
  "user_name": "empleado1",
  "email": "empleado1@example.com",
  "document_number": "87654321",
  "password": "ClaveFuerte123"
}
```

#### 4.1.5. Roles y permisos

- **Autenticación**: Requerida (idealmente usuario administrador).

**Roles (`/api/architect/roles/`):**

| Método | Endpoint                                   | Descripción        |
|--------|--------------------------------------------|--------------------|
| GET    | `/api/architect/roles/`                   | Listar roles       |
| POST   | `/api/architect/roles/`                   | Crear rol          |
| GET    | `/api/architect/roles/{id}/`              | Ver rol            |
| PUT    | `/api/architect/roles/{id}/`              | Actualizar rol     |
| DELETE | `/api/architect/roles/{id}/`              | Eliminar rol       |

**Ejemplo – Crear rol (POST):**

```json
{
  "name": "Administrador",
  "guard_name": "admin"
}
```

**Permisos (`/api/architect/permissions/`):**

| Método | Endpoint                             | Descripción        |
|--------|--------------------------------------|--------------------|
| GET    | `/api/architect/permissions/`       | Listar permisos    |

---

## 5. Endpoints independientes de catálogo

### 5.1. Tipos de documento (`/api/types_documents/`)

Base URL para este módulo:

```text
http://127.0.0.1:8000/api/types_documents/
```

- **Autenticación**: Requerida (Bearer token).
- **Endpoints**:

| Método | Endpoint                          | Descripción                    |
|--------|-----------------------------------|--------------------------------|
| GET    | `/api/types_documents/document_types/`          | Listar tipos de documento     |
| POST   | `/api/types_documents/document_types/create/`   | Crear tipo de documento       |
| PUT    | `/api/types_documents/document_types/{id}/edit/`| Editar tipo de documento      |
| DELETE | `/api/types_documents/document_types/{id}/delete/`| Eliminar tipo de documento |

**Ejemplo – Listar:**

```http
GET http://127.0.0.1:8000/api/types_documents/document_types/
Authorization: Bearer ACCESS_TOKEN_JWT
```

**Respuesta:**

```json
{
  "document_types": [
    {
      "id": 1,
      "name": "DNI",
      "description": "Documento Nacional de Identidad"
    }
  ]
}
```

**Ejemplo – Crear:**

```json
{
  "name": "RUC",
  "description": "Registro Único de Contribuyentes"
}
```

---

### 5.2. Ubigeo (`/api/locations/`)

Base URL para este módulo:

```text
http://127.0.0.1:8000/api/locations/
```

Endpoints generados por `DefaultRouter` (solo lectura):

| Método | Endpoint                      | Descripción                 |
|--------|-------------------------------|-----------------------------|
| GET    | `/api/locations/regions/`     | Listar regiones             |
| GET    | `/api/locations/regions/{id}/`| Ver región                  |
| GET    | `/api/locations/provinces/`   | Listar provincias (filtro `?region=` opcional) |
| GET    | `/api/locations/provinces/{id}/`| Ver provincia             |
| GET    | `/api/locations/districts/`   | Listar distritos (filtro `?province=` opcional)|
| GET    | `/api/locations/districts/{id}/`| Ver distrito             |

**Ejemplo – Provincias por región:**

```http
GET http://127.0.0.1:8000/api/locations/provinces/?region=1
Authorization: Bearer ACCESS_TOKEN_JWT
```

**Respuesta (ejemplo simplificado):**

```json
[
  {
    "id": 10,
    "name": "Lima",
    "region": 1
  }
]
```

---

## 6. Endpoints de perfil de usuario (`/api/profiles/`)

Base URL:

```text
http://127.0.0.1:8000/api/profiles/
```

Todos requieren autenticación (Bearer).

### 6.1. Usuario autenticado

| Método | Endpoint                    | Descripción                         |
|--------|-----------------------------|-------------------------------------|
| GET    | `/api/profiles/user/me/`    | Obtener datos del usuario actual   |
| PUT    | `/api/profiles/user/me/update/` | Actualizar datos del usuario   |
| GET    | `/api/profiles/user/profile/`   | Perfil completo del usuario       |
| GET    | `/api/profiles/user/search/?q=texto` | Buscar usuarios activos      |

**Ejemplo – Obtener usuario actual:**

```http
GET http://127.0.0.1:8000/api/profiles/user/me/
Authorization: Bearer ACCESS_TOKEN_JWT
```

### 6.2. Perfil y configuración

| Método | Endpoint                               | Descripción                           |
|--------|----------------------------------------|---------------------------------------|
| GET    | `/api/profiles/profiles/me/`          | Obtener perfil propio                 |
| POST   | `/api/profiles/profiles/create/`      | Crear/actualizar perfil               |
| GET    | `/api/profiles/profiles/settings/`    | Obtener configuración de perfil       |
| PUT    | `/api/profiles/profiles/settings/`    | Actualizar configuración de perfil    |
| GET    | `/api/profiles/profiles/completion/`  | Porcentaje de completitud de perfil   |

### 6.3. Seguridad: contraseñas

Base: `/api/profiles/password/`

| Método | Endpoint                        | Descripción                            |
|--------|---------------------------------|----------------------------------------|
| POST   | `/api/profiles/password/change/`   | Cambiar contraseña (autenticado)      |
| POST   | `/api/profiles/password/reset/`    | Solicitar reset (usa verificación)    |
| POST   | `/api/profiles/password/reset/confirm/` | Confirmar reset con código        |
| POST   | `/api/profiles/password/strength/` | Verificar fortaleza de contraseña     |
| GET    | `/api/profiles/password/history/`  | Historial simple de cambios           |
| GET    | `/api/profiles/password/policy/`   | Ver política de contraseñas           |

**Ejemplo – Cambiar contraseña:**

```json
{
  "old_password": "MiClaveSegura123",
  "new_password": "NuevaClaveFuerte456",
  "new_password_confirm": "NuevaClaveFuerte456"
}
```

### 6.4. Seguridad: verificación de email

Base: `/api/profiles/verification/`

| Método | Endpoint                                | Descripción                                   |
|--------|-----------------------------------------|-----------------------------------------------|
| POST   | `/api/profiles/verification/code/`      | Solicitar código (distintos tipos)            |
| POST   | `/api/profiles/verification/code/resend/`| Reenviar código                             |
| GET    | `/api/profiles/verification/status/`    | Estado de verificaciones activas              |
| POST   | `/api/profiles/verification/email/change/` | Solicitar cambio de email                 |
| POST   | `/api/profiles/verification/email/change/confirm/` | Confirmar cambio de email         |
| POST   | `/api/profiles/verification/email/`     | Enviar código para verificar email de registro|
| POST   | `/api/profiles/verification/email/confirm/` | Confirmar verificación de email         |

---

## 7. Endpoints dependientes: empleados (`/api/employees/`)

Dependen de:
- Tipos de documento (`types_documents`).
- Ubigeo (`locations`).
- Roles (opcional).

Base:

```text
http://127.0.0.1:8000/api/employees/
```

Autenticación: Requerida.

| Método   | Endpoint                                      | Descripción                  |
|----------|-----------------------------------------------|------------------------------|
| GET      | `/api/employees/employee/`                   | Listar empleados             |
| POST     | `/api/employees/employee/create/`            | Crear empleado               |
| GET      | `/api/employees/employee/{id}/`              | Ver empleado                 |
| PUT/PATCH| `/api/employees/employee/{id}/edit/`         | Actualizar empleado          |
| DELETE   | `/api/employees/employee/{id}/delete/`       | Eliminar empleado            |
| POST     | `/api/employees/employee/{id}/photo/`        | Subir foto de empleado       |
| PUT      | `/api/employees/employee/{id}/photo/edit/`   | Actualizar foto              |
| DELETE   | `/api/employees/employee/{id}/photo/delete/` | Eliminar foto                |

**Ejemplo – Crear empleado (POST `/employee/create/`):**

```json
{
  "name": "Juan",
  "last_name_paternal": "Pérez",
  "last_name_maternal": "García",
  "document_type": 1,
  "document_number": "12345678",
  "email": "juan.perez@example.com",
  "gender": "M",
  "phone": "+51999999999",
  "birth_date": "1990-01-01",
  "region": 1,
  "province": 10,
  "district": 100,
  "rol": 2,
  "salary": 2500.0,
  "address": "Av. Siempre Viva 742"
}
```

---

## 8. Endpoints dependientes: configuraciones de productos (`/api/products_configurations/`)

Todos requieren autenticación.

### 8.1. Categorías (`category`)

Base:

```text
http://127.0.0.1:8000/api/products_configurations/category/
```

| Método | Endpoint                           | Descripción          |
|--------|------------------------------------|----------------------|
| GET    | `/category/`                       | Listar categorías    |
| POST   | `/category/create/`                | Crear categoría      |
| GET    | `/category/{id}/`                  | Ver categoría        |
| PUT    | `/category/{id}/edit/`             | Actualizar categoría |
| DELETE | `/category/{id}/delete/`           | Eliminar categoría   |

**Ejemplo – Crear categoría:**

```json
{
  "name": "Celulares",
  "description": "Equipos móviles"
}
```

### 8.2. Proveedores (`supplier`)

Base:

```text
http://127.0.0.1:8000/api/products_configurations/supplier/
```

| Método | Endpoint                          | Descripción                |
|--------|-----------------------------------|----------------------------|
| GET    | `/supplier/`                      | Listar proveedores         |
| POST   | `/supplier/create/`               | Crear proveedor            |
| GET    | `/supplier/{id}/`                 | Ver proveedor              |
| PUT    | `/supplier/{id}/edit/`            | Actualizar proveedor       |
| DELETE | `/supplier/{id}/delete/`          | Eliminar proveedor         |

**Ejemplo – Crear proveedor:**

```json
{
  "ruc": "20123456789",
  "company_name": "Proveedor SAC",
  "business_name": "Proveedor Comercial",
  "representative": "Carlos Ramírez",
  "phone": "+51987654321",
  "email": "contacto@proveedor.com",
  "address": "Av. Principal 123",
  "account_number": "001-123456789",
  "region": 1,
  "province": 10,
  "district": 100
}
```

### 8.3. Marcas (`brand`)

Base:

```text
http://127.0.0.1:8000/api/products_configurations/brand/
```

| Método | Endpoint                        | Descripción              |
|--------|---------------------------------|--------------------------|
| GET    | `/brand/`                       | Listar marcas            |
| POST   | `/brand/create/`                | Crear marca              |
| GET    | `/brand/{id}/`                  | Ver marca                |
| PUT    | `/brand/{id}/edit/`             | Actualizar marca         |
| DELETE | `/brand/{id}/delete/`           | Eliminar marca           |

**Ejemplo – Crear marca:**

```json
{
  "name": "Samsung",
  "description": "Marca de equipos móviles",
  "country": 1
}
```

### 8.4. Productos (`product`)

Base:

```text
http://127.0.0.1:8000/api/products_configurations/product/
```

| Método   | Endpoint                              | Descripción                 |
|----------|---------------------------------------|-----------------------------|
| GET      | `/product/`                           | Listar productos            |
| POST     | `/product/create/`                    | Crear producto              |
| GET      | `/product/{id}/`                      | Ver producto                |
| PUT/PATCH| `/product/{id}/edit/`                 | Actualizar producto         |
| DELETE   | `/product/{id}/delete/`               | Eliminar producto           |
| POST     | `/product/{id}/photo/`                | Subir foto de producto      |
| PUT      | `/product/{id}/photo/edit/`           | Actualizar foto             |
| DELETE   | `/product/{id}/photo/delete/`         | Eliminar foto               |

**Ejemplo – Crear producto:**

```json
{
  "name": "iPhone 15",
  "description": "Smartphone de alta gama",
  "model": "A3100",
  "unit_price": 3500.0,
  "sales_price": 4200.0,
  "stock": 10,
  "discount": 0,
  "category_id": 1,
  "supplier_id": 1,
  "brand_id": 1,
  "state": "ACTIVE"
}
```

---

## 9. Auditoría (`/api/audits/`) – dependiente de login

Base:

```text
http://127.0.0.1:8000/api/audits/
```

- **Autenticación**: Requerida.
- **Permisos**: Solo administradores (`IsAdminUser`).

| Método | Endpoint                          | Descripción                                     |
|--------|-----------------------------------|-------------------------------------------------|
| GET    | `/sessions/`                      | Tabla de acciones (movimientos)                |
| GET    | `/events/`                        | Alias de `sessions/`                           |
| GET    | `/users/{user_id}/`               | Detalle de usuario + eventos y sesiones        |

**Ejemplo – Listar eventos auditados:**

```http
GET http://127.0.0.1:8000/api/audits/sessions/?user_id=1&active=true
Authorization: Bearer ACCESS_TOKEN_JWT
```

---

## 10. Analytics (`/api/analytics/`) – dependiente de auditoría

Base:

```text
http://127.0.0.1:8000/api/analytics/
```

- **Autenticación**: Requerida.
- **Permisos**: Solo administradores (`IsAdminUser`).

| Método | Endpoint                    | Descripción                                |
|--------|-----------------------------|--------------------------------------------|
| GET    | `/summary/`                 | Resumen general del sistema                |
| GET    | `/clicks/`                  | Serie de tiempo de clicks/auditoría        |
| GET    | `/new-employees/`           | Serie de tiempo de nuevos empleados        |
| GET    | `/new-users/`               | Serie de tiempo de nuevos usuarios         |

**Ejemplo – Resumen general:**

```http
GET http://127.0.0.1:8000/api/analytics/summary/
Authorization: Bearer ACCESS_TOKEN_JWT
```

**Respuesta (ejemplo simplificado):**

```json
{
  "total_employees": 15,
  "total_users": 20,
  "total_clicks": 350,
  "product_clicks": 120
}
```

---

## 11. Notas finales para uso local

- Todas las pruebas se recomiendan en **Postman**, usando la base URL `http://127.0.0.1:8000/`.
- La mayoría de endpoints requiere autenticación:
  - Primero hacer login con el flujo de **2FA**.
  - Copiar el `access` token y usarlo en el header `Authorization: Bearer ...`.
- Para cualquier error de permisos, revisar:
  - Que el usuario esté activo.
  - Que el token no haya expirado.
  - Que el endpoint no requiera rol de administrador.

