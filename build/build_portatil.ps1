# Gera a versao portatil (.exe + Tesseract enxuto + licencas), compacta em .zip
# e monta o instalador (Inno Setup 6) com a mesma pasta.
# Uso (na raiz do projeto):  powershell -ExecutionPolicy Bypass -File build\build_portatil.ps1 -Versao 1.0.0
# Sem o Inno Setup instalado, use -SemInstalador para gerar so o .zip.
param([string]$Versao = "1.0.0", [switch]$SemInstalador)

$ErrorActionPreference = 'Stop'
$raiz = Split-Path -Parent $PSScriptRoot
Set-Location $raiz

$py   = Join-Path $raiz '.venv\Scripts\python.exe'
$tess = Join-Path $raiz 'Tesseract-OCR'
if (-not (Test-Path $py)) { throw "Ambiente .venv nao encontrado. Veja o README (secao Compilar)." }
if (-not (Test-Path "$tess\tesseract.exe")) { throw "Pasta Tesseract-OCR nao encontrada. Veja o README." }
foreach ($l in 'eng', 'por') {
    if (-not (Test-Path "$tess\tessdata\$l.traineddata")) { throw "Falta $l.traineddata em Tesseract-OCR\tessdata." }
}

$tmp = Join-Path $env:TEMP 'conversor_build'
Remove-Item -Recurse -Force $tmp -ErrorAction SilentlyContinue

Write-Host "1/5 Gerando o executavel..."
$ErrorActionPreference = 'Continue'   # PyInstaller escreve avisos no stderr
& $py -m PyInstaller --noconfirm --clean --windowed --onedir --name 'Conversor Markdown' `
    --icon "$raiz\assets\icone.ico" --add-data "$raiz\assets\icone.png;assets" `
    --workpath "$tmp\work" --distpath "$tmp\dist" --specpath "$tmp\work" `
    --collect-all pymupdf --collect-all pymupdf4llm --collect-all onnxruntime --collect-all tkinterdnd2 `
    --hidden-import pytesseract --hidden-import xlrd --hidden-import mammoth --hidden-import markdownify `
    --hidden-import anonimizacao --hidden-import revisao_tk --hidden-import preferencias --hidden-import plataforma --collect-submodules anonimizador `
    --log-level WARN conversor_markdown.py
$ErrorActionPreference = 'Stop'
if ($LASTEXITCODE -ne 0) { throw "PyInstaller falhou." }

$app = "$tmp\dist\Conversor Markdown"

Write-Host "2/5 Copiando o Tesseract (somente o necessario para o OCR)..."
$t = "$app\Tesseract-OCR"
New-Item -ItemType Directory -Force "$t\tessdata" | Out-Null
Copy-Item "$tess\tesseract.exe" $t
# Descobre as DLLs lendo as importacoes do tesseract.exe e de cada DLL (recursivo).
# A lista fixa que havia aqui deixou de fora a libcurl-4.dll e quebrou o OCR da 1.2.0 e da 1.3.0.
$ErrorActionPreference = 'Continue'
$dlls = & $py build\dependencias_windows.py $tess tesseract.exe
$codigo = $LASTEXITCODE
$ErrorActionPreference = 'Stop'
if ($codigo -ne 0 -or -not $dlls) { throw "Nao foi possivel listar as DLLs do Tesseract." }
foreach ($d in $dlls) { Copy-Item "$tess\$d" $t }
Write-Host ("    {0} DLLs: {1}" -f @($dlls).Count, ($dlls -join ', '))
Copy-Item "$tess\tessdata\eng.traineddata", "$tess\tessdata\por.traineddata" "$t\tessdata"
foreach ($c in 'configs', 'tessconfigs') {
    if (Test-Path "$tess\tessdata\$c") { Copy-Item -Recurse "$tess\tessdata\$c" "$t\tessdata\$c" }
}
# Testa ISOLADO: com o PATH reduzido ao Windows, para que DLLs de um Tesseract instalado
# no sistema nao mascarem uma DLL que faltou na copia (foi o que escondeu o erro antes).
$pathOriginal = $env:PATH
$env:PATH = "$env:SystemRoot\System32;$env:SystemRoot"
$ErrorActionPreference = 'Continue'
$teste = & "$t\tesseract.exe" --list-langs 2>&1 | Out-String
$codigo = $LASTEXITCODE
$ErrorActionPreference = 'Stop'
$env:PATH = $pathOriginal
if ($codigo -ne 0 -or $teste -notmatch 'por') {
    throw ("Tesseract copiado nao funcionou sozinho (codigo {0}; -1073741515 = falta DLL): {1}" -f $codigo, $teste)
}
Write-Host "    Tesseract da pasta funciona sozinho (portugues disponivel)."

