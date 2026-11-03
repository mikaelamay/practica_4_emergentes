"""Blueprint de administración de usuarios (solo rol admin)."""

from flask import (
    Blueprint,
    abort,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user
from sqlalchemy import func, or_
from sqlalchemy.exc import IntegrityError

from ..decorators import admin_required
from ..extensions import db
from ..models import Usuario
from ..utils import email_valido, password_valida, username_valido

bp = Blueprint("usuarios", __name__, url_prefix="/usuarios")

ROLES = ("admin", "usuario")


# ----------------------------------------------------------------------
# Validación
# ----------------------------------------------------------------------
def _validar(datos, usuario=None) -> list[str]:
    """Valida el formulario y devuelve una lista de errores."""
    errores = []
    nombre = datos.get("nombre", "").strip()
    username = datos.get("username", "").strip()
    email = datos.get("email", "").strip().lower()
    rol = datos.get("rol", "usuario")
    password = datos.get("password", "")

    if len(nombre) < 3:
        errores.append("El nombre debe tener al menos 3 caracteres.")

    if not username_valido(username):
        errores.append(
            "El usuario debe tener entre 3 y 50 caracteres y solo puede contener "
            "letras, números, punto, guion o guion bajo."
        )
    else:
        existente = Usuario.query.filter(
            func.lower(Usuario.username) == username.lower()
        ).first()
        if existente and (usuario is None or existente.id != usuario.id):
            errores.append("Ese nombre de usuario ya está registrado.")

    if not email_valido(email):
        errores.append("El correo electrónico no tiene un formato válido.")
    else:
        existente = Usuario.query.filter(
            func.lower(Usuario.email) == email.lower()
        ).first()
        if existente and (usuario is None or existente.id != usuario.id):
            errores.append("Ese correo electrónico ya está registrado.")

    if rol not in ROLES:
        errores.append("El rol seleccionado no es válido.")

    if usuario is None and not password:
        errores.append("La contraseña es obligatoria para un usuario nuevo.")
    if password and not password_valida(password):
        errores.append(
            "La contraseña debe tener al menos 8 caracteres, con una letra y un número."
        )

    if usuario is not None:
        # Evitar que el administrador se bloquee a sí mismo.
        if usuario.id == current_user.id:
            if rol != "admin":
                errores.append("No podés quitarte tu propio rol de administrador.")
            if datos.get("activo") != "on":
                errores.append("No podés desactivar tu propia cuenta.")

        # Evitar quedarse sin administradores activos.
        if usuario.is_admin and (rol != "admin" or datos.get("activo") != "on"):
            otros_admins = Usuario.query.filter(
                Usuario.rol == "admin",
                Usuario.activo.is_(True),
                Usuario.id != usuario.id,
            ).count()
            if otros_admins == 0:
                errores.append("Debe existir al menos un administrador activo.")

    return errores


def _obtener(id_usuario: int) -> Usuario:
    usuario = db.session.get(Usuario, id_usuario)
    if usuario is None:
        abort(404)
    return usuario


# ----------------------------------------------------------------------
# Listado
# ----------------------------------------------------------------------
@bp.route("/")
@admin_required
def listar():
    page = request.args.get("page", 1, type=int)
    busqueda = request.args.get("q", "", type=str).strip()

    consulta = Usuario.query
    if busqueda:
        patron = f"%{busqueda}%"
        consulta = consulta.filter(
            or_(
                Usuario.nombre.ilike(patron),
                Usuario.username.ilike(patron),
                Usuario.email.ilike(patron),
            )
        )

    paginacion = consulta.order_by(Usuario.nombre.asc()).paginate(
        page=page, per_page=10, error_out=False
    )

    return render_template(
        "usuarios/list.html",
        paginacion=paginacion,
        usuarios=paginacion.items,
        busqueda=busqueda,
    )


# ----------------------------------------------------------------------
# Crear
# ----------------------------------------------------------------------
@bp.route("/nuevo", methods=["GET", "POST"])
@admin_required
def crear():
    if request.method == "POST":
        errores = _validar(request.form)
        if errores:
            for error in errores:
                flash(error, "danger")
            return render_template(
                "usuarios/form.html",
                titulo="Nuevo usuario",
                usuario=None,
                datos=request.form,
                roles=ROLES,
            )

        usuario = Usuario(
            nombre=request.form["nombre"].strip(),
            username=request.form["username"].strip(),
            email=request.form["email"].strip().lower(),
            rol=request.form["rol"],
            activo=request.form.get("activo") == "on",
        )
        usuario.set_password(request.form["password"])
        db.session.add(usuario)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash("No se pudo guardar: revisá los datos únicos.", "danger")
        else:
            flash(f"Usuario «{usuario.nombre}» creado correctamente.", "success")
            return redirect(url_for("usuarios.listar"))

    return render_template(
        "usuarios/form.html",
        titulo="Nuevo usuario",
        usuario=None,
        datos=request.form,
        roles=ROLES,
    )


# ----------------------------------------------------------------------
# Editar
# ----------------------------------------------------------------------
@bp.route("/<int:id_usuario>/editar", methods=["GET", "POST"])
@admin_required
def editar(id_usuario):
    usuario = _obtener(id_usuario)

    if request.method == "POST":
        errores = _validar(request.form, usuario=usuario)
        if errores:
            for error in errores:
                flash(error, "danger")
            return render_template(
                "usuarios/form.html",
                titulo="Editar usuario",
                usuario=usuario,
                datos=request.form,
                roles=ROLES,
            )

        usuario.nombre = request.form["nombre"].strip()
        usuario.username = request.form["username"].strip()
        usuario.email = request.form["email"].strip().lower()
        usuario.rol = request.form["rol"]
        usuario.activo = request.form.get("activo") == "on"
        if request.form.get("password"):
            usuario.set_password(request.form["password"])

        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash("No se pudo guardar: revisá los datos únicos.", "danger")
        else:
            flash(f"Usuario «{usuario.nombre}» actualizado correctamente.", "success")
            return redirect(url_for("usuarios.listar"))

    return render_template(
        "usuarios/form.html",
        titulo="Editar usuario",
        usuario=usuario,
        datos=request.form,
        roles=ROLES,
    )


# ----------------------------------------------------------------------
# Eliminar
# ----------------------------------------------------------------------
@bp.route("/<int:id_usuario>/eliminar", methods=["POST"])
@admin_required
def eliminar(id_usuario):
    usuario = _obtener(id_usuario)

    if usuario.id == current_user.id:
        flash("No podés eliminar tu propia cuenta.", "danger")
        return redirect(url_for("usuarios.listar"))

    if usuario.is_admin:
        otros_admins = Usuario.query.filter(
            Usuario.rol == "admin",
            Usuario.activo.is_(True),
            Usuario.id != usuario.id,
        ).count()
        if otros_admins == 0:
            flash("No se puede eliminar al único administrador activo.", "danger")
            return redirect(url_for("usuarios.listar"))

    nombre = usuario.nombre
    total = usuario.total_anuncios
    db.session.delete(usuario)
    db.session.commit()
    flash(
        f"Usuario «{nombre}» eliminado. También se eliminaron {total} anuncio(s).",
        "success",
    )
    return redirect(url_for("usuarios.listar"))
