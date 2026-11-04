# Tablón de Anuncios — Práctica N° 4

Aplicación web desarrollada con **Python + Flask** para gestionar un tablón de anuncios
institucional. Incluye autenticación, administración de usuarios, categorías y anuncios,
base de datos relacional MariaDB/MySQL y una interfaz responsive con **Bootstrap 5**.

## Características

- **Application Factory** mediante `create_app()` en `app/__init__.py`.
- **Blueprints** separados por dominio: `main`, `auth`, `usuarios`, `categorias`, `anuncios`.
- **Flask-SQLAlchemy** como ORM y **Flask-Login** para la sesión.
- Contraseñas almacenadas con hash (`werkzeug.security`), nunca en texto plano.
- CRUD completo de usuarios, categorías y anuncios.
- Roles `admin` y `usuario`; el administrador gestiona usuarios y categorías.
- Los anuncios pueden ser creados por cualquier usuario autenticado y editados solo por
  su autor o por un administrador.
- Tablón público con búsqueda, filtro por categoría y paginación.
- Validaciones del lado del servidor, mensajes flash y páginas de error 403/404/500.
- Datos de ejemplo y comando CLI para inicializar la base.
- Recursos de Bootstrap e iconos incluidos localmente (no depende de CDN).

## Tecnologías

| Componente | Tecnología |
|---|---|
| Lenguaje | Python 3.13 |
| Framework web | Flask 3.1 |
| ORM | Flask-SQLAlchemy 3.1 (SQLAlchemy 2.x) |
| Base de datos | MariaDB 11 / MySQL 8 |
| Autenticación | Flask-Login + Werkzeug |
| Interfaz | Bootstrap 5.3 + Bootstrap Icons |
| Pruebas | pytest |

## Estructura del proyecto

```text
practica4_emergentes/
├── app/
│   ├── __init__.py              # create_app(): fábrica de la aplicación
│   ├── extensions.py            # db, login_manager
│   ├── models.py                # Usuario, Categoria, Anuncio
│   ├── decorators.py            # @admin_required
│   ├── utils.py                 # validaciones y redirecciones seguras
│   ├── cli.py                   # init-db, seed-db, reset-db
│   ├── blueprints/
│   │   ├── main.py              # tablón público
│   │   ├── auth.py              # login / logout
│   │   ├── usuarios.py          # CRUD de usuarios
│   │   ├── categorias.py        # CRUD de categorías
│   │   └── anuncios.py          # CRUD de anuncios
│   ├── templates/
│   │   ├── base.html            # cabecera, menú, contenido y pie comunes
│   │   ├── macros.html          # paginación y estado vacío
│   │   ├── auth/                # inicio de sesión
│   │   ├── main/                # página principal
│   │   ├── usuarios/            # listado y formulario
│   │   ├── categorias/          # listado y formulario
│   │   ├── anuncios/            # listado, formulario y detalle
│   │   └── errors/              # 403, 404, 500
│   └── static/css/styles.css    # identidad visual institucional
├── database/
│   ├── setup.sql                # base de datos, usuario y permisos
│   └── schema.sql               # tablas, PK, FK, índices y relaciones
├── tests/                       # pruebas funcionales con pytest
├── config.py                    # configuración por variables de entorno
├── run.py                       # punto de entrada
├── requirements.txt
├── requirements-dev.txt
├── .env.example
└── README.md
```

## Diseño de la base de datos

Base de datos: **`bd_anuncios`**, motor InnoDB, codificación `utf8mb4`.

### Tabla `usuarios`

| Campo | Tipo | Restricciones |
|---|---|---|
| `id_usuario` | INT | PK, AUTO_INCREMENT |
| `nombre` | VARCHAR(120) | NOT NULL |
| `username` | VARCHAR(50) | NOT NULL, UNIQUE |
| `email` | VARCHAR(150) | NOT NULL, UNIQUE |
| `password_hash` | VARCHAR(255) | NOT NULL |
| `rol` | VARCHAR(20) | NOT NULL, CHECK (`admin`/`usuario`) |
| `activo` | TINYINT(1) | NOT NULL, DEFAULT 1 |
| `creado_en` | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP |

### Tabla `categorias`

| Campo | Tipo | Restricciones |
|---|---|---|
| `id_categoria` | INT | PK, AUTO_INCREMENT |
| `nombre` | VARCHAR(80) | NOT NULL, UNIQUE |
| `descripcion` | VARCHAR(255) | NULL |
| `creado_en` | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP |

### Tabla `anuncios`

| Campo | Tipo | Restricciones |
|---|---|---|
| `id_anuncio` | INT | PK, AUTO_INCREMENT |
| `titulo` | VARCHAR(150) | NOT NULL |
| `contenido` | TEXT | NOT NULL |
| `fecha_publicacion` | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP |
| `actualizado_en` | DATETIME | NOT NULL, ON UPDATE CURRENT_TIMESTAMP |
| `id_usuario` | INT | FK → `usuarios.id_usuario`, CASCADE |
| `id_categoria` | INT | FK → `categorias.id_categoria`, RESTRICT |

### Relaciones

