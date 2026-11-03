"""Funciones auxiliares de validación y seguridad."""

import re
from urllib.parse import urlsplit

from email_validator import EmailNotValidError, validate_email

USERNAME_RE = re.compile(r"^[A-Za-z0-9_.-]{3,50}$")


def email_valido(email: str) -> bool:
    """Devuelve True si el correo tiene un formato válido."""
    try:
        validate_email(email, check_deliverability=False)
        return True
    except EmailNotValidError:
        return False


def username_valido(username: str) -> bool:
    """Solo letras, números, punto, guion y guion bajo (3 a 50 caracteres)."""
    return bool(USERNAME_RE.match(username or ""))


def password_valida(password: str) -> bool:
    """Mínimo 8 caracteres, al menos una letra y un número."""
    if not password or len(password) < 8:
        return False
    return bool(re.search(r"[A-Za-z]", password) and re.search(r"\d", password))


def siguiente_url_segura(valor: str | None) -> str | None:
    """Evita redirecciones abiertas: solo acepta rutas internas."""
    if not valor:
        return None
    partes = urlsplit(valor)
    if partes.scheme or partes.netloc or not valor.startswith("/"):
        return None
    return valor
