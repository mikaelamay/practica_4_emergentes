"""Fábrica de la aplicación (Application Factory)."""

from datetime import datetime

from flask import Flask, render_template
from flask_login import current_user

from config import Config
from .extensions import db, login_manager


def create_app(config_class=Config):
    """Crea y configura una instancia de la aplicación Flask.

    :param config_class: clase de configuración (por defecto ``Config``).
    """

    app = Flask(__name__)
    app.config.from_object(config_class)

    # ------------------------------------------------------------------
    # Extensiones
    # ------------------------------------------------------------------
    db.init_app(app)
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        from .models import Usuario

        try:
            return db.session.get(Usuario, int(user_id))
        except (TypeError, ValueError):
            return None

    # ------------------------------------------------------------------
    # Blueprints
    # ------------------------------------------------------------------
    from .blueprints.anuncios import bp as anuncios_bp
    from .blueprints.auth import bp as auth_bp
    from .blueprints.categorias import bp as categorias_bp
    from .blueprints.main import bp as main_bp
    from .blueprints.usuarios import bp as usuarios_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(usuarios_bp)
    app.register_blueprint(categorias_bp)
    app.register_blueprint(anuncios_bp)

    # ------------------------------------------------------------------
    # Comandos CLI
    # ------------------------------------------------------------------
    from .cli import register_commands

    register_commands(app)

    # ------------------------------------------------------------------
    # Filtros y variables disponibles en las plantillas
    # ------------------------------------------------------------------
    @app.template_filter("fecha")
    def fecha_filter(value, formato="%d/%m/%Y %H:%M"):
        return value.strftime(formato) if value else ""

    @app.context_processor
    def inject_globals():
        return {
            "institucion": app.config["INSTITUCION"],
            "facultad": app.config["FACULTAD"],
            "sistema": app.config["SISTEMA"],
            "desarrollador": app.config["DESARROLLADOR"],
            "anio_actual": datetime.now().year,
        }

    # ------------------------------------------------------------------
    # Manejadores de errores
    # ------------------------------------------------------------------
    @app.errorhandler(403)
    def forbidden(error):
        return render_template("errors/403.html"), 403

    @app.errorhandler(404)
    def not_found(error):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template("errors/500.html"), 500

    # Expone current_user en todas las plantillas (Flask-Login ya lo hace,
    # pero se deja explícito para mayor claridad).
    @app.context_processor
    def inject_user():
        return {"current_user": current_user}

    return app
