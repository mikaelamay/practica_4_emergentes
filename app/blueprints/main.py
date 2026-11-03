"""Blueprint principal: tablón público de anuncios."""

from flask import Blueprint, current_app, request, render_template
from sqlalchemy import or_

from ..extensions import db
from ..models import Anuncio, Categoria

bp = Blueprint("main", __name__)


@bp.route("/")
def index():
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

    consulta = consulta.order_by(
        Anuncio.fecha_publicacion.desc(), Anuncio.id.desc()
    )

    paginacion = consulta.paginate(
        page=page,
        per_page=current_app.config["ANUNCIOS_POR_PAGINA"],
        error_out=False,
    )

    categorias = Categoria.query.order_by(Categoria.nombre.asc()).all()

    return render_template(
        "main/index.html",
        paginacion=paginacion,
        anuncios=paginacion.items,
        categorias=categorias,
        busqueda=busqueda,
        categoria_id=categoria_id,
        total_anuncios=db.session.query(Anuncio.id).count(),
        total_categorias=db.session.query(Categoria.id).count(),
    )
