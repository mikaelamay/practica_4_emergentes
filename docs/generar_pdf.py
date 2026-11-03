"""Genera el borrador del informe en PDF a partir de documento_practica.md.

Herramientas necesarias:
    pip install markdown playwright
    # Chromium del sistema (/usr/bin/chromium) o indicar CHROMIUM_PATH.

Uso:
    python docs/generar_pdf.py
"""

import html
import os
import re
from pathlib import Path

import markdown
from playwright.sync_api import sync_playwright

DOCS = Path(__file__).resolve().parent
MARKDOWN = DOCS / "documento_practica.md"
SALIDA_PDF = DOCS / "informe_practica4.pdf"
DIAGRAMA = DOCS / "capturas" / "00-modelo-er.png"
MERMAID_JS = DOCS / "vendor" / "mermaid.min.js"
CHROMIUM_PATH = os.getenv("CHROMIUM_PATH", "/usr/bin/chromium")

CSS = """
@page { size: A4; }
* { box-sizing: border-box; }
body {
  font-family: "DejaVu Sans", Arial, sans-serif;
  font-size: 10.5pt;
  line-height: 1.55;
  color: #1f2933;
  margin: 0;
}
.cover {
  min-height: 245mm;
  display: flex;
  flex-direction: column;
  justify-content: center;
  text-align: center;
  page-break-after: always;
  border-top: 10px solid #0b3d6b;
  padding: 30mm 15mm;
}
.cover .univ { font-size: 16pt; font-weight: bold; color: #0b3d6b; }
.cover .fac { font-size: 12pt; color: #52606d; margin-bottom: 28mm; }
.cover h1 { font-size: 27pt; color: #0b3d6b; border: 0; margin: 0 0 8mm; line-height: 1.2; }
.cover .practica { font-size: 14pt; color: #a67c00; font-weight: bold; margin-bottom: 28mm; }
.cover .datos { margin: 0 auto; font-size: 11pt; text-align: left; }
.cover .datos td { border: 0; padding: 2mm 4mm; background: transparent; }
.cover .datos td:first-child { font-weight: bold; color: #0b3d6b; }
h1 {
  font-size: 22pt;
  color: #0b3d6b;
  border-bottom: 3px solid #f2b705;
  padding-bottom: 3mm;
  margin: 0 0 6mm;
}
h2 {
  font-size: 15pt;
  color: #0b3d6b;
  border-bottom: 1px solid #c9d6e3;
  padding-bottom: 1.5mm;
  margin-top: 8mm;
  page-break-after: avoid;
}
h3 { font-size: 12pt; color: #12558f; margin-top: 6mm; page-break-after: avoid; }
p { margin: 0 0 3mm; text-align: justify; }
ul, ol { margin: 0 0 3mm 6mm; }
li { margin-bottom: 1mm; }
table {
  width: 100%;
  border-collapse: collapse;
  margin: 3mm 0 6mm;
  font-size: 8.8pt;
  page-break-inside: avoid;
}
th, td { border: 1px solid #c9d6e3; padding: 2mm 2.5mm; vertical-align: top; }
th { background: #eef3f8; color: #0b3d6b; text-align: left; }
code {
  background: #eef3f8;
  color: #0b3d6b;
  padding: 0.3mm 1.2mm;
  border-radius: 2px;
  font-family: "DejaVu Sans Mono", monospace;
  font-size: 8.8pt;
}
pre {
  background: #f8fafc;
  border-left: 3px solid #0b3d6b;
  padding: 3mm 4mm;
  overflow-wrap: break-word;
  white-space: pre-wrap;
  page-break-inside: avoid;
}
pre code { background: transparent; padding: 0; }
blockquote {
  margin: 4mm 0;
  padding: 3mm 5mm;
  background: #fff9e6;
  border-left: 4px solid #f2b705;
  color: #52606d;
}
img {
  max-width: 100%;
  border: 1px solid #d7dee8;
  border-radius: 2mm;
  margin: 2mm 0 4mm;
  page-break-inside: avoid;
}
hr { border: 0; border-top: 1px solid #d7dee8; margin: 6mm 0; }
a { color: #12558f; text-decoration: none; }
"""

