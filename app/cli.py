"""Comandos personalizados de Flask CLI.

Uso:
    flask --app run.py init-db
    flask --app run.py seed-db
    flask --app run.py reset-db --yes
"""

from datetime import timedelta

import click
from flask import current_app

from .extensions import db
from .models import Anuncio, Categoria, Usuario, utcnow


def _crear_admin() -> Usuario:
    """Crea el usuario administrador si todavía no existe."""
    admin = Usuario.query.filter_by(username=current_app.config["ADMIN_USERNAME"]).first()
    if admin is None:
        admin = Usuario(
            nombre=current_app.config["ADMIN_NOMBRE"],
            username=current_app.config["ADMIN_USERNAME"],
            email=current_app.config["ADMIN_EMAIL"],
            rol="admin",
            activo=True,
        )
        admin.set_password(current_app.config["ADMIN_PASSWORD"])
        db.session.add(admin)
        db.session.flush()
    return admin


def _crear_datos_demo(admin: Usuario) -> None:
    """Crea categorías y anuncios de ejemplo de forma idempotente."""
    # Usuario con rol "usuario" para demostrar el control de permisos.
    profesor = Usuario.query.filter_by(username="profesor").first()
    if profesor is None:
        profesor = Usuario(
            nombre="Profesor Demo",
            username="profesor",
            email="profesor@tablon.edu",
            rol="usuario",
            activo=True,
        )
        profesor.set_password("Profesor123!")
        db.session.add(profesor)
        db.session.flush()

    datos = {
        "Académico": "Noticias sobre clases, exámenes y trámites académicos.",
        "Eventos": "Charlas, talleres, congresos y actividades institucionales.",
        "Becas": "Convocatorias de becas y ayudas económicas.",
        "Deportes": "Torneos y actividades deportivas.",
    }

    categorias = {}
    for nombre, descripcion in datos.items():
        categoria = Categoria.query.filter_by(nombre=nombre).first()
        if categoria is None:
            categoria = Categoria(nombre=nombre, descripcion=descripcion)
            db.session.add(categoria)
            db.session.flush()
        categorias[nombre] = categoria

    if Anuncio.query.count() == 0:
        ahora = utcnow()
        ejemplos = [
            (
                "Inscripción a exámenes finales",
                "Se informa a los estudiantes que la inscripción a exámenes "
                "finales estará habilitada hasta el viernes 20 de noviembre. "
                "El trámite se realiza únicamente por el portal académico.",
                "Académico",
                ahora - timedelta(days=1),
            ),
            (
                "Charla: Introducción a Flask",
                "El Centro de Estudiantes invita a la charla sobre desarrollo "
                "web con Python y Flask. La actividad es gratuita y se realizará "
                "en el Aula Magna a las 18:00 hs.",
                "Eventos",
                ahora - timedelta(days=3),
            ),
            (
                "Convocatoria de becas 2026",
                "Ya se encuentra abierta la convocatoria de becas de ayuda "
                "económica para el ciclo 2026. Consultá los requisitos en la "
                "Secretaría de Bienestar Estudiantil.",
                "Becas",
                ahora - timedelta(days=6),
            ),
        ]

        for titulo, contenido, categoria, fecha in ejemplos:
            db.session.add(
                Anuncio(
                    titulo=titulo,
                    contenido=contenido,
                    categoria=categorias[categoria],
                    usuario=admin,
                    fecha_publicacion=fecha,
                )
            )

    # Un anuncio publicado por el usuario de rol "usuario".
    if not Anuncio.query.filter_by(titulo="Taller de Git y GitHub").first():
        db.session.add(
            Anuncio(
                titulo="Taller de Git y GitHub",
                contenido="Se invita a los estudiantes al taller práctico de control "
                "de versiones con Git y publicación de proyectos en GitHub. "
                "Cupos limitados; inscripción en la secretaría.",
                categoria=categorias["Eventos"],
                usuario=profesor,
                fecha_publicacion=utcnow() - timedelta(days=2),
            )
        )


def register_commands(app):
    @app.cli.command("init-db")
    def init_db():
        """Crea las tablas de la base de datos."""
        db.create_all()
        click.echo("✔ Tablas creadas correctamente.")

    @app.cli.command("seed-db")
    def seed_db():
        """Crea el usuario administrador y datos de ejemplo."""
        db.create_all()
        admin = _crear_admin()
        _crear_datos_demo(admin)
        db.session.commit()
        click.echo("✔ Datos iniciales cargados.")
        click.echo(
            f"  Usuario: {current_app.config['ADMIN_USERNAME']}  "
            f"Contraseña: {current_app.config['ADMIN_PASSWORD']}"
        )

    @app.cli.command("reset-db")
    @click.option("--yes", is_flag=True, help="Confirma la eliminación de todos los datos.")
    def reset_db(yes):
        """Elimina todas las tablas y vuelve a crear los datos iniciales."""
        if not yes:
            raise click.ClickException(
                "Esta operación borra todos los datos. Usá --yes para confirmar."
            )
        db.drop_all()
        db.create_all()
        admin = _crear_admin()
        _crear_datos_demo(admin)
        db.session.commit()
        click.echo("✔ Base de datos reiniciada con datos de ejemplo.")
