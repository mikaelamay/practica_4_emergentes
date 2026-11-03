"""Modelos de la base de datos bd_anuncios.

Tablas:
    usuarios   -> personas que publican y administran el tablón.
    categorias -> clasificación de los anuncios.
    anuncios   -> publicaciones del tablón.

Relaciones:
    usuarios 1 --- N anuncios
    categorias 1 --- N anuncios
"""

from datetime import datetime, timezone

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from .extensions import db


def utcnow() -> datetime:
    """Fecha/hora actual en UTC (sin información de zona)."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


class Usuario(UserMixin, db.Model):
    __tablename__ = "usuarios"

    id = db.Column("id_usuario", db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(120), nullable=False)
    username = db.Column(db.String(50), nullable=False, unique=True, index=True)
    email = db.Column(db.String(150), nullable=False, unique=True, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    rol = db.Column(db.String(20), nullable=False, default="usuario")
    activo = db.Column(db.Boolean, nullable=False, default=True)
    creado_en = db.Column(db.DateTime, nullable=False, default=utcnow)

    anuncios = db.relationship(
        "Anuncio",
        back_populates="usuario",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )

    # ------------------------------------------------------------------
    # Contraseñas
    # ------------------------------------------------------------------
    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    # ------------------------------------------------------------------
    # Utilidades
    # ------------------------------------------------------------------
    @property
    def is_admin(self) -> bool:
        return self.rol == "admin"

    @property
    def total_anuncios(self) -> int:
        return self.anuncios.count()

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Usuario {self.username}>"


class Categoria(db.Model):
    __tablename__ = "categorias"

    id = db.Column("id_categoria", db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(80), nullable=False, unique=True, index=True)
    descripcion = db.Column(db.String(255), nullable=True)
    creado_en = db.Column(db.DateTime, nullable=False, default=utcnow)

    anuncios = db.relationship(
        "Anuncio",
        back_populates="categoria",
        lazy="dynamic",
    )

    @property
    def total_anuncios(self) -> int:
        return self.anuncios.count()

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Categoria {self.nombre}>"


class Anuncio(db.Model):
    __tablename__ = "anuncios"

    id = db.Column("id_anuncio", db.Integer, primary_key=True, autoincrement=True)
    titulo = db.Column(db.String(150), nullable=False, index=True)
    contenido = db.Column(db.Text, nullable=False)
    fecha_publicacion = db.Column(db.DateTime, nullable=False, default=utcnow)
    actualizado_en = db.Column(db.DateTime, nullable=False, default=utcnow, onupdate=utcnow)

    usuario_id = db.Column(
        "id_usuario",
        db.Integer,
        db.ForeignKey("usuarios.id_usuario", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    categoria_id = db.Column(
        "id_categoria",
        db.Integer,
        db.ForeignKey("categorias.id_categoria", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    usuario = db.relationship("Usuario", back_populates="anuncios")
    categoria = db.relationship("Categoria", back_populates="anuncios")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Anuncio {self.titulo}>"
