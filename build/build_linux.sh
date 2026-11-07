#!/usr/bin/env bash
# Gera o Conversor Markdown para Linux (x86-64):
#   - .deb para Ubuntu, Debian, Mint e derivados (instala o Tesseract como dependência)
#   - .tar.gz para as demais distribuições, com instalar.sh e desinstalar.sh (sem sudo)
# O OCR usa o Tesseract do sistema.
# Uso (na raiz do projeto, com o ambiente Python ativo):  bash build/build_linux.sh 1.3.0
set -euo pipefail

VERSAO="${1:?informe a versão, ex.: 1.3.0}"
RAIZ="$(cd "$(dirname "$0")/.." && pwd)"
cd "$RAIZ"
PY="${PYTHON:-python}"
TMP="$(mktemp -d)"
NOME="conversor-markdown"
APP="$TMP/dist/$NOME"

echo "1/4 Gerando o executável..."
"$PY" -m PyInstaller --noconfirm --clean --onedir --name "$NOME" \
    --add-data "$RAIZ/assets/icone.png:assets" \
    --workpath "$TMP/work" --distpath "$TMP/dist" --specpath "$TMP/work" \
    --collect-all pymupdf --collect-all pymupdf4llm --collect-all onnxruntime --collect-all tkinterdnd2 \
    --hidden-import pytesseract --hidden-import xlrd --hidden-import mammoth --hidden-import markdownify \
    --hidden-import anonimizacao --hidden-import revisao_tk --hidden-import preferencias \
    --hidden-import plataforma --collect-submodules anonimizador \
    --log-level WARN conversor_markdown.py

echo "2/4 Licenças, ícone e atalho..."
mkdir -p "$APP/LICENCAS"
cp LICENSE "$APP/LICENCAS/LICENSE-Conversor-Markdown-AGPL-3.0.txt"
cp THIRD-PARTY-NOTICES.md "$APP/LICENCAS/"
cp anonimizador/LICENSE-GPL-3.0.txt "$APP/LICENCAS/LICENSE-motor-Anonimizador-LGPD-GPL-3.0.txt"
"$PY" build/coletar_licencas.py "$APP/LICENCAS/python" >/dev/null
cp assets/icone.png "$APP/$NOME.png"
cp LEIA-ME-linux.txt "$APP/LEIA-ME.txt"
mkdir -p "$RAIZ/dist"

echo "3/4 Pacote .deb..."
DEB="$TMP/deb"
mkdir -p "$DEB/DEBIAN" "$DEB/opt" "$DEB/usr/bin" "$DEB/usr/share/applications" \
         "$DEB/usr/share/icons/hicolor/512x512/apps" "$DEB/usr/share/icons/hicolor/scalable/apps" \
         "$DEB/usr/share/doc/$NOME"
cp -R "$APP" "$DEB/opt/$NOME"
ln -s "/opt/$NOME/$NOME" "$DEB/usr/bin/$NOME"
cp assets/icone.png "$DEB/usr/share/icons/hicolor/512x512/apps/$NOME.png"
cp assets/icone.svg "$DEB/usr/share/icons/hicolor/scalable/apps/$NOME.svg"
cat > "$DEB/usr/share/applications/$NOME.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=Conversor Markdown
Comment=Converte PDF, Word, PowerPoint, Excel e imagens em Markdown, no próprio computador
Exec=$NOME %F
Icon=$NOME
Terminal=false
Categories=Office;Utility;
Keywords=markdown;pdf;docx;ocr;lgpd;anonimizar;
EOF
cat > "$DEB/usr/share/doc/$NOME/copyright" <<EOF
Conversor Markdown
Copyright (C) 2026 n-lobato
Licença: GNU AGPL v3. Textos completos em /opt/$NOME/LICENCAS.
Código-fonte: https://github.com/n-lobato/conversor-markdown
EOF
TAMANHO=$(du -sk "$DEB/opt" | cut -f1)
cat > "$DEB/DEBIAN/control" <<EOF
Package: $NOME
Version: $VERSAO
Section: utils
Priority: optional
Architecture: amd64
Maintainer: n-lobato <n-lobato@users.noreply.github.com>
Homepage: https://github.com/n-lobato/conversor-markdown
Installed-Size: $TAMANHO
Depends: tesseract-ocr, tesseract-ocr-por, libx11-6
Description: Conversor local de documentos para Markdown
 Converte PDF, Word, PowerPoint, Excel, CSV e imagens em Markdown, em lote,
 sem enviar nada para a internet. Tem OCR e anonimização opcional de dados
 pessoais (nomes, CPF, endereços) com revisão antes de salvar.
EOF
chmod -R u=rwX,go=rX "$DEB"
chmod 755 "$DEB/opt/$NOME/$NOME"
dpkg-deb --root-owner-group --build "$DEB" "$RAIZ/dist/${NOME}_${VERSAO}_amd64.deb" >/dev/null

echo "4/4 Pacote .tar.gz..."
cp build/linux/instalar.sh build/linux/desinstalar.sh "$TMP/dist/"
chmod +x "$TMP/dist/instalar.sh" "$TMP/dist/desinstalar.sh"
PASTA="Conversor-Markdown-v$VERSAO-linux-x64"
mv "$TMP/dist" "$TMP/$PASTA"
tar -C "$TMP" -czf "$RAIZ/dist/$PASTA.tar.gz" "$PASTA"
rm -rf "$TMP"
ls -lh "$RAIZ"/dist/*.deb "$RAIZ"/dist/*.tar.gz
