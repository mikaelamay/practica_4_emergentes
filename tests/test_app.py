"""Pruebas funcionales de la aplicación."""

from app.extensions import db
from app.models import Anuncio, Categoria, Usuario


# ----------------------------------------------------------------------
# Páginas públicas y autenticación
# ----------------------------------------------------------------------
def test_pagina_principal_publica(client):
    respuesta = client.get("/")
    assert respuesta.status_code == 200
    assert b"Tabl" in respuesta.data


def test_archivos_estaticos_disponibles(client):
    respuesta = client.get("/static/vendor/bootstrap/bootstrap.min.css")
    assert respuesta.status_code == 200
    assert len(respuesta.data) > 1000


def test_login_fallido(client):
    respuesta = client.post(
        "/auth/login",
        data={"identificador": "admin", "password": "incorrecta"},
        follow_redirects=True,
    )
    assert b"incorrectos" in respuesta.data


def test_login_exitoso_y_logout(client, auth):
    respuesta = auth.login()
    assert b"Bienvenido/a" in respuesta.data
    assert respuesta.request.path == "/"

    respuesta = auth.logout()
    assert b"Sesi" in respuesta.data


def test_acceso_anonimo_redirige_al_login(client):
    respuesta = client.get("/usuarios/")
    assert respuesta.status_code == 302
    assert "/auth/login" in respuesta.headers["Location"]


def test_usuario_normal_no_puede_administrar_usuarios(client, auth):
    auth.login("alumno", "Alumno123!")
    respuesta = client.get("/usuarios/")
    assert respuesta.status_code == 403


# ----------------------------------------------------------------------
# CRUD de categorías
# ----------------------------------------------------------------------
def test_crear_categoria(app, client, auth):
    auth.login()
    respuesta = client.post(
        "/categorias/nueva",
        data={"nombre": "Eventos", "descripcion": "Charlas y talleres"},
        follow_redirects=True,
    )
    assert "creada correctamente" in respuesta.get_data(as_text=True)

    with app.app_context():
        assert Categoria.query.filter_by(nombre="Eventos").count() == 1


def test_nombre_categoria_duplicado(app, client, auth):
    auth.login()
    respuesta = client.post(
        "/categorias/nueva",
        data={"nombre": "general", "descripcion": "Duplicada"},
        follow_redirects=True,
    )
    assert "Ya existe una categoría" in respuesta.get_data(as_text=True)


def test_no_eliminar_categoria_con_anuncios(app, client, auth):
    with app.app_context():
        admin = Usuario.query.filter_by(username="admin").first()
        categoria = Categoria.query.first()
        db.session.add(
            Anuncio(
                titulo="Anuncio de prueba",
                contenido="Contenido suficientemente largo.",
                usuario=admin,
                categoria=categoria,
            )
        )
        db.session.commit()
        categoria_id = categoria.id

    auth.login()
    respuesta = client.post(
        f"/categorias/{categoria_id}/eliminar", follow_redirects=True
    )
    assert "No se puede eliminar" in respuesta.get_data(as_text=True)

    with app.app_context():
        assert db.session.get(Categoria, categoria_id) is not None


# ----------------------------------------------------------------------
# CRUD de anuncios
# ----------------------------------------------------------------------
def _crear_anuncio(client, categoria_id):
    return client.post(
        "/anuncios/nuevo",
        data={
            "titulo": "Nuevo anuncio de prueba",
            "contenido": "Este es el contenido completo del anuncio de prueba.",
            "categoria_id": categoria_id,
        },
        follow_redirects=True,
    )


def test_crear_anuncio(app, client, auth):
    with app.app_context():
        categoria_id = Categoria.query.first().id

    auth.login()
    respuesta = _crear_anuncio(client, categoria_id)
    assert "publicado correctamente" in respuesta.get_data(as_text=True)

    with app.app_context():
        anuncio = Anuncio.query.filter_by(titulo="Nuevo anuncio de prueba").first()
        assert anuncio is not None
        assert anuncio.usuario.username == "admin"
        assert anuncio.categoria.nombre == "General"


