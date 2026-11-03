"""Genera las capturas de pantalla del informe con Playwright.

Requisitos:
    pip install playwright
    # El script usa el Chromium del sistema (/usr/bin/chromium).
    # También se puede apuntar a otro binario con CHROMIUM_PATH.

Uso:
    flask --app run.py run --host 127.0.0.1 --port 5000
    python docs/generar_capturas.py
"""

import os
from pathlib import Path

from playwright.sync_api import sync_playwright

BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:5000")
CHROMIUM_PATH = os.getenv("CHROMIUM_PATH", "/usr/bin/chromium")
SALIDA = Path(__file__).resolve().parent / "capturas"

ADMIN = ("admin", "Admin123!")
PROFESOR = ("profesor", "Profesor123!")


def capturar(page, nombre: str) -> None:
    page.wait_for_timeout(300)
    page.screenshot(path=str(SALIDA / nombre), full_page=True)
    print(f"  ✔ {nombre}")


def iniciar_sesion(page, credenciales) -> None:
    page.goto(f"{BASE_URL}/auth/login", wait_until="networkidle")
    page.fill("#identificador", credenciales[0])
    page.fill("#password", credenciales[1])
    page.locator("main form button[type=submit]").click()
    page.wait_for_load_state("networkidle")


def main() -> None:
    SALIDA.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        navegador = p.chromium.launch(
            executable_path=CHROMIUM_PATH,
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage"],
        )

        # ------------------------------------------------------------------
        # Sesión pública
        # ------------------------------------------------------------------
        contexto = navegador.new_context(
            viewport={"width": 1440, "height": 1000},
            locale="es-ES",
        )
        page = contexto.new_page()

        print("Capturas públicas:")
        page.goto(BASE_URL, wait_until="networkidle")
        capturar(page, "01-pagina-principal.png")

        page.goto(f"{BASE_URL}/auth/login", wait_until="networkidle")
        capturar(page, "02-login.png")

        # ------------------------------------------------------------------
        # Sesión como administrador
        # ------------------------------------------------------------------
        print("Capturas del administrador:")
        iniciar_sesion(page, ADMIN)
        capturar(page, "03-tablon-admin.png")

        page.goto(f"{BASE_URL}/usuarios/", wait_until="networkidle")
        capturar(page, "04-usuarios-listado.png")

        page.goto(f"{BASE_URL}/usuarios/nuevo", wait_until="networkidle")
        capturar(page, "05-usuario-formulario.png")

        page.goto(f"{BASE_URL}/categorias/", wait_until="networkidle")
        capturar(page, "06-categorias-listado.png")

        page.goto(f"{BASE_URL}/categorias/nueva", wait_until="networkidle")
        capturar(page, "07-categoria-formulario.png")

        page.goto(f"{BASE_URL}/anuncios/", wait_until="networkidle")
        capturar(page, "08-anuncios-listado.png")

        page.goto(f"{BASE_URL}/anuncios/nuevo", wait_until="networkidle")
        capturar(page, "09-anuncio-formulario.png")

        page.goto(f"{BASE_URL}/anuncios/", wait_until="networkidle")
        enlace_detalle = page.locator(
            'table tbody tr a[href*="/anuncios/"]'
        ).first.get_attribute("href")
        page.goto(f"{BASE_URL}{enlace_detalle}", wait_until="networkidle")
        capturar(page, "10-anuncio-detalle.png")

        # Validación: nombre de categoría duplicado.
        page.goto(f"{BASE_URL}/categorias/nueva", wait_until="networkidle")
        page.fill("#nombre", "Académico")
        page.locator("main form button[type=submit]").click()
        page.wait_for_load_state("networkidle")
        capturar(page, "11-validacion.png")
        contexto.close()

        # ------------------------------------------------------------------
        # Control de acceso: usuario con rol limitado
        # ------------------------------------------------------------------
        print("Captura de acceso denegado:")
        contexto_profesor = navegador.new_context(
            viewport={"width": 1440, "height": 1000},
            locale="es-ES",
        )
        page_profesor = contexto_profesor.new_page()
        iniciar_sesion(page_profesor, PROFESOR)
        page_profesor.goto(f"{BASE_URL}/usuarios/", wait_until="networkidle")
        capturar(page_profesor, "12-acceso-denegado.png")
        contexto_profesor.close()

        navegador.close()

    print(f"\nCapturas guardadas en: {SALIDA}")


if __name__ == "__main__":
    main()
