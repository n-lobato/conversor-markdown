#!/usr/bin/env bash
# Remove o Conversor Markdown instalado pelo instalar.sh. Os arquivos .md convertidos não são apagados.
set -euo pipefail
rm -rf "$HOME/.local/share/conversor-markdown"
rm -f "$HOME/.local/bin/conversor-markdown" \
      "$HOME/.local/share/applications/conversor-markdown.desktop" \
      "$HOME/.local/share/icons/hicolor/512x512/apps/conversor-markdown.png"
rm -rf "$HOME/.config/conversor-markdown"
update-desktop-database "$HOME/.local/share/applications" >/dev/null 2>&1 || true
echo "Conversor Markdown removido."