def test_validacion_anuncio_sin_categoria(client, auth):
    auth.login()
    respuesta = client.post(
        "/anuncios/nuevo",
        data={"titulo": "Título válido", "contenido": "Contenido válido largo."},
        follow_redirects=True,
    )
    assert "seleccionar una categor" in respuesta.get_data(as_text=True)


def test_autor_puede_editar_su_anuncio(app, client, auth):
    with app.app_context():
        categoria_id = Categoria.query.first().id

    auth.login()
    _crear_anuncio(client, categoria_id)

    with app.app_context():
        anuncio_id = Anuncio.query.first().id

    respuesta = client.get(f"/anuncios/{anuncio_id}/editar")
    assert respuesta.status_code == 200


def test_otro_usuario_no_puede_editar_anuncio_ajeno(app, client, auth):
    with app.app_context():
        categoria_id = Categoria.query.first().id

    auth.login()
    _crear_anuncio(client, categoria_id)

    with app.app_context():
        anuncio_id = Anuncio.query.first().id

    auth.logout()
    auth.login("alumno", "Alumno123!")
    respuesta = client.get(f"/anuncios/{anuncio_id}/editar")
    assert respuesta.status_code == 403


def test_eliminar_anuncio(app, client, auth):
    with app.app_context():
        categoria_id = Categoria.query.first().id

    auth.login()
    _crear_anuncio(client, categoria_id)

    with app.app_context():
        anuncio_id = Anuncio.query.first().id

    respuesta = client.post(f"/anuncios/{anuncio_id}/eliminar", follow_redirects=True)
    assert "eliminado correctamente" in respuesta.get_data(as_text=True)

    with app.app_context():
        assert db.session.get(Anuncio, anuncio_id) is None


# ----------------------------------------------------------------------
# CRUD de usuarios
# ----------------------------------------------------------------------
def test_crear_usuario(app, client, auth):
    auth.login()
    respuesta = client.post(
        "/usuarios/nuevo",
        data={
            "nombre": "Nuevo Usuario",
            "username": "nuevo",
            "email": "nuevo@example.com",
            "password": "Clave123!",
            "rol": "usuario",
            "activo": "on",
        },
        follow_redirects=True,
    )
    assert "creado correctamente" in respuesta.get_data(as_text=True)

    with app.app_context():
        usuario = Usuario.query.filter_by(username="nuevo").first()
        assert usuario is not None
        assert usuario.check_password("Clave123!")


def test_no_eliminar_propia_cuenta(app, client, auth):
    auth.login()
    with app.app_context():
        admin_id = Usuario.query.filter_by(username="admin").first().id

    respuesta = client.post(f"/usuarios/{admin_id}/eliminar", follow_redirects=True)
    assert "No podés eliminar tu propia cuenta" in respuesta.get_data(as_text=True)

    with app.app_context():
        assert db.session.get(Usuario, admin_id) is not None


def test_error_404(client):
    respuesta = client.get("/anuncios/9999")
    assert respuesta.status_code == 404


def test_paginacion_principal(app, client):
    with app.app_context():
        admin = Usuario.query.filter_by(username="admin").first()
        categoria = Categoria.query.first()
        for numero in range(1, 4):
            db.session.add(
                Anuncio(
                    titulo=f"Anuncio paginado {numero}",
                    contenido="Contenido de prueba para la paginación.",
                    usuario=admin,
                    categoria=categoria,
                )
            )
        db.session.commit()

    respuesta = client.get("/")
    assert respuesta.status_code == 200
    assert "?page=2" in respuesta.get_data(as_text=True)

    respuesta = client.get("/?page=2")
    assert respuesta.status_code == 200
    assert b"Anuncio paginado" in respuesta.data
