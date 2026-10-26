#!/usr/bin/env python3
"""Toma capturas de un artifact (escritorio oscuro, escritorio claro y móvil) y detecta desbordes.

Uso: python3 screenshot.py <archivo.html>

Usa los tokens simulados de preview.py. Imprime las rutas de los PNG (ábrelos con tu herramienta de
ver imágenes) y un informe de desborde horizontal a 375px con los elementos culpables.
Código de salida: 0 ok · 1 hay desborde · 3 no se encontró navegador.
Navegador: variable VA_CHROME, o el chrome-headless-shell de Playwright, o Chrome/Chromium/Edge.
"""
from __future__ import annotations

import glob
import html
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from preview import build  # noqa: E402

DESKTOP_WIDTH = 1280
MOBILE_WIDTH = 375
MAX_HEIGHT = 8000
TIMEOUT_S = 60

# Mide el desborde ignorando lo que está dentro de un contenedor con scroll propio y lo deja en un <meta>.
PROBE = """<script>addEventListener('load', () => setTimeout(() => {
  const W = document.documentElement.clientWidth, over = [];
  document.querySelectorAll('body *').forEach(el => {
    const r = el.getBoundingClientRect();
    if (!r.width || r.right <= W + 1 || getComputedStyle(el).position === 'fixed') return;
    for (let p = el.parentElement; p && p !== document.body; p = p.parentElement)
      if (getComputedStyle(p).overflowX !== 'visible') return;
    over.push(el);
  });
  const top = over.filter(e => !over.some(o => o !== e && o.contains(e)));
  const m = document.createElement('meta');
  m.name = 'va-probe';
  m.content = JSON.stringify({
    height: document.documentElement.scrollHeight, width: W,
    scrollWidth: document.documentElement.scrollWidth,
    culprits: top.slice(0, 5).map(e => e.tagName.toLowerCase() + '.' +
      String(e.className).trim().split(/\\s+/).slice(0, 3).join('.') + ' (borde derecho ' + Math.round(e.getBoundingClientRect().right) + 'px)'),
  });
  document.head.append(m);
}, 300));</script>"""


def find_browser() -> tuple[str, bool] | None:
    """Devuelve (ruta, es_headless_shell). El headless shell respeta anchos de 375px; Chrome completo no."""
    if os.environ.get("VA_CHROME"):
        path = os.environ["VA_CHROME"]
        return path, "headless" in Path(path).name
    home = Path.home()
    local = Path(os.environ.get("LOCALAPPDATA", home / "AppData/Local"))
    caches = [home / ".cache/ms-playwright", local / "ms-playwright", home / "Library/Caches/ms-playwright"]
    for cache in caches:
        shells = sorted(glob.glob(str(cache / "chromium_headless_shell-*/chrome-headless-shell-*/chrome-headless-shell*")), reverse=True)
        if shells:
            return shells[0], True
    for name in ("chrome-headless-shell", "chromium", "chromium-browser", "google-chrome", "google-chrome-stable", "msedge"):
        if shutil.which(name):
            return shutil.which(name), name == "chrome-headless-shell"
    for cache in caches:
        full = sorted(glob.glob(str(cache / "chromium-*/chrome-*/chrome*")), reverse=True)
        full = [f for f in full if Path(f).name in ("chrome", "chrome.exe", "Chromium")]
        if full:
            return full[0], False
    for path in (r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                 r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"):
        if Path(path).is_file():
            return path, False
    return None


def run(browser: tuple[str, bool], url: str, width: int, height: int, extra: list[str]) -> str:
    path, is_shell = browser
    cmd = [path, "--no-sandbox", "--disable-gpu", "--hide-scrollbars", "--force-prefers-reduced-motion", "--virtual-time-budget=5000",
           f"--window-size={width},{height}", *extra, url]
    if not is_shell:
        cmd.insert(1, "--headless=new")
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=TIMEOUT_S)
    return result.stdout


def probe(browser: tuple[str, bool], url: str, width: int) -> dict:
    dom = run(browser, url, width, 900, ["--dump-dom"])
    match = re.search(r'name="va-probe" content="([^"]*)"', dom)
    if not match:
        raise RuntimeError("No se pudo medir la página (¿error de JavaScript al cargar?).")
    return json.loads(html.unescape(match.group(1)))


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__.strip())
        return 2
    src = Path(sys.argv[1])
    if not src.is_file():
        print(f"No existe: {src}")
        return 2
    browser = find_browser()
    if not browser:
        print("No encontré navegador. Define VA_CHROME, instala uno (`npx playwright install chromium-headless-shell`)\n"
              "o abre la salida de preview.py con la herramienta de navegador de Antigravity.")
        return 3

    out_dir = Path(tempfile.gettempdir()) / "va-shots"
    out_dir.mkdir(exist_ok=True)
    source = src.read_text(encoding="utf-8")
    pages = {}
    for theme in ("dark", "light"):
        page = out_dir / f"{src.stem}-{theme}.html"
        page.write_text(build(source, theme == "light", False).replace("</body>", PROBE + "</body>", 1), encoding="utf-8")
        pages[theme] = page.resolve().as_uri()

    mobile = probe(browser, pages["dark"], MOBILE_WIDTH)
    desktop = probe(browser, pages["dark"], DESKTOP_WIDTH)
    shots = [("desktop-dark", pages["dark"], DESKTOP_WIDTH, desktop["height"]),
             ("desktop-light", pages["light"], DESKTOP_WIDTH, desktop["height"]),
             ("mobile", pages["dark"], MOBILE_WIDTH, mobile["height"])]
    for name, url, width, height in shots:
        png = out_dir / f"{src.stem}-{name}.png"
        run(browser, url, width, min(height, MAX_HEIGHT), [f"--screenshot={png}"])
        print(f"{name}: {png}")

    if not browser[1]:
        print("AVISO: Chrome completo impone ~500px de ancho mínimo; la captura móvil puede no ser fiel.")
    if desktop["height"] > MAX_HEIGHT:
        print(f"AVISO: la página mide {desktop['height']}px; las capturas se cortan en {MAX_HEIGHT}px.")
    if mobile["scrollWidth"] > mobile["width"]:
        print(f"DESBORDE a {MOBILE_WIDTH}px: la página mide {mobile['scrollWidth']}px de ancho en un viewport de {mobile['width']}px.")
        for culprit in mobile["culprits"]:
            print(f"  culpable: {culprit}")
        return 1
    print(f"Sin desborde horizontal a {MOBILE_WIDTH}px.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