PORTADA = """
<section class="cover">
  <div class="univ">Universidad Nacional</div>
  <div class="fac">Facultad de Ingeniería</div>
  <h1>Aplicación web:<br>Tablón de Anuncios con Flask</h1>
  <div class="practica">Práctica N° 4</div>
  <table class="datos">
    <tr><td>Carrera:</td><td>[Completar]</td></tr>
    <tr><td>Asignatura:</td><td>[Completar]</td></tr>
    <tr><td>Estudiante:</td><td>[Completar]</td></tr>
    <tr><td>Docente:</td><td>[Completar]</td></tr>
    <tr><td>Fecha:</td><td>Noviembre de 2026</td></tr>
  </table>
</section>
"""


def generar_diagrama(navegador) -> None:
    """Renderiza el bloque Mermaid como imagen PNG."""
    if not MERMAID_JS.exists():
        print("  ! No se encontró mermaid.min.js; se omite el diagrama.")
        return

    texto = MARKDOWN.read_text(encoding="utf-8")
    coincidencia = re.search(r"```mermaid\s*(.*?)```", texto, re.S)
    if not coincidencia:
        return

    codigo = html.escape(coincidencia.group(1).strip())
    temporal = DOCS / "_mermaid_temporal.html"
    temporal.write_text(
        f"""<!doctype html>
<html lang="es"><head><meta charset="utf-8">
<style>
  body {{ margin: 0; padding: 20px; background: #fff;
         font-family: "DejaVu Sans", Arial, sans-serif; }}
  .mermaid {{ display: flex; justify-content: center; }}
</style></head>
<body>
<pre class="mermaid">{codigo}</pre>
<script src="{MERMAID_JS.as_uri()}"></script>
<script>mermaid.initialize({{ startOnLoad: true, theme: "default" }});</script>
</body></html>""",
        encoding="utf-8",
    )

    try:
        page = navegador.new_page(viewport={"width": 1100, "height": 800})
        page.goto(temporal.as_uri(), wait_until="load")
        page.wait_for_selector(".mermaid svg", state="visible", timeout=30_000)
        DIAGRAMA.parent.mkdir(parents=True, exist_ok=True)
        page.locator(".mermaid svg").screenshot(path=str(DIAGRAMA))
        page.close()
        print(f"  ✔ Diagrama ER: {DIAGRAMA.name}")
    finally:
        temporal.unlink(missing_ok=True)


def main() -> None:
    texto = MARKDOWN.read_text(encoding="utf-8")

    # La portada se genera aparte; se quita del Markdown para no duplicarla.
    if "## Índice" in texto:
        texto = texto[texto.index("## Índice"):]

    with sync_playwright() as p:
        navegador = p.chromium.launch(
            executable_path=CHROMIUM_PATH,
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage"],
        )

        generar_diagrama(navegador)

        # Reemplaza el bloque Mermaid por la imagen generada.
        texto = re.sub(
            r"```mermaid.*?```",
            "![Modelo entidad-relación](capturas/00-modelo-er.png)",
            texto,
            flags=re.S,
        )

        cuerpo = markdown.markdown(
            texto,
            extensions=["tables", "fenced_code", "toc", "sane_lists"],
        )

        documento = f"""<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <base href="{DOCS.as_uri()}/">
  <style>{CSS}</style>
</head>
<body>
{PORTADA}
<article>{cuerpo}</article>
</body>
</html>"""

        temporal = DOCS / "_informe_temporal.html"
        temporal.write_text(documento, encoding="utf-8")
        try:
            page = navegador.new_page()
            page.goto(temporal.as_uri(), wait_until="load")
            page.wait_for_load_state("networkidle")
            page.pdf(
                path=str(SALIDA_PDF),
                format="A4",
                print_background=True,
                prefer_css_page_size=True,
                display_header_footer=True,
                header_template=(
                    '<div style="font-size:8px;width:100%;text-align:right;'
                    'padding:0 16mm;color:#8a97a8;">Práctica N° 4 · Tablón de Anuncios</div>'
                ),
                footer_template=(
                    '<div style="font-size:8px;width:100%;text-align:center;'
                    'color:#8a97a8;"><span class="pageNumber"></span> / '
                    '<span class="totalPages"></span></div>'
                ),
                margin={"top": "20mm", "bottom": "16mm", "left": "16mm", "right": "16mm"},
            )
            page.close()
        finally:
            temporal.unlink(missing_ok=True)

        navegador.close()

    print(f"\nPDF generado en: {SALIDA_PDF}")


if __name__ == "__main__":
    main()
