"""Configuración de la aplicación.

Los valores se pueden sobrescribir mediante variables de entorno definidas en
el archivo .env (ver .env.example).
"""

import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


class Config:
    """Configuración común para todos los entornos."""

    SECRET_KEY = os.getenv("SECRET_KEY", "cambia-esta-clave-en-produccion")

    # Por defecto se utiliza MariaDB/MySQL. Si no hay servidor disponible se
    # puede usar SQLite cambiando DATABASE_URL en el archivo .env.
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "mysql+pymysql://anuncios_user:anuncios_pass@127.0.0.1:3306/bd_anuncios"
        "?charset=utf8mb4",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True, "pool_recycle": 280}

    # Datos institucionales que se muestran en la cabecera y el pie.
    INSTITUCION = os.getenv("INSTITUCION", "Universidad Pública de El Alto")
    FACULTAD = os.getenv("FACULTAD", "Facultad de Ingeniería")
    SISTEMA = os.getenv("SISTEMA", "Tablón de Anuncios")
    DESARROLLADOR = os.getenv("DESARROLLADOR", "Mayte")

    # Paginación
    ANUNCIOS_POR_PAGINA = int(os.getenv("ANUNCIOS_POR_PAGINA", "6"))

    # Usuario administrador creado por el comando `flask seed-db`.
    ADMIN_NOMBRE = os.getenv("ADMIN_NOMBRE", "Administrador del Sistema")
    ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
    ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@tablon.edu")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "Admin123!")


class TestingConfig(Config):
    """Configuración usada por la suite de pruebas (SQLite en memoria)."""

    TESTING = True
    SECRET_KEY = "clave-solo-para-pruebas"
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_ENGINE_OPTIONS = {}
    ANUNCIOS_POR_PAGINA = 2
