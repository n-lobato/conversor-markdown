#!/usr/bin/env bash
# Gera o Conversor Markdown para Mac: um .app com o Tesseract incluído, dentro de um .dmg.
# Uso (na raiz do projeto, com o ambiente Python ativo):
#   brew install tesseract dylibbundler
#   bash build/build_mac.sh 1.3.0
set -euo pipefail

VERSAO="${1:?informe a versão, ex.: 1.3.0}"
RAIZ="$(cd "$(dirname "$0")/.." && pwd)"
cd "$RAIZ"
PY="${PYTHON:-python}"
TMP="$(mktemp -d)"
APP="$TMP/dist/Conversor Markdown.app"
ARQ="$(uname -m)"
[ "$ARQ" = "arm64" ] && NOME_ARQ="apple-silicon" || NOME_ARQ="intel"
# Dados do OCR numa versão fixa (commit de 09/03/2024 do tesseract-ocr/tessdata), com o
# SHA-256 conferido: se o arquivo baixado não for exatamente esse, o build para.
TESSDATA_COMMIT="ced78752cc61322fb554c280d13360b35b8684e4"
TESSDATA_URL="https://github.com/tesseract-ocr/tessdata/raw/$TESSDATA_COMMIT"
SHA_por="016c6a371bb1e4c48fe521908cf3ba3d751fade0ab846ad5d4086b563f5c528c"
SHA_eng="daa0c97d651c19fba3b25e81317cd697e9908c8208090c94c3905381c23fc047"

echo "1/6 Gerando o aplicativo..."
"$PY" -m PyInstaller --noconfirm --clean --windowed --onedir --name "Conversor Markdown" \
    --osx-bundle-identifier io.github.n-lobato.conversor-markdown \
    --icon "$RAIZ/assets/icone.png" --add-data "$RAIZ/assets/icone.png:assets" \
    --workpath "$TMP/work" --distpath "$TMP/dist" --specpath "$TMP/work" \
    --collect-all pymupdf --collect-all pymupdf4llm --collect-all onnxruntime --collect-all tkinterdnd2 \
    --hidden-import pytesseract --hidden-import xlrd --hidden-import mammoth --hidden-import markdownify \
    --hidden-import anonimizacao --hidden-import revisao_tk --hidden-import preferencias \
    --hidden-import plataforma --collect-submodules anonimizador \
    --log-level WARN conversor_markdown.py

