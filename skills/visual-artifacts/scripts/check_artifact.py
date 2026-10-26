#!/usr/bin/env python3
"""Revisa un artifact HTML de Antigravity contra las restricciones del host y la skill visual-artifacts.

Uso: python3 check_artifact.py <archivo.html> [...]
Sale con código 1 si hay errores; los avisos no bloquean.
"""
import re
import sys
from pathlib import Path

TAILWIND_URL = "https://www.gstatic.com/antigravity/web/dev/tailwindcss.min.js"
MIN_FONT_PX = 12
HOST_TOKENS = (
    "background", "content", "card", "sidebar", "border", "foreground", "muted-foreground",
    "placeholder", "primary", "primary-foreground", "secondary", "secondary-foreground", "accent",
)

# (regex, mensaje). Errores: rompen el render o el tema. Avisos: suelen indicar diseño genérico.
ERRORS = [
    (r"<link[^>]+href=[\"']https?://", "Hoja de estilos externa: el CSP del host la bloquea."),
    (r"@import\s+url\(", "@import externo: el CSP del host lo bloquea."),
    (r"fonts\.googleapis|fonts\.gstatic", "Google Fonts está bloqueado: la tipografía la pone el host."),
    (r"text-\[(?:[0-9]|1[01])(?:\.\d+)?px\]", f"Texto por debajo de {MIN_FONT_PX}px."),
    (r"lorem ipsum|\bItem [0-9]\b|\bPlaceholder\b", "Contenido de relleno: usa datos reales."),
]
WARNINGS = [
    (r"\b(?:min-)?h-screen\b|100vh", "h-screen/100vh: si el artifact va inline, colapsa el iframe."),
    (r"\b(?:text|bg|border)-(?:white|black)\b", "Color fijo blanco/negro: usa los tokens del host para soportar ambos temas."),
    (r"\b(?:text|bg|border)-(?:slate|gray|zinc|neutral|stone)-\d{2,3}\b", "Gris fijo de Tailwind: usa --muted-foreground, --card o --border."),
    (r"bg-gradient-to-|linear-gradient\([^)]*(?:purple|violet|fuchsia|pink)", "Gradiente decorativo: ¿significa algo?"),
    (r"(?i)\b(?:validad[oa]s?|verificad[oa]s?|datos reales|métricas reales)\b",
     "Sello de credibilidad: si no hay fuentes citadas, quítalo y marca las cifras como estimadas."),
]


def check(path: Path) -> tuple[list[str], list[str]]:
    html = path.read_text(encoding="utf-8")
    errors = [msg for pattern, msg in ERRORS if re.search(pattern, html, re.IGNORECASE)]
    # Los avisos miran solo lo que se renderiza: los comentarios HTML son notas del autor.
    rendered = re.sub(r"<!--.*?-->", "", html, flags=re.DOTALL)
    warnings = [msg for pattern, msg in WARNINGS if re.search(pattern, rendered)]

    for src in re.findall(r"<script[^>]+src=[\"']([^\"']+)", html, re.IGNORECASE):
        if src != TAILWIND_URL:
            errors.append(f"Script externo no permitido por el CSP: {src}")

    for size in re.findall(r"font-size\s*:\s*(\d+(?:\.\d+)?)px", html):
        if float(size) < MIN_FONT_PX:
            errors.append(f"font-size: {size}px está por debajo de {MIN_FONT_PX}px.")
            break

    for block in re.findall(r":root\s*\{([^}]*)\}", html):
        redefined = [t for t in HOST_TOKENS if re.search(rf"--{t}\s*:", block)]
        if redefined:
            errors.append(f"Redefine tokens del host en :root ({', '.join(redefined)}): rompe el tema.")

    if not re.search(r"<!DOCTYPE html>", html, re.IGNORECASE):
        warnings.append("Falta <!DOCTYPE html>.")
    if TAILWIND_URL not in html:
        warnings.append("No carga el Tailwind permitido del host.")
    if not re.search(r"<!--\s*dirección:", html, re.IGNORECASE):
        warnings.append("Falta el comentario '<!-- dirección: ... -->' del paso 2.")
    if not re.search(r"html\.light", html) and re.search(r"oklch\(|#[0-9a-f]{3,6}\b|rgb\(", html, re.IGNORECASE):
        warnings.append("Define colores propios pero no tiene variante para html.light.")
    for svg in re.findall(r"<svg\b[^>]*>", html, re.IGNORECASE):
        if "viewBox" not in svg and "va-chart" not in svg:
            warnings.append("Hay un <svg> sin viewBox: no escalará.")
            break

    return errors, warnings


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__.strip())
        return 2
    failed = False
    for arg in sys.argv[1:]:
        path = Path(arg)
        if not path.is_file():
            print(f"✗ {arg}: no existe")
            failed = True
            continue
        errors, warnings = check(path)
        print(f"{'✗' if errors else '✓'} {path.name}: {len(errors)} errores, {len(warnings)} avisos")
        for msg in errors:
            print(f"  ERROR  {msg}")
        for msg in warnings:
            print(f"  AVISO  {msg}")
        failed = failed or bool(errors)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