- **Usuario 1 — N Anuncios**: un usuario publica muchos anuncios. Al eliminar el usuario
  se eliminan sus anuncios (`ON DELETE CASCADE`).
- **Categoría 1 — N Anuncios**: una categoría agrupa muchos anuncios. No se permite
  eliminar una categoría con anuncios asociados (`ON DELETE RESTRICT`).

```mermaid
erDiagram
    USUARIOS ||--o{ ANUNCIOS : publica
    CATEGORIAS ||--o{ ANUNCIOS : clasifica

    USUARIOS {
        int id_usuario PK
        varchar nombre
        varchar username UK
        varchar email UK
        varchar password_hash
        varchar rol
        boolean activo
        datetime creado_en
    }
    CATEGORIAS {
        int id_categoria PK
        varchar nombre UK
        varchar descripcion
        datetime creado_en
    }
    ANUNCIOS {
        int id_anuncio PK
        varchar titulo
        text contenido
        datetime fecha_publicacion
        datetime actualizado_en
        int id_usuario FK
        int id_categoria FK
    }
```

El script completo está en [`database/schema.sql`](database/schema.sql).

## Puesta en marcha

### 1. Requisitos

- Python 3.11 o superior.
- MariaDB 10.4+ o MySQL 8+ (también se puede usar SQLite, ver más abajo).

### 2. Crear la base de datos y el usuario

```bash
mysql -u root -p < database/setup.sql
mysql -u root -p < database/schema.sql
```

Esto crea la base `bd_anuncios`, el usuario `anuncios_user` (contraseña `anuncios_pass`)
y las tres tablas con sus relaciones. Si ya se usó `setup.sql`, alcanza con ejecutar
`schema.sql`.

### 3. Crear el entorno virtual e instalar dependencias

```bash
python3 -m venv .venv
source .venv/bin/activate        # En Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 4. Configurar las variables de entorno

```bash
cp .env.example .env
```

Editar `.env` si es necesario. La cadena de conexión por defecto es:

```text
mysql+pymysql://anuncios_user:anuncios_pass@127.0.0.1:3306/bd_anuncios?charset=utf8mb4
```

> **Alternativa con SQLite (sin servidor):** en `.env` usar
> `DATABASE_URL=sqlite:///bd_anuncios.sqlite3`. El resto de la aplicación funciona igual.

### 5. Crear las tablas y cargar datos de ejemplo

```bash
flask --app run.py init-db     # crea las tablas si no existen
flask --app run.py seed-db     # crea admin, categorías y anuncios de ejemplo
```

Para reiniciar todo desde cero:

```bash
flask --app run.py reset-db --yes
```

### 6. Ejecutar la aplicación

```bash
flask --app run.py run --debug
# o bien: python run.py
```

Abrir <http://127.0.0.1:5000>.

### Credenciales iniciales

| Usuario | Contraseña | Rol |
|---|---|---|
| `admin` | `Admin123!` | Administrador |
| `admin@tablon.edu` | `Admin123!` | Administrador (también puede ingresar con el correo) |
| `profesor` | `Profesor123!` | Usuario (rol limitado) |

> Cambiar la contraseña y el `SECRET_KEY` antes de publicar la aplicación.

## Rutas principales

| Método | Ruta | Acceso | Descripción |
|---|---|---|---|
| GET | `/` | Público | Tablón con búsqueda, filtro y paginación |
| GET/POST | `/auth/login` | Público | Inicio de sesión |
| POST | `/auth/logout` | Autenticado | Cierre de sesión |
| GET | `/anuncios/<id>` | Público | Detalle de un anuncio |
| GET | `/anuncios/` | Autenticado | Administración de anuncios |
| GET/POST | `/anuncios/nuevo` | Autenticado | Crear anuncio |
| GET/POST | `/anuncios/<id>/editar` | Autor o admin | Editar anuncio |
| POST | `/anuncios/<id>/eliminar` | Autor o admin | Eliminar anuncio |
| GET | `/categorias/` | Admin | Listado de categorías |
| GET/POST | `/categorias/nueva` | Admin | Crear categoría |
| GET/POST | `/categorias/<id>/editar` | Admin | Editar categoría |
| POST | `/categorias/<id>/eliminar` | Admin | Eliminar categoría |
| GET | `/usuarios/` | Admin | Listado de usuarios |
| GET/POST | `/usuarios/nuevo` | Admin | Crear usuario |
| GET/POST | `/usuarios/<id>/editar` | Admin | Editar usuario |
| POST | `/usuarios/<id>/eliminar` | Admin | Eliminar usuario |

## Pruebas

```bash
pip install -r requirements-dev.txt
pytest
```

La suite usa SQLite en memoria y verifica autenticación, permisos por rol, CRUD de las
tres entidades, validaciones y reglas de negocio (por ejemplo, no eliminar una categoría
con anuncios ni la propia cuenta del administrador).

## Notas de seguridad y mejoras posibles

- Agregar **CSRF Protection** con Flask-WTF en todos los formularios.
- Incorporar **Flask-Migrate** para versionar cambios del esquema.
- Guardar el `SECRET_KEY` y las credenciales únicamente en variables de entorno.
- Configurar HTTPS y cookies `Secure` en producción.
- Agregar recuperación de contraseña y verificación de correo.
