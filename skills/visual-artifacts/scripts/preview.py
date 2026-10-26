#!/usr/bin/env python3
"""Genera una copia de un artifact con los tokens del host simulados, para revisarlo en el navegador.

Uso: python3 preview.py <archivo.html> [--light] [--inline]
  --light   arranca en tema claro (el botón de la esquina alterna el tema)
  --inline  dibuja una línea en 500px: lo que quede debajo no se ve en un embed inline

Escribe <nombre>.preview.html en el directorio temporal del sistema e imprime la ruta file://.
Ábrela con el navegador, toma capturas en ~1280px y en 375px, y prueba ambos temas.
El original no se modifica: la preview no es el artifact y no se entrega al usuario.
"""
import sys
import tempfile
from pathlib import Path

# Aproximación de los tokens que inyecta Antigravity en el iframe; solo sirve para revisar.
HOST_TOKENS = """
:root{--background:#0e1014;--content:#0e1014;--card:#16191f;--sidebar:#121418;--border:#2a2f38;
--foreground:#e8eaee;--muted-foreground:#9aa1ad;--placeholder:#6b7280;--primary:#6ea8fe;
--primary-foreground:#0b1020;--secondary:#232831;--secondary-foreground:#e8eaee;--accent:#232831}
html.light{--background:#f7f7f8;--content:#f7f7f8;--card:#ffffff;--sidebar:#f0f0f2;--border:#e2e4e9;
--foreground:#16181d;--muted-foreground:#5d6470;--placeholder:#9aa1ad;--primary:#2563eb;
--primary-foreground:#ffffff;--secondary:#eef0f3;--secondary-foreground:#16181d;--accent:#eef0f3}
body{font-family:system-ui,'Segoe UI',sans-serif}
#va-preview-toggle{position:fixed;top:8px;right:8px;z-index:9999;font:600 12px system-ui;padding:6px 10px;
border-radius:8px;border:1px solid var(--border);background:var(--card);color:var(--foreground);cursor:pointer}
"""
INLINE_MARK = """
html{max-width:760px}
body{position:relative}
body::after{content:'límite del embed inline · 500px';position:absolute;left:0;right:0;top:500px;
border-top:2px dashed #e5484d;color:#e5484d;font:600 12px system-ui;padding:2px 8px;pointer-events:none}
"""
TOGGLE = """<button id="va-preview-toggle" type="button"
onclick="document.documentElement.classList.toggle('light')">Cambiar tema</button>"""
LIGHT_ON_LOAD = "<script>document.documentElement.classList.add('light')</script>"


def build(html: str, light: bool, inline: bool) -> str:
    if "</head>" not in html or "</body>" not in html:
        raise ValueError("El artifact debe tener <head> y <body> completos.")
    style = f"<style>{HOST_TOKENS}{INLINE_MARK if inline else ''}</style>"
    extras = TOGGLE + (LIGHT_ON_LOAD if light else "")
    return html.replace("</head>", style + "</head>", 1).replace("</body>", extras + "</body>", 1)


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if len(args) != 1:
        print(__doc__.strip())
        return 2
    src = Path(args[0])
    if not src.is_file():
        print(f"No existe: {src}")
        return 1
    try:
        out_html = build(src.read_text(encoding="utf-8"), "--light" in sys.argv, "--inline" in sys.argv)
    except ValueError as err:
        print(f"Error: {err}")
        return 1
    out = Path(tempfile.gettempdir()) / f"{src.stem}.preview.html"
    out.write_text(out_html, encoding="utf-8")
    print(out.resolve().as_uri())
    return 0


if __name__ == "__main__":
    sys.exit(main())