Write-Host "3/5 Reunindo licencas..."
$lic = "$app\LICENCAS"
New-Item -ItemType Directory -Force "$lic\Tesseract", "$lic\Python-e-TclTk" | Out-Null
Copy-Item LICENSE "$lic\LICENSE-Conversor-Markdown-AGPL-3.0.txt"
Copy-Item THIRD-PARTY-NOTICES.md $lic
Copy-Item anonimizador\LICENSE-GPL-3.0.txt "$lic\LICENSE-motor-Anonimizador-LGPD-GPL-3.0.txt"
Copy-Item "$tess\doc\LICENSE" "$lic\Tesseract\LICENSE.txt"
$dlls | Out-File -Encoding utf8 "$lic\Tesseract\DLLS-INCLUIDAS.txt"
if (Test-Path "$tess\doc\AUTHORS") { Copy-Item "$tess\doc\AUTHORS" "$lic\Tesseract\AUTHORS.txt" }
# Textos de licenca de cada DLL, tirados dos pacotes MSYS2 de onde elas vem.
# No GitHub Actions (CI) e obrigatorio; num build local sem MSYS2 so avisa.
$msys = if ($env:MSYS2_ROOT) { $env:MSYS2_ROOT } else { 'C:\msys64' }
if (Test-Path "$msys\usr\bin\bash.exe") {
    $argsLic = @('build\licencas_windows.py', '--msys', $msys, '--destino', "$lic\Tesseract\bibliotecas",
                 '--tesseract-licenca', "$tess\doc\LICENSE")
    if ($env:CI) { $argsLic += '--obrigatorio' }
    $ErrorActionPreference = 'Continue'
    & $py @argsLic @dlls
    $codigo = $LASTEXITCODE
    $ErrorActionPreference = 'Stop'
    if ($codigo -ne 0) { throw "Falha ao reunir os textos de licenca das DLLs do Tesseract." }
} elseif ($env:CI) {
    throw "MSYS2 nao encontrado em ${msys}: necessario para os textos de licenca das DLLs."
} else {
    Write-Warning "MSYS2 nao encontrado em ${msys}: o pacote sai sem os textos de licenca das DLLs."
}
$base = (& $py -c "import sys; print(sys.base_prefix)").Trim()
Copy-Item "$base\LICENSE.txt" "$lic\Python-e-TclTk\Python-LICENSE.txt"
foreach ($x in 'tcl8.6', 'tk8.6') {
    if (Test-Path "$base\tcl\$x\license.terms") { Copy-Item "$base\tcl\$x\license.terms" "$lic\Python-e-TclTk\$x-license.txt" }
}
& $py build\coletar_licencas.py "$lic\python"
Copy-Item LEIA-ME-portatil.txt "$app\LEIA-ME.txt"

Write-Host "4/5 Compactando..."
New-Item -ItemType Directory -Force "$raiz\dist" | Out-Null
$zip = "$raiz\dist\Conversor-Markdown-v$Versao-windows-x64.zip"
Remove-Item $zip -ErrorAction SilentlyContinue
# Python em vez de [IO.Compression.ZipFile]::CreateFromDirectory, que no Windows
# PowerShell 5.1 grava os caminhos com barra invertida (fora do padrao do zip).
& $py build\criar_zip.py "$tmp\dist" $zip
if ($LASTEXITCODE -ne 0) { throw "Falha ao criar o .zip." }
Write-Host ("    {0} ({1:N0} MB)" -f $zip, ((Get-Item $zip).Length / 1MB))

if ($SemInstalador) {
    Write-Host "5/5 Instalador pulado (-SemInstalador)."
} else {
    Write-Host "5/5 Montando o instalador..."
    $iscc = @("${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe", "$env:ProgramFiles\Inno Setup 6\ISCC.exe",
              "$env:LOCALAPPDATA\Programs\Inno Setup 6\ISCC.exe") | Where-Object { Test-Path $_ } | Select-Object -First 1
    if (-not $iscc) { throw "Inno Setup 6 nao encontrado. Instale (choco install innosetup) ou use -SemInstalador." }
    & $iscc /Q "/DVersao=$Versao" "/DOrigem=$app" build\instalador.iss
    if ($LASTEXITCODE -ne 0) { throw "Inno Setup falhou." }
    $inst = "$raiz\dist\Conversor-Markdown-v$Versao-windows-x64-instalador.exe"
    Write-Host ("    {0} ({1:N0} MB)" -f $inst, ((Get-Item $inst).Length / 1MB))
}
Remove-Item -Recurse -Force $tmp
Write-Host "Pronto."
exit 0
