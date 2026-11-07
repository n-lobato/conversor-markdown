# Conversor Markdown

## Baixar

| Sistema | Arquivo |
| --- | --- |
| **Windows 10 e 11** (recomendado) | [Instalador](https://github.com/n-lobato/conversor-markdown/releases/latest/download/Conversor-Markdown-v1.3.0-windows-x64-instalador.exe) |
| Windows, versão portátil (pen drive) | [.zip](https://github.com/n-lobato/conversor-markdown/releases/latest/download/Conversor-Markdown-v1.3.0-windows-x64.zip) |
| **Mac** com chip Apple (M1 ou mais novo) | [.dmg](https://github.com/n-lobato/conversor-markdown/releases/latest/download/Conversor-Markdown-v1.3.0-mac-apple-silicon.dmg) |
| **Linux** Ubuntu, Debian, Mint | [.deb](https://github.com/n-lobato/conversor-markdown/releases/latest/download/conversor-markdown_1.3.0_amd64.deb) |
| Outras distribuições Linux | [.tar.gz](https://github.com/n-lobato/conversor-markdown/releases/latest/download/Conversor-Markdown-v1.3.0-linux-x64.tar.gz) |

Todos os arquivos também estão na página de [Releases](https://github.com/n-lobato/conversor-markdown/releases/latest). Como instalar em cada sistema está na seção [Instalar](#instalar).

> **Atenção:** não use o botão verde **Code > Download ZIP**. Ele baixa só o código-fonte, que não roda sem Python instalado.

Programa para Windows, Mac e Linux que converte PDF, Word, PowerPoint, Excel, CSV e imagens em Markdown, em lote, **sem enviar nada para a internet**. Tudo roda no próprio computador, inclusive o OCR.

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
- **Anonimização (vem ligada):** troca nomes, CPF, endereços e outros dados pessoais por códigos antes de salvar, com uma tela de revisão. Veja abaixo.

## Instalar

### Windows

**Instalador (recomendado).** Baixe o `Conversor-Markdown-v1.3.0-windows-x64-instalador.exe` e abra. Ele instala só para o seu usuário, sem pedir senha de administrador, cria o atalho no menu Iniciar (e, se quiser, na Área de Trabalho) e aparece em **Configurações > Aplicativos > Aplicativos instalados**. É por lá que se desinstala. Para atualizar, basta rodar o instalador da versão nova.

**Versão portátil.** Baixe o `.zip`, clique com o botão direito em **Extrair tudo** e abra `Conversor Markdown.exe` dentro da pasta extraída. Não instala nada, então serve para levar num pen drive. Para remover, apague a pasta.

Funciona no Windows 10 e 11 (64 bits), com o OCR já incluído. Na primeira vez, o Windows pode mostrar o aviso "O Windows protegeu o computador", porque o programa não tem assinatura digital comercial. Clique em **Mais informações** e depois em **Executar assim mesmo**.

### Mac

Para Macs com chip Apple (M1, M2, M3, M4 ou mais novos), com o OCR já incluído. Abra o `.dmg` e arraste **Conversor Markdown** para a pasta **Aplicativos**.

O programa não tem certificado pago da Apple, então o Mac bloqueia a primeira abertura. No macOS 15 (Sequoia) ou mais novo: tente abrir uma vez, depois vá em **Ajustes do Sistema > Privacidade e Segurança**, role até o fim e clique em **Abrir Mesmo Assim**. No macOS 14 ou anterior: clique com o botão direito no programa, escolha **Abrir** e confirme. Depois disso o Mac não pergunta mais.

Para desinstalar, arraste o programa da pasta Aplicativos para o Lixo.

Macs com processador Intel ainda não têm pacote pronto. Neles, dá para rodar a partir do código (veja abaixo).

### Linux

**Ubuntu, Debian, Mint e derivados:** baixe o `.deb` e rode `sudo apt install ./conversor-markdown_1.3.0_amd64.deb`. O Tesseract (OCR) em português é instalado junto. O programa aparece no menu de aplicativos. Para remover: `sudo apt remove conversor-markdown`.

**Outras distribuições:** extraia o `.tar.gz` e rode `./instalar.sh` dentro da pasta. Ele instala só para o seu usuário, sem sudo, e cria o atalho no menu. Para remover, `./desinstalar.sh`. Para o OCR, instale o Tesseract com português pelo gerenciador de pacotes da distribuição.

Para computadores de 64 bits (x86-64).

### Conferir se o arquivo é o original

Os pacotes são gerados e testados pelo GitHub Actions a partir do código deste repositório, e não no computador do autor. Cada arquivo publicado vem acompanhado de um `.sha256` com a impressão digital dele, que também aparece nas notas da versão. Para conferir:

- Windows (PowerShell): `Get-FileHash .\NOME_DO_ARQUIVO -Algorithm SHA256`
- Mac: `shasum -a 256 NOME_DO_ARQUIVO`
- Linux: `sha256sum NOME_DO_ARQUIVO`

O código mostrado deve ser igual ao publicado. Se for diferente, não use o arquivo.

## Como usar

**Jeito rápido:** arraste arquivos ou pastas para dentro da janela. Se você não escolher onde salvar, os `.md` vão para uma pasta `markdown` ao lado dos originais.

**Pelos botões:** escolha a origem (pasta ou arquivos), a pasta de saída e clique em **Converter**.

Opções:

- **Usar OCR:** lê texto de imagens e PDFs escaneados. Deixa a conversão mais lenta.
- **Incluir subpastas.**
- **Sobrescrever .md existentes:** se desmarcado, arquivos já convertidos são pulados.
- **Converter automaticamente ao soltar arquivos.**
- **Anonimizar dados pessoais:** vem marcada. Veja a seção seguinte.

O programa lembra essas escolhas para a próxima vez, menos "Sobrescrever", que sempre volta desmarcada para evitar que um arquivo seja trocado sem querer. Só as caixas de marcar são guardadas, nunca pastas ou nomes de arquivos. Elas ficam em `%APPDATA%\Conversor Markdown` no Windows, em `~/Library/Application Support/Conversor Markdown` no Mac e em `~/.config/conversor-markdown` no Linux.

## Anonimizar antes de usar com IA

Converter no próprio computador evita o upload do arquivo original, mas o Markdown gerado continuaria com todos os dados pessoais. Se ele for colado numa ferramenta de IA na nuvem, o problema volta. Por isso a opção **Anonimizar dados pessoais (com revisão antes de salvar)** vem marcada a partir da versão 1.2.0. Quem desmarcar recebe um aviso no registro da conversão, e a escolha fica lembrada.

Com ela marcada:

1. Os arquivos são convertidos, mas **nada é gravado ainda**.
2. O programa procura nomes, CPF, RG, CNH, OAB, endereços, telefones, e-mails, contas bancárias, datas de nascimento e outros dados, usando o mesmo motor do [Anonimizador LGPD](https://github.com/n-lobato/anonimizador-lgpd).
3. Abre uma tela de revisão com tudo o que foi encontrado e o trecho onde aparece. Desmarque o que não for dado pessoal, inclua o que faltou e una linhas que forem a mesma pessoa.
4. Ao clicar em **Salvar anonimizado**, os arquivos são gravados com o sufixo `_anonimizado`, e cada dado vira um código: `[PESSOA_1]`, `[CPF_1]`, `[ENDERECO_1]`. A mesma pessoa recebe o mesmo código em todos os arquivos do lote.

Se a revisão for cancelada ou algo der errado na anonimização, **nenhum arquivo é salvo**. Assim não sai, por engano, um Markdown com dados pessoais quando a anonimização foi pedida.

**Por que anonimizar o texto convertido, e não o arquivo original?** Porque é o texto convertido que vai parar no Markdown, inclusive o que o OCR leu em imagens, prints, carimbos e assinaturas dentro de Word e PowerPoint. Se o original fosse anonimizado primeiro, esse conteúdo de imagem passaria direto, e formatos como PowerPoint e `.xls` ficariam de fora. E o Markdown não é gravado no disco antes da hora: a conversão fica na memória até a revisão terminar.

Leve a sério a revisão. Na medição publicada no Anonimizador LGPD, **cerca de 1 em cada 10 nomes passou sem ser detectado** em textos que o programa não conhecia. Além disso:

- trocar nomes e números não basta se o contexto (cargo, local, datas, fatos) ainda permitir saber quem é a pessoa;
- os **nomes dos arquivos** não são alterados. Se o nome do arquivo tiver o nome de alguém, renomeie antes;
- não é gerada tabela de correspondência entre códigos e dados originais. Para isso, ou para anonimizar Word e PDF mantendo o formato original, use o Anonimizador LGPD.

Pela linha de comando, a anonimização continua desligada se não for pedida: `--anonimizar` faz a troca **sem revisão manual** e mostra um aviso. Use só quando for conferir os arquivos depois.

## Limitações

- Arquivos antigos `.doc` e `.ppt` não são convertidos. Salve como `.docx` ou `.pptx` antes.
- PDFs protegidos por senha não são convertidos.
- Em planilhas, fórmulas mostram o valor salvo pelo Excel. Se o arquivo nunca foi aberto no Excel, aparece a fórmula.
- O resultado do OCR depende da qualidade da imagem. Revise textos importantes.

## Rodar a partir do código

Requer Python 3.10 ou mais recente (com Tkinter) e o Tesseract para o OCR. Funciona em Windows, Mac (inclusive Intel) e Linux.

Windows:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\pythonw.exe conversor_markdown.py
```

Mac e Linux:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python conversor_markdown.py
```

Tesseract: no Windows, o [instalador da UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki) ou a pasta `Tesseract-OCR` ao lado do script; no Mac, `brew install tesseract tesseract-lang`; no Ubuntu/Debian, `sudo apt install tesseract-ocr tesseract-ocr-por`.

Também funciona pela linha de comando:

```
python conversor_markdown.py ORIGEM [ORIGEM...] --saida=PASTA [--sem-ocr] [--sem-subpastas] [--sobrescrever] [--anonimizar]
```

## Gerar os pacotes

Os pacotes publicados em Releases são gerados e testados pelo GitHub Actions (`.github/workflows/versao.yml`), um sistema por vez. Para publicar uma versão nova: altere `VERSAO` em `conversor_markdown.py` e os links da seção Baixar, envie para o ramo `main` e rode o fluxo **Pacotes (Windows, Mac e Linux)** em Actions, marcando **publicar**.

Para gerar no próprio computador (sempre com o ambiente criado acima e `pip install -r requirements-dev.txt`):

- **Windows** (`.zip` e instalador): coloque o Tesseract na pasta `Tesseract-OCR`, na raiz do projeto, com o [`por.traineddata`](https://github.com/tesseract-ocr/tessdata/raw/main/por.traineddata) em `Tesseract-OCR\tessdata`. Instale o [Inno Setup 6](https://jrsoftware.org/isinfo.php) e rode `powershell -ExecutionPolicy Bypass -File build\build_portatil.ps1 -Versao 1.3.0`. Sem o Inno Setup, acrescente `-SemInstalador`.
- **Mac** (`.dmg`): `brew install tesseract dylibbundler` e depois `bash build/build_mac.sh 1.3.0`. O Tesseract e as bibliotecas dele vão para dentro do aplicativo.
- **Linux** (`.deb` e `.tar.gz`): `bash build/build_linux.sh 1.3.0`. O OCR usa o Tesseract do sistema.

Tudo sai na pasta `dist`. `python build/testar_pacote.py CAMINHO_DO_EXECUTAVEL` testa um pacote pronto (conversão, OCR e anonimização).

### Testes e motor de anonimização

`python -m pytest` roda os testes, que também rodam no GitHub Actions (Windows, Mac e Linux) a cada envio.

A pasta `anonimizador/` é uma cópia do motor de detecção do [Anonimizador LGPD](https://github.com/n-lobato/anonimizador-lgpd). Não edite lá: corrija no anonimizador e traga a nova versão com `python build/atualizar_motor.py CAMINHO_DO_ANONIMIZADOR`.

## Licença

Este projeto é software livre sob a **GNU Affero General Public License v3.0** (arquivo [`LICENSE`](LICENSE)). Você pode usar, estudar, modificar e redistribuir, desde que mantenha a mesma licença e disponibilize o código-fonte.

A licença AGPL foi escolhida porque o projeto usa o [PyMuPDF](https://github.com/pymupdf/PyMuPDF), distribuído pela Artifex sob AGPL-3.0 ou licença comercial. Os demais componentes e suas licenças estão em [`THIRD-PARTY-NOTICES.md`](THIRD-PARTY-NOTICES.md).

O motor de anonimização (pasta `anonimizador/`) vem do Anonimizador LGPD, do mesmo autor, sob GPL-3.0, que pode ser combinada com a AGPL-3.0 (seção 13 de ambas as licenças).

## Sobre o uso de inteligência artificial

O desenvolvimento contou com o Claude, assistente de IA da Anthropic, na escrita do código, dos testes e desta documentação. As escolhas sobre como o programa funciona foram feitas pelo autor. O código é aberto para que qualquer pessoa possa conferir o que ele faz.

## Autor

[n-lobato](https://github.com/n-lobato)
