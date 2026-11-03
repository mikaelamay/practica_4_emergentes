"""Blueprint de administración de categorías (solo rol admin)."""

from flask import (
    Blueprint,
    abort,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from sqlalchemy import func, or_
from sqlalchemy.exc import IntegrityError

from ..decorators import admin_required
from ..extensions import db
from ..models import Categoria

bp = Blueprint("categorias", __name__, url_prefix="/categorias")


def _validar(datos, categoria=None) -> list[str]:
    errores = []
    nombre = datos.get("nombre", "").strip()
    descripcion = datos.get("descripcion", "").strip()

    if len(nombre) < 3 or len(nombre) > 80:
        errores.append("El nombre debe tener entre 3 y 80 caracteres.")

    if len(descripcion) > 255:
        errores.append("La descripción no puede superar los 255 caracteres.")

    if nombre:
        existente = Categoria.query.filter(
            func.lower(Categoria.nombre) == nombre.lower()
        ).first()
        if existente and (categoria is None or existente.id != categoria.id):
            errores.append("Ya existe una categoría con ese nombre.")

    return errores


def _obtener(id_categoria: int) -> Categoria:
    categoria = db.session.get(Categoria, id_categoria)
    if categoria is None:
        abort(404)
    return categoria


@bp.route("/")
@admin_required
def listar():
    page = request.args.get("page", 1, type=int)
    busqueda = request.args.get("q", "", type=str).strip()

    consulta = Categoria.query
    if busqueda:
        patron = f"%{busqueda}%"
        consulta = consulta.filter(
            or_(
                Categoria.nombre.ilike(patron),
                Categoria.descripcion.ilike(patron),
            )
        )

    paginacion = consulta.order_by(Categoria.nombre.asc()).paginate(
        page=page, per_page=10, error_out=False
    )

    return render_template(
        "categorias/list.html",
        paginacion=paginacion,
        categorias=paginacion.items,
        busqueda=busqueda,
    )


@bp.route("/nueva", methods=["GET", "POST"])
@admin_required
def crear():
    if request.method == "POST":
        errores = _validar(request.form)
        if errores:
            for error in errores:
                flash(error, "danger")
        else:
            categoria = Categoria(
                nombre=request.form["nombre"].strip(),
                descripcion=request.form.get("descripcion", "").strip() or None,
            )
            db.session.add(categoria)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                flash("Ya existe una categoría con ese nombre.", "danger")
            else:
                flash(f"Categoría «{categoria.nombre}» creada correctamente.", "success")
                return redirect(url_for("categorias.listar"))

    return render_template(
        "categorias/form.html",
        titulo="Nueva categoría",
        categoria=None,
        datos=request.form,
    )


@bp.route("/<int:id_categoria>/editar", methods=["GET", "POST"])
@admin_required
def editar(id_categoria):
    categoria = _obtener(id_categoria)

    if request.method == "POST":
        errores = _validar(request.form, categoria=categoria)
        if errores:
            for error in errores:
                flash(error, "danger")
        else:
            categoria.nombre = request.form["nombre"].strip()
            categoria.descripcion = request.form.get("descripcion", "").strip() or None
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                flash("Ya existe una categoría con ese nombre.", "danger")
            else:
                flash(
                    f"Categoría «{categoria.nombre}» actualizada correctamente.",
                    "success",
                )
                return redirect(url_for("categorias.listar"))

    return render_template(
        "categorias/form.html",
        titulo="Editar categoría",
        categoria=categoria,
        datos=request.form,
    )


@bp.route("/<int:id_categoria>/eliminar", methods=["POST"])
@admin_required
def eliminar(id_categoria):
    categoria = _obtener(id_categoria)

    if categoria.total_anuncios > 0:
        flash(
            f"No se puede eliminar «{categoria.nombre}» porque tiene "
            f"{categoria.total_anuncios} anuncio(s) asociado(s). "
            "Reasigná o eliminá esos anuncios primero.",
            "danger",
        )
        return redirect(url_for("categorias.listar"))

    nombre = categoria.nombre
    db.session.delete(categoria)
    db.session.commit()
    flash(f"Categoría «{nombre}» eliminada correctamente.", "success")
    return redirect(url_for("categorias.listar"))
