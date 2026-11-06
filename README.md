# Conversor Markdown

## [Baixar o programa para Windows (.zip, 159 MB)](https://github.com/n-lobato/conversor-markdown/releases/latest/download/Conversor-Markdown-v1.0.0-windows-x64.zip)

> **Atenção:** não use o botão verde **Code > Download ZIP**. Ele baixa só o código-fonte, que não roda sem Python instalado. O programa pronto é o link acima, também disponível na página de [Releases](https://github.com/n-lobato/conversor-markdown/releases/latest).

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
- **Anonimização opcional:** troca nomes, CPF, endereços e outros dados pessoais por códigos antes de salvar, com uma tela de revisão. Veja abaixo.

## Download

Baixe o arquivo **[Conversor-Markdown-v1.0.0-windows-x64.zip](https://github.com/n-lobato/conversor-markdown/releases/latest/download/Conversor-Markdown-v1.0.0-windows-x64.zip)** na página de **[Releases](https://github.com/n-lobato/conversor-markdown/releases/latest)**. Não confunda com o "Download ZIP" do botão verde Code, que traz apenas o código-fonte.

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
- **Anonimizar dados pessoais:** veja a seção seguinte.

## Anonimizar antes de usar com IA

Converter no próprio computador evita o upload do arquivo original, mas o Markdown gerado continua com todos os dados pessoais. Se ele for colado numa ferramenta de IA na nuvem, o problema volta. Para isso existe a opção **Anonimizar dados pessoais (com revisão antes de salvar)**.

Com ela marcada:

1. Os arquivos são convertidos, mas **nada é gravado ainda**.
2. O programa procura nomes, CPF, RG, CNH, OAB, endereços, telefones, e-mails, contas bancárias, datas de nascimento e outros dados, usando o mesmo motor do [Anonimizador LGPD](https://github.com/n-lobato/anonimizador-lgpd).
3. Abre uma tela de revisão com tudo o que foi encontrado e o trecho onde aparece. Desmarque o que não for dado pessoal, inclua o que faltou e una linhas que forem a mesma pessoa.
4. Ao clicar em **Salvar anonimizado**, os arquivos são gravados com o sufixo `_anonimizado`, e cada dado vira um código: `[PESSOA_1]`, `[CPF_1]`, `[ENDERECO_1]`. A mesma pessoa recebe o mesmo código em todos os arquivos do lote.

Se a revisão for cancelada ou algo der errado na anonimização, **nenhum arquivo é salvo**. Assim não sai, por engano, um Markdown com dados pessoais quando a anonimização foi pedida.

Leve a sério a revisão. Na medição publicada no Anonimizador LGPD, **cerca de 1 em cada 10 nomes passou sem ser detectado** em textos que o programa não conhecia. Além disso:

- trocar nomes e números não basta se o contexto (cargo, local, datas, fatos) ainda permitir saber quem é a pessoa;
- os **nomes dos arquivos** não são alterados. Se o nome do arquivo tiver o nome de alguém, renomeie antes;
- não é gerada tabela de correspondência entre códigos e dados originais. Para isso, ou para anonimizar Word e PDF mantendo o formato original, use o Anonimizador LGPD.

Pela linha de comando, `--anonimizar` faz a troca **sem revisão manual** e mostra um aviso. Use só quando for conferir os arquivos depois.

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
.\.venv\Scripts\python.exe conversor_markdown.py "C:\pasta\origem" --saida="C:\pasta\saida" [--sem-ocr] [--sem-subpastas] [--sobrescrever] [--anonimizar]
```

## Compilar a versão portátil

1. Crie o ambiente como acima e instale também o PyInstaller: `.\.venv\Scripts\python.exe -m pip install pyinstaller`
2. Coloque o Tesseract na pasta `Tesseract-OCR`, na raiz do projeto. Uma forma de fazer isso sem administrador é extrair o instalador da [UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki) com o 7-Zip.
3. Baixe o [`por.traineddata`](https://github.com/tesseract-ocr/tessdata/raw/main/por.traineddata) para `Tesseract-OCR\tessdata`.
4. Rode:

```powershell
powershell -ExecutionPolicy Bypass -File build\build_portatil.ps1 -Versao 1.1.0
```

O `.zip` sai na pasta `dist`. O script leva só as partes do Tesseract usadas pelo OCR e junta os textos de licença de todos os componentes.

### Testes e motor de anonimização

`python -m pytest` roda os testes, que também rodam no GitHub Actions (Windows e Linux) a cada envio.

A pasta `anonimizador/` é uma cópia do motor de detecção do [Anonimizador LGPD](https://github.com/n-lobato/anonimizador-lgpd). Não edite lá: corrija no anonimizador e traga a nova versão com `python build/atualizar_motor.py CAMINHO_DO_ANONIMIZADOR`.

## Licença

Este projeto é software livre sob a **GNU Affero General Public License v3.0** (arquivo [`LICENSE`](LICENSE)). Você pode usar, estudar, modificar e redistribuir, desde que mantenha a mesma licença e disponibilize o código-fonte.

A licença AGPL foi escolhida porque o projeto usa o [PyMuPDF](https://github.com/pymupdf/PyMuPDF), distribuído pela Artifex sob AGPL-3.0 ou licença comercial. Os demais componentes e suas licenças estão em [`THIRD-PARTY-NOTICES.md`](THIRD-PARTY-NOTICES.md).

O motor de anonimização (pasta `anonimizador/`) vem do Anonimizador LGPD, do mesmo autor, sob GPL-3.0, que pode ser combinada com a AGPL-3.0 (seção 13 de ambas as licenças).

## Sobre o uso de inteligência artificial

O desenvolvimento contou com o Claude, assistente de IA da Anthropic, na escrita do código, dos testes e desta documentação. As escolhas sobre como o programa funciona foram feitas pelo autor. O código é aberto para que qualquer pessoa possa conferir o que ele faz.

## Autor

[n-lobato](https://github.com/n-lobato)
