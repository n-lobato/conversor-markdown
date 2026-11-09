#!/usr/bin/env bash
# Instala o Conversor Markdown só para o seu usuário (sem sudo), em ~/.local.
# Depois disso ele aparece no menu de aplicativos.
set -euo pipefail
ORIGEM="$(cd "$(dirname "$0")" && pwd)/conversor-markdown"
DESTINO="$HOME/.local/share/conversor-markdown"
[ -x "$ORIGEM/conversor-markdown" ] || { echo "Rode este script de dentro da pasta extraída."; exit 1; }

rm -rf "$DESTINO"
mkdir -p "$DESTINO" "$HOME/.local/bin" "$HOME/.local/share/applications" \
         "$HOME/.local/share/icons/hicolor/512x512/apps"
cp -R "$ORIGEM/." "$DESTINO/"
ln -sf "$DESTINO/conversor-markdown" "$HOME/.local/bin/conversor-markdown"
cp "$DESTINO/conversor-markdown.png" "$HOME/.local/share/icons/hicolor/512x512/apps/conversor-markdown.png"
cat > "$HOME/.local/share/applications/conversor-markdown.desktop" <<DESK
[Desktop Entry]
Type=Application
Name=Conversor Markdown
Comment=Converte PDF, Word, PowerPoint, Excel e imagens em Markdown, no próprio computador
Exec="$DESTINO/conversor-markdown" %F
Icon=conversor-markdown
Terminal=false
Categories=Office;Utility;
DESK
update-desktop-database "$HOME/.local/share/applications" >/dev/null 2>&1 || true

echo "Conversor Markdown instalado. Procure por ele no menu de aplicativos."
if ! command -v tesseract >/dev/null 2>&1; then
    echo
    echo "Para ler imagens e PDFs escaneados (OCR), instale o Tesseract:"
    echo "  Ubuntu/Debian/Mint: sudo apt install tesseract-ocr tesseract-ocr-por"
    echo "  Fedora:             sudo dnf install tesseract tesseract-langpack-por"
    echo "  Arch:               sudo pacman -S tesseract tesseract-data-por"
fi
