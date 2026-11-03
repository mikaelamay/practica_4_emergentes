"""Extensiones de Flask instanciadas sin asociarlas todavía a una app.

Se inicializan dentro de create_app() siguiendo el patrón Application Factory.
"""

from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
login_manager = LoginManager()

login_manager.login_view = "auth.login"
login_manager.login_message = "Debes iniciar sesión para acceder a esta sección."
login_manager.login_message_category = "warning"
