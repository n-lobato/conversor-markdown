# Conversor Markdown

Programa para Windows que converte PDF, Word, PowerPoint, Excel, CSV e imagens em Markdown, em lote, **sem enviar nada para a internet**. Tudo roda no próprio computador, inclusive o OCR.

Feito para quem precisa preparar documentos para ferramentas de IA, bases de conhecimento ou anotações, mas não quer (ou não pode) subir arquivos para serviços online.

## Por que local?

Muitos conversores online pedem o upload do documento. Para contratos, processos, relatórios internos ou qualquer arquivo com dados pessoais, isso é um risco desnecessário. Aqui o arquivo nunca sai da máquina, o que facilita o cuidado com a LGPD e com informações sensíveis.

## O que ele faz

- Converte **PDF** (inclusive escaneado, com OCR), **Word (.docx)**, **PowerPoint (.pptx)**, **Excel (.xlsx, .xlsm, .xls)**, **CSV** e **imagens** (PNG, JPG, TIF, BMP, GIF, WEBP).
- **Em lote:** uma pasta inteira, com subpastas, mantendo a mesma estrutura na saída.
- **Arrastar e soltar:** solte arquivos ou pastas na janela, ou em cima do ícone, e a conversão começa.
- **OCR em português e inglês** para imagens, PDFs escaneados e figuras dentro de Word e PowerPoint.
- Preserva títulos, listas, negrito, tabelas e notas do apresentador.
- Se um arquivo falhar, os outros continuam. Os erros ficam registrados num log.

## Download

Baixe o arquivo `.zip` da versão mais recente em **[Releases](https://github.com/n-lobato/conversor-markdown/releases/latest)**.

1. Extraia o `.zip` (botão direito > Extrair tudo).
2. Abra `Conversor Markdown.exe`.

Não precisa instalar Python nem ter permissão de administrador. Funciona no Windows 10 e 11 (64 bits).

Na primeira execução, o Windows pode mostrar o aviso "O Windows protegeu o computador", porque o programa não tem assinatura digital comercial. Clique em **Mais informações** e depois em **Executar assim mesmo**.

## Como usar

**Jeito rápido:** arraste arquivos ou pastas para dentro da janela. Se você não escolher onde salvar, os `.md` vão para uma pasta `markdown` ao lado dos originais.

**Pelos botões:** escolha a origem (pasta ou arquivos), a pasta de saída e clique em **Converter**.

Opções:

- **Usar OCR:** lê texto de imagens e PDFs escaneados. Deixa a conversão mais lenta.
- **Incluir subpastas.**
- **Sobrescrever .md existentes:** se desmarcado, arquivos já convertidos são pulados.
- **Converter automaticamente ao soltar arquivos.**

## Limitações

- Arquivos antigos `.doc` e `.ppt` não são convertidos. Salve como `.docx` ou `.pptx` antes.
- PDFs protegidos por senha não são convertidos.
- Em planilhas, fórmulas mostram o valor salvo pelo Excel. Se o arquivo nunca foi aberto no Excel, aparece a fórmula.
- O resultado do OCR depende da qualidade da imagem. Revise textos importantes.

## Rodar a partir do código

Requer Python 3.10 ou mais recente e o [Tesseract](https://github.com/UB-Mannheim/tesseract/wiki) para o OCR.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\pythonw.exe conversor_markdown.py
```

O programa procura o Tesseract na pasta `Tesseract-OCR` ao lado do script ou na instalação padrão do Windows.

Também funciona pela linha de comando:

```powershell
.\.venv\Scripts\python.exe conversor_markdown.py "C:\pasta\origem" --saida="C:\pasta\saida" [--sem-ocr] [--sem-subpastas] [--sobrescrever]
```

## Compilar a versão portátil

1. Crie o ambiente como acima e instale também o PyInstaller: `.\.venv\Scripts\python.exe -m pip install pyinstaller`
2. Coloque o Tesseract na pasta `Tesseract-OCR`, na raiz do projeto. Uma forma de fazer isso sem administrador é extrair o instalador da [UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki) com o 7-Zip.
3. Baixe o [`por.traineddata`](https://github.com/tesseract-ocr/tessdata/raw/main/por.traineddata) para `Tesseract-OCR\tessdata`.
4. Rode:

```powershell
powershell -ExecutionPolicy Bypass -File build\build_portatil.ps1 -Versao 1.0.0
```

O `.zip` sai na pasta `dist`. O script leva só as partes do Tesseract usadas pelo OCR e junta os textos de licença de todos os componentes.

## Licença

Este projeto é software livre sob a **GNU Affero General Public License v3.0** (arquivo [`LICENSE`](LICENSE)). Você pode usar, estudar, modificar e redistribuir, desde que mantenha a mesma licença e disponibilize o código-fonte.

A licença AGPL foi escolhida porque o projeto usa o [PyMuPDF](https://github.com/pymupdf/PyMuPDF), distribuído pela Artifex sob AGPL-3.0 ou licença comercial. Os demais componentes e suas licenças estão em [`THIRD-PARTY-NOTICES.md`](THIRD-PARTY-NOTICES.md).

## Autor

[n-lobato](https://github.com/n-lobato)