echo "2/6 Copiando o Tesseract e as bibliotecas dele para dentro do aplicativo..."
TESS="$APP/Contents/Frameworks/Tesseract-OCR"
DADOS="$APP/Contents/Resources/tessdata"
mkdir -p "$TESS/libs" "$DADOS"
cp "$(brew --prefix tesseract)/bin/tesseract" "$TESS/"
chmod u+w "$TESS/tesseract"
dylibbundler -of -cd -b -x "$TESS/tesseract" -d "$TESS/libs" -p @executable_path/libs/ >/dev/null
if otool -L "$TESS/tesseract" "$TESS"/libs/*.dylib | grep -E "/opt/homebrew|/usr/local/(opt|Cellar)"; then
    echo "ERRO: o Tesseract ainda aponta para bibliotecas do Homebrew"; exit 1
fi
for l in eng por; do
    curl -fsSL -o "$DADOS/$l.traineddata" "$TESSDATA_URL/$l.traineddata"
    esperado="SHA_$l"
    obtido="$(shasum -a 256 "$DADOS/$l.traineddata" | awk '{print $1}')"
    if [ "$obtido" != "${!esperado}" ]; then
        echo "ERRO: SHA-256 diferente do esperado em $l.traineddata ($obtido)"; exit 1
    fi
done
cp -R "$(brew --prefix tesseract)/share/tessdata/configs" "$DADOS/" 2>/dev/null || true
cp -R "$(brew --prefix tesseract)/share/tessdata/tessconfigs" "$DADOS/" 2>/dev/null || true
codesign --force -s - "$TESS"/libs/*.dylib "$TESS/tesseract"
# versão mínima do macOS exigida pelo Tesseract e pelas bibliotecas (a maior vale para o pacote)
# 14.0 é o mínimo do Python e do onnxruntime incluídos
MINIMO=$( { echo 14.0; for f in "$TESS/tesseract" "$TESS"/libs/*.dylib; do vtool -show-build "$f" 2>/dev/null | awk '/minos/{print $2}' || true; done; } | sort -V | tail -1)
echo "    macOS mínimo do OCR incluído: $MINIMO"
for f in "$TESS/tesseract" "$TESS"/libs/*.dylib; do echo "      $(vtool -show-build "$f" 2>/dev/null | awk '/minos/{print $2}')  $(basename "$f")"; done
echo "$MINIMO" > "$TMP/minimo.txt"
"$TESS/tesseract" --tessdata-dir "$DADOS" --list-langs | grep -q por || { echo "ERRO: Tesseract copiado não funcionou"; exit 1; }

echo "3/6 Reunindo licenças..."
LIC="$APP/Contents/Resources/LICENCAS"
mkdir -p "$LIC/Tesseract-e-bibliotecas"
cp LICENSE "$LIC/LICENSE-Conversor-Markdown-AGPL-3.0.txt"
cp THIRD-PARTY-NOTICES.md "$LIC/"
cp anonimizador/LICENSE-GPL-3.0.txt "$LIC/LICENSE-motor-Anonimizador-LGPD-GPL-3.0.txt"
FORMULAS="tesseract $(brew deps --installed tesseract | tr '\n' ' ')"
brew info --json=v2 $FORMULAS | "$PY" build/licencas_homebrew.py > "$LIC/Tesseract-e-bibliotecas/_INDICE.md"
for f in $FORMULAS; do
    destino="$LIC/Tesseract-e-bibliotecas/$f"
    mkdir -p "$destino"
    find "$(brew --prefix "$f")/" -maxdepth 1 -type f \( -iname 'LICEN*' -o -iname 'COPYING*' -o -iname 'NOTICE*' -o -iname 'AUTHORS*' \) \
        -exec cp {} "$destino/" \; 2>/dev/null || true
done
"$PY" build/coletar_licencas.py "$LIC/python" >/dev/null

echo "4/6 Ajustando o Info.plist (versão e arrastar arquivos para o ícone)..."
PL="$APP/Contents/Info.plist"
plutil -replace CFBundleShortVersionString -string "$VERSAO" "$PL"
plutil -replace CFBundleVersion -string "$VERSAO" "$PL"
plutil -replace LSMinimumSystemVersion -string "$(cat "$TMP/minimo.txt")" "$PL"
plutil -replace CFBundleDisplayName -string "Conversor Markdown" "$PL"
plutil -replace NSHumanReadableCopyright -string "© 2026 n-lobato. Software livre (GNU AGPL v3)." "$PL"
plutil -replace CFBundleDocumentTypes -json \
    '[{"CFBundleTypeName":"Documento","CFBundleTypeRole":"Viewer","LSHandlerRank":"Alternate","LSItemContentTypes":["public.data","public.folder"]}]' "$PL"

echo "5/6 Assinando (assinatura local, sem certificado da Apple)..."
codesign --force --deep -s - "$APP"
codesign --verify --deep --strict "$APP"

echo "6/6 Montando o .dmg..."
DMG_DIR="$TMP/dmg"
mkdir -p "$DMG_DIR"
cp -R "$APP" "$DMG_DIR/"
ln -s /Applications "$DMG_DIR/Aplicativos"
cp LEIA-ME-mac.txt "$DMG_DIR/LEIA-ME.txt"
mkdir -p "$RAIZ/dist"
SAIDA="$RAIZ/dist/Conversor-Markdown-v$VERSAO-mac-$NOME_ARQ.dmg"
rm -f "$SAIDA"
# Nas máquinas Mac do GitHub, o hdiutil às vezes falha com "Resource busy" sem motivo real;
# tenta até 5 vezes antes de desistir.
for tentativa in 1 2 3 4 5; do
    if hdiutil create -volname "Conversor Markdown" -srcfolder "$DMG_DIR" -ov -format UDZO "$SAIDA" >/dev/null; then
        break
    fi
    if [ "$tentativa" = 5 ]; then echo "ERRO: hdiutil falhou 5 vezes"; exit 1; fi
    echo "    hdiutil falhou (tentativa $tentativa); tentando de novo em 15 s..."
    sleep 15
done
# cópia do .app fora do .dmg, para o teste automático
rm -rf "$RAIZ/dist/mac-app" && mkdir -p "$RAIZ/dist/mac-app" && cp -R "$APP" "$RAIZ/dist/mac-app/"
rm -rf "$TMP"
echo "Pronto: $SAIDA ($(du -h "$SAIDA" | cut -f1))"
