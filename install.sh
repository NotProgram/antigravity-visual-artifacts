#!/usr/bin/env sh
# Instala la skill visual-artifacts y su regla siempre activa en Antigravity.
#
#   ./install.sh                      instalación global (~/.gemini/config)
#   ./install.sh --workspace <dir>    solo para un proyecto (<dir>/.agents)
#   ./install.sh --uninstall [--workspace <dir>]
set -eu

REPO_DIR=$(cd "$(dirname "$0")" && pwd)
ROOT="${ANTIGRAVITY_CONFIG_DIR:-$HOME/.gemini/config}"
UNINSTALL=0

while [ $# -gt 0 ]; do
  case "$1" in
    --workspace)
      [ $# -ge 2 ] || { echo "Falta la ruta después de --workspace" >&2; exit 2; }
      [ -d "$2" ] || { echo "No existe el directorio: $2" >&2; exit 2; }
      ROOT="$(cd "$2" && pwd)/.agents"
      shift 2 ;;
    --uninstall) UNINSTALL=1; shift ;;
    -h|--help) sed -n '2,7p' "$0"; exit 0 ;;
    *) echo "Opción desconocida: $1" >&2; exit 2 ;;
  esac
done

SKILL_DIR="$ROOT/skills/visual-artifacts"
RULE_FILE="$ROOT/rules/visual-artifacts.md"

if [ "$UNINSTALL" -eq 1 ]; then
  rm -rf "$SKILL_DIR" "$RULE_FILE"
  echo "Desinstalado de $ROOT"
  exit 0
fi

mkdir -p "$SKILL_DIR" "$ROOT/rules"
cp -R "$REPO_DIR/skills/visual-artifacts/." "$SKILL_DIR/"
# La regla apunta a la skill con ruta absoluta: Antigravity a veces no descubre las skills globales solo.
sed "s|{{SKILL_MD}}|$SKILL_DIR/SKILL.md|" "$REPO_DIR/rules/visual-artifacts.md" > "$RULE_FILE"

echo "Skill instalada en: $SKILL_DIR"
echo "Regla instalada en: $RULE_FILE"
echo "Abre una conversación NUEVA en Antigravity y pide, por ejemplo: \"haz un artifact comparando estas 3 opciones\"."
