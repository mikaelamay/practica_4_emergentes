"""Blueprint de administración de anuncios."""

from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user, login_required
from sqlalchemy import or_

from ..extensions import db
from ..models import Anuncio, Categoria

bp = Blueprint("anuncios", __name__, url_prefix="/anuncios")


def _obtener(id_anuncio: int) -> Anuncio:
    anuncio = db.session.get(Anuncio, id_anuncio)
    if anuncio is None:
        abort(404)
    return anuncio


def _puede_gestionar(anuncio: Anuncio) -> bool:
    return current_user.is_authenticated and (
        current_user.is_admin or anuncio.usuario_id == current_user.id
    )


def _validar(datos) -> tuple[list[str], Categoria | None]:
    errores = []
    titulo = datos.get("titulo", "").strip()
    contenido = datos.get("contenido", "").strip()

    try:
        categoria_id = int(datos.get("categoria_id", ""))
    except (TypeError, ValueError):
        categoria_id = 0

    if len(titulo) < 5 or len(titulo) > 150:
        errores.append("El título debe tener entre 5 y 150 caracteres.")
    if len(contenido) < 10:
        errores.append("El contenido debe tener al menos 10 caracteres.")

    categoria = None
    if not categoria_id:
        errores.append("Debés seleccionar una categoría.")
    else:
        categoria = db.session.get(Categoria, categoria_id)
        if categoria is None:
            errores.append("La categoría seleccionada no existe.")

    return errores, categoria


def _contexto_formulario():
    return {
        "categorias": Categoria.query.order_by(Categoria.nombre.asc()).all(),
    }


@bp.route("/")
@login_required
def listar():
    page = request.args.get("page", 1, type=int)
    busqueda = request.args.get("q", "", type=str).strip()
    categoria_id = request.args.get("categoria", type=int)

    consulta = Anuncio.query
    if busqueda:
        patron = f"%{busqueda}%"
        consulta = consulta.filter(
            or_(Anuncio.titulo.ilike(patron), Anuncio.contenido.ilike(patron))
        )
    if categoria_id:
        consulta = consulta.filter(Anuncio.categoria_id == categoria_id)

    paginacion = consulta.order_by(
        Anuncio.fecha_publicacion.desc(), Anuncio.id.desc()
    ).paginate(page=page, per_page=10, error_out=False)

    return render_template(
        "anuncios/list.html",
        paginacion=paginacion,
        anuncios=paginacion.items,
        categorias=Categoria.query.order_by(Categoria.nombre.asc()).all(),
        busqueda=busqueda,
        categoria_id=categoria_id,
    )


@bp.route("/nuevo", methods=["GET", "POST"])
@login_required
def crear():
    categorias = Categoria.query.order_by(Categoria.nombre.asc()).all()
    if not categorias:
        flash(
            "Primero debe existir al menos una categoría para poder publicar un anuncio.",
            "warning",
        )
        if current_user.is_admin:
            return redirect(url_for("categorias.crear"))
        return redirect(url_for("main.index"))

    if request.method == "POST":
        errores, categoria = _validar(request.form)
        if errores:
            for error in errores:
                flash(error, "danger")
        else:
            anuncio = Anuncio(
                titulo=request.form["titulo"].strip(),
                contenido=request.form["contenido"].strip(),
                categoria=categoria,
                usuario=current_user,
            )
            db.session.add(anuncio)
            db.session.commit()
            flash("Anuncio publicado correctamente.", "success")
            return redirect(url_for("anuncios.detalle", id_anuncio=anuncio.id))

    return render_template(
        "anuncios/form.html",
        titulo="Nuevo anuncio",
        anuncio=None,
        datos=request.form,
        **_contexto_formulario(),
    )


@bp.route("/<int:id_anuncio>")
def detalle(id_anuncio):
    anuncio = _obtener(id_anuncio)
    return render_template("anuncios/detail.html", anuncio=anuncio)


@bp.route("/<int:id_anuncio>/editar", methods=["GET", "POST"])
@login_required
def editar(id_anuncio):
    anuncio = _obtener(id_anuncio)
    if not _puede_gestionar(anuncio):
        abort(403)

    if request.method == "POST":
        errores, categoria = _validar(request.form)
        if errores:
            for error in errores:
                flash(error, "danger")
        else:
            anuncio.titulo = request.form["titulo"].strip()
            anuncio.contenido = request.form["contenido"].strip()
            anuncio.categoria = categoria
            db.session.commit()
            flash("Anuncio actualizado correctamente.", "success")
            return redirect(url_for("anuncios.detalle", id_anuncio=anuncio.id))

    return render_template(
        "anuncios/form.html",
        titulo="Editar anuncio",
        anuncio=anuncio,
        datos=request.form,
        **_contexto_formulario(),
    )


@bp.route("/<int:id_anuncio>/eliminar", methods=["POST"])
@login_required
def eliminar(id_anuncio):
    anuncio = _obtener(id_anuncio)
    if not _puede_gestionar(anuncio):
        abort(403)

    titulo = anuncio.titulo
    db.session.delete(anuncio)
    db.session.commit()
    flash(f"Anuncio «{titulo}» eliminado correctamente.", "success")
    return redirect(url_for("anuncios.listar"))
