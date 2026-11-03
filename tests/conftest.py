"""Fixtures compartidas por la suite de pruebas."""

import pytest

from app import create_app
from app.extensions import db
from app.models import Categoria, Usuario
from config import TestingConfig


@pytest.fixture
def app():
    app = create_app(TestingConfig)

    with app.app_context():
        db.create_all()

        admin = Usuario(
            nombre="Administrador de Prueba",
            username="admin",
            email="admin@example.com",
            rol="admin",
            activo=True,
        )
        admin.set_password("Admin123!")

        alumno = Usuario(
            nombre="Alumno de Prueba",
            username="alumno",
            email="alumno@example.com",
            rol="usuario",
            activo=True,
        )
        alumno.set_password("Alumno123!")

        categoria = Categoria(nombre="General", descripcion="Categoría de prueba")

        db.session.add_all([admin, alumno, categoria])
        db.session.commit()

        yield app

        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def auth(client):
    class AuthActions:
        def login(self, identificador="admin", password="Admin123!"):
            return client.post(
                "/auth/login",
                data={"identificador": identificador, "password": password},
                follow_redirects=True,
            )

        def logout(self):
            return client.post("/auth/logout", follow_redirects=True)

    return AuthActions()
