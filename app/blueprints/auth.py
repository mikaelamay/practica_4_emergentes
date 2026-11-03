"""Blueprint de autenticación: inicio y cierre de sesión."""

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy import or_

from ..extensions import db
from ..models import Usuario
from ..utils import siguiente_url_segura

bp = Blueprint("auth", __name__, url_prefix="/auth")


@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    if request.method == "POST":
        identificador = request.form.get("identificador", "").strip()
        password = request.form.get("password", "")
        recordar = bool(request.form.get("recordar"))

        usuario = Usuario.query.filter(
            or_(Usuario.username == identificador, Usuario.email == identificador)
        ).first()

        if usuario is None or not usuario.check_password(password):
            flash("Usuario/correo o contraseña incorrectos.", "danger")
        elif not usuario.activo:
            flash("Tu cuenta está deshabilitada. Contactá al administrador.", "warning")
        else:
            login_user(usuario, remember=recordar)
            flash(f"¡Bienvenido/a, {usuario.nombre}!", "success")
            destino = siguiente_url_segura(request.args.get("next"))
            return redirect(destino or url_for("main.index"))

    return render_template("auth/login.html")


@bp.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    db.session.remove()
    flash("Sesión cerrada correctamente.", "info")
    return redirect(url_for("main.index"))
