# -*- coding: utf-8 -*-
# Conversor Markdown
# Copyright (C) 2026 n-lobato
#
# Este programa e software livre: voce pode redistribui-lo e/ou modifica-lo
# sob os termos da GNU Affero General Public License, versao 3, publicada pela
# Free Software Foundation. Distribuido SEM QUALQUER GARANTIA. Veja o arquivo
# LICENSE ou <https://www.gnu.org/licenses/agpl-3.0.html>.
# Codigo-fonte: https://github.com/n-lobato/conversor-markdown
"""
Conversor em lote para Markdown (100% local, sem upload).

Formatos: PDF, DOCX, PPTX, XLSX/XLSM, XLS, CSV e imagens (PNG, JPG, TIF, BMP, GIF, WEBP).
OCR (Tesseract) para imagens e para paginas de PDF escaneadas.

Uso:
  Janela:        pythonw conversor_markdown.py
  Linha de cmd:  python conversor_markdown.py ORIGEM [ORIGEM...] --saida=PASTA [--sem-ocr] [--sem-subpastas] [--sobrescrever]
  Arrastar arquivos sobre o icone: abre a janela e ja converte
"""

import csv
import io
import os
import queue
import shutil
import sys
import threading
import time
import traceback
from datetime import datetime
from pathlib import Path

if getattr(sys, "frozen", False):
    # executavel gerado pelo PyInstaller: pasta onde esta o .exe
    APP_DIR = Path(sys.executable).resolve().parent
else:
    APP_DIR = Path(__file__).resolve().parent

VERSAO = "1.0.0"

# no .exe sem console, stdout/stderr nao existem; evita erro de bibliotecas que imprimem
if sys.stdout is None:
    sys.stdout = open(os.devnull, "w", encoding="utf-8")
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w", encoding="utf-8")
TESSDATA_DIR = APP_DIR / "tessdata"

EXT_PDF = {".pdf"}
EXT_WORD = {".docx"}
EXT_PPT = {".pptx"}
EXT_EXCEL = {".xlsx", ".xlsm"}
EXT_XLS = {".xls"}
EXT_CSV = {".csv"}
EXT_IMG = {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp", ".gif", ".webp"}
EXT_ANTIGOS = {".doc", ".ppt"}
SUPORTADAS = EXT_PDF | EXT_WORD | EXT_PPT | EXT_EXCEL | EXT_XLS | EXT_CSV | EXT_IMG


# ----------------------------------------------------------------------------
# OCR
# ----------------------------------------------------------------------------

class OCR:
    def __init__(self):
        self.disponivel = False
        self.idioma = "eng"
        self.config = ""
        self.motivo = ""
        try:
            import pytesseract
        except ImportError:
            self.motivo = "biblioteca pytesseract nao instalada"
            return
        self.pt = pytesseract

        candidatos = [
            APP_DIR / "Tesseract-OCR" / "tesseract.exe",
            Path(os.environ.get("ProgramFiles", r"C:\Program Files")) / "Tesseract-OCR" / "tesseract.exe",
            Path(os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")) / "Tesseract-OCR" / "tesseract.exe",
            Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "Tesseract-OCR" / "tesseract.exe",
        ]
        exe = next((str(c) for c in candidatos if c.is_file()), None) or shutil.which("tesseract")
        if not exe:
            self.motivo = "Tesseract nao encontrado"
            return
        pytesseract.pytesseract.tesseract_cmd = exe

        if (TESSDATA_DIR / "por.traineddata").is_file():
            self.config = f'--tessdata-dir "{TESSDATA_DIR}"'
        try:
            idiomas = set(pytesseract.get_languages(config=self.config))
        except Exception as e:  # noqa: BLE001
            self.motivo = f"erro ao iniciar o Tesseract: {e}"
            return
        escolhidos = [i for i in ("por", "eng") if i in idiomas]
        if not escolhidos:
            self.motivo = "nenhum idioma (por/eng) encontrado no Tesseract"
            return
        self.idioma = "+".join(escolhidos)
        self.disponivel = True

    def ler(self, imagem):
        """imagem: objeto PIL.Image. Retorna texto em paragrafos."""
        from PIL import ImageOps
        img = ImageOps.exif_transpose(imagem)
        if img.mode not in ("RGB", "L"):
            img = img.convert("RGB")
        # imagens pequenas reconhecem melhor ampliadas
        if max(img.size) < 1500:
            fator = 1500 / max(img.size)
            img = img.resize((int(img.width * fator), int(img.height * fator)))
        texto = self.pt.image_to_string(img, lang=self.idioma, config=self.config)
        return limpar_texto_ocr(texto)


def limpar_texto_ocr(texto):
    """Junta linhas quebradas em paragrafos, mantendo paragrafos separados."""
    paragrafos, atual = [], []
    for linha in texto.splitlines():
        linha = linha.strip()
        if not linha:
            if atual:
                paragrafos.append(" ".join(atual))
                atual = []
            continue
        if atual and atual[-1].endswith("-") and not atual[-1].endswith(" -"):
            atual[-1] = atual[-1][:-1] + linha
        else:
            atual.append(linha)
    if atual:
        paragrafos.append(" ".join(atual))
    return "\n\n".join(p for p in paragrafos if p.strip())


# ----------------------------------------------------------------------------
# Utilidades Markdown
# ----------------------------------------------------------------------------

def celula(valor):
    if valor is None:
        return ""
    if isinstance(valor, float) and valor.is_integer():
        valor = int(valor)
    if isinstance(valor, datetime):
        valor = valor.strftime("%d/%m/%Y %H:%M") if (valor.hour or valor.minute) else valor.strftime("%d/%m/%Y")
    s = str(valor).replace("\r", "").replace("\n", "<br>").replace("|", "\\|").strip()
    return s


def tabela_md(linhas):
    """linhas: lista de listas. Primeira linha vira cabecalho."""
    linhas = [[celula(v) for v in l] for l in linhas]
    # remove linhas totalmente vazias
    linhas = [l for l in linhas if any(c for c in l)]
    if not linhas:
        return ""
    n = max(len(l) for l in linhas)
    linhas = [l + [""] * (n - len(l)) for l in linhas]
    # remove colunas totalmente vazias
    cols = [j for j in range(n) if any(l[j] for l in linhas)]
    linhas = [[l[j] for j in cols] for l in linhas]
    if not cols:
        return ""
    cab = linhas[0]
    out = ["| " + " | ".join(c or " " for c in cab) + " |",
           "| " + " | ".join("---" for _ in cab) + " |"]
    for l in linhas[1:]:
        out.append("| " + " | ".join(l) + " |")
    return "\n".join(out)


# ----------------------------------------------------------------------------
# Conversores
# ----------------------------------------------------------------------------

def converter_pdf(caminho, ocr, log):
    import pymupdf
    doc = pymupdf.open(str(caminho))
    if doc.needs_pass:
        raise RuntimeError("PDF protegido por senha")
    total = doc.page_count

    paginas_md = None
    try:
        import pymupdf4llm
        chunks = pymupdf4llm.to_markdown(doc, page_chunks=True, use_ocr=False,
                                         header=False, footer=False, show_progress=False)
        paginas_md = [c.get("text", "") for c in chunks]
        if len(paginas_md) != total:
            paginas_md = None
    except TypeError:
        try:
            import pymupdf4llm
            chunks = pymupdf4llm.to_markdown(doc, page_chunks=True)
            paginas_md = [c.get("text", "") for c in chunks]
        except Exception:  # noqa: BLE001
            paginas_md = None
    except Exception:  # noqa: BLE001
        paginas_md = None

    if paginas_md is None:
        paginas_md = [doc[i].get_text("text") for i in range(total)]

    from PIL import Image
    partes, ocr_feitas, sem_texto = [], 0, 0
    for i in range(total):
        texto = (paginas_md[i] or "").strip()
        if len(texto) < 20:
            if ocr and ocr.disponivel:
                pix = doc[i].get_pixmap(dpi=300)
                img = Image.open(io.BytesIO(pix.tobytes("png")))
                lido = ocr.ler(img)
                if lido:
                    texto = lido
                    ocr_feitas += 1
            elif not texto:
                sem_texto += 1
        if texto:
            partes.append(texto)
    doc.close()

    if ocr_feitas:
        log(f"    OCR aplicado em {ocr_feitas} pagina(s) escaneada(s)")
    if sem_texto:
        log(f"    Aviso: {sem_texto} pagina(s) sem texto digital (ative o OCR para ler)")
    return "\n\n---\n\n".join(partes) + "\n"


def converter_docx(caminho, ocr, log):
    import mammoth
    from markdownify import markdownify

    textos_img = {}

    def tratar_imagem(image):
        n = len(textos_img) + 1
        texto = ""
        if ocr and ocr.disponivel:
            try:
                from PIL import Image
                with image.open() as f:
                    img = Image.open(io.BytesIO(f.read()))
                    img.load()
                if min(img.size) >= 80:
                    texto = ocr.ler(img)
            except Exception:  # noqa: BLE001
                texto = ""
        textos_img[n] = texto
        return {"src": f"imagem-{n}", "alt": ""}

    with open(caminho, "rb") as f:
        resultado = mammoth.convert_to_html(f, convert_image=mammoth.images.img_element(tratar_imagem))
    html = resultado.value
    try:
        md = markdownify(html, heading_style="ATX", bullets="-", strip=["span"], table_infer_header=True)
    except TypeError:
        md = markdownify(html, heading_style="ATX", bullets="-", strip=["span"])

    # substitui as tags de imagem por um marcador legivel
    import re

    def troca(m):
        texto = textos_img.get(int(m.group(1)), "")
        if texto:
            return "\n\n> **[Texto da imagem]**\n>\n> " + texto.replace("\n\n", "\n>\n> ") + "\n\n"
        return "*[imagem]*"

    md = re.sub(r"!\[[^\]]*\]\(imagem-(\d+)\)", troca, md)
    md = re.sub(r"\n{3,}", "\n\n", md).strip()
    return md + "\n"


def _texto_frame(tf):
    linhas = []
    for p in tf.paragraphs:
        t = "".join(r.text for r in p.runs).strip() or p.text.strip()
        if not t:
            continue
        nivel = p.level or 0
        linhas.append(("  " * nivel) + "- " + t)
    return linhas


def _shapes(shapes, ocr, saida, titulo_id):
    from pptx.enum.shapes import MSO_SHAPE_TYPE
    # ordena de cima para baixo, esquerda para direita
    def chave(s):
        return ((s.top or 0) // 100000, s.left or 0)
    for s in sorted(shapes, key=chave):
        if s.shape_id == titulo_id:
            continue
        if s.shape_type == MSO_SHAPE_TYPE.GROUP:
            _shapes(s.shapes, ocr, saida, titulo_id)
            continue
        if getattr(s, "has_table", False) and s.has_table:
            linhas = [[c.text for c in row.cells] for row in s.table.rows]
            t = tabela_md(linhas)
            if t:
                saida.append(t)
            continue
        if getattr(s, "has_text_frame", False) and s.has_text_frame:
            linhas = _texto_frame(s.text_frame)
            if linhas:
                saida.append("\n".join(linhas))
            continue
        if s.shape_type == MSO_SHAPE_TYPE.PICTURE:
            texto = ""
            if ocr and ocr.disponivel:
                try:
                    from PIL import Image
                    img = Image.open(io.BytesIO(s.image.blob))
                    img.load()
                    if min(img.size) >= 80:
                        texto = ocr.ler(img)
                except Exception:  # noqa: BLE001
                    texto = ""
            if texto:
                saida.append("> **[Texto da imagem]**\n>\n> " + texto.replace("\n\n", "\n>\n> "))
            else:
                saida.append("*[imagem]*")


def converter_pptx(caminho, ocr, log):
    from pptx import Presentation
    prs = Presentation(str(caminho))
    partes = []
    for n, slide in enumerate(prs.slides, start=1):
        titulo, titulo_id = "", None
        try:
            if slide.shapes.title is not None and slide.shapes.title.text.strip():
                titulo = slide.shapes.title.text.strip().replace("\n", " ")
                titulo_id = slide.shapes.title.shape_id
        except Exception:  # noqa: BLE001
            pass
        cab = f"## Slide {n}" + (f": {titulo}" if titulo else "")
        corpo = []
        _shapes(slide.shapes, ocr, corpo, titulo_id)
        bloco = [cab] + corpo
        if slide.has_notes_slide:
            notas = slide.notes_slide.notes_text_frame.text.strip() if slide.notes_slide.notes_text_frame else ""
            if notas:
                bloco.append("**Notas do apresentador:**\n\n" + notas)
        partes.append("\n\n".join(bloco))
    return "\n\n".join(partes) + "\n"


def converter_xlsx(caminho, ocr, log):
    import openpyxl
    wb = openpyxl.load_workbook(str(caminho), data_only=True, read_only=True)
    wbf = openpyxl.load_workbook(str(caminho), data_only=False, read_only=True)
    partes = [f"# {caminho.stem}"]
    for ws, wsf in zip(wb.worksheets, wbf.worksheets):
        linhas = []
        for r, rf in zip(ws.iter_rows(values_only=True), wsf.iter_rows(values_only=True)):
            # se a formula nao tem valor salvo, mostra a propria formula
            linhas.append([v if v is not None or not (isinstance(f, str) and f.startswith("="))
                           else f for v, f in zip(r, rf)])
        t = tabela_md(linhas)
        partes.append(f"## Planilha: {ws.title}\n\n" + (t or "*(planilha vazia)*"))
    wb.close()
    wbf.close()
    return "\n\n".join(partes) + "\n"


def converter_xls(caminho, ocr, log):
    import xlrd
    wb = xlrd.open_workbook(str(caminho))
    partes = [f"# {caminho.stem}"]
    for sh in wb.sheets():
        linhas = []
        for r in range(sh.nrows):
            linha = []
            for c in range(sh.ncols):
                cel = sh.cell(r, c)
                v = cel.value
                if cel.ctype == xlrd.XL_CELL_DATE:
                    try:
                        v = xlrd.xldate.xldate_as_datetime(v, wb.datemode)
                    except Exception:  # noqa: BLE001
                        pass
                linha.append(v)
            linhas.append(linha)
        t = tabela_md(linhas)
        partes.append(f"## Planilha: {sh.name}\n\n" + (t or "*(planilha vazia)*"))
    return "\n\n".join(partes) + "\n"


def converter_csv(caminho, ocr, log):
    dados = caminho.read_bytes()
    for enc in ("utf-8-sig", "cp1252", "latin-1"):
        try:
            texto = dados.decode(enc)
            break
        except UnicodeDecodeError:
            continue
    try:
        dialeto = csv.Sniffer().sniff(texto[:5000], delimiters=";,\t|")
    except csv.Error:
        class dialeto(csv.excel):  # noqa: N801
            delimiter = ";" if texto.count(";") > texto.count(",") else ","
    linhas = list(csv.reader(io.StringIO(texto), dialeto))
    return f"# {caminho.stem}\n\n" + (tabela_md(linhas) or "*(arquivo vazio)*") + "\n"


def converter_imagem(caminho, ocr, log):
    if not (ocr and ocr.disponivel):
        raise RuntimeError("imagem precisa de OCR, que esta desativado ou indisponivel")
    from PIL import Image, ImageSequence
    img = Image.open(str(caminho))
    textos = []
    for quadro in ImageSequence.Iterator(img):
        t = ocr.ler(quadro.copy())
        if t:
            textos.append(t)
        if caminho.suffix.lower() not in (".tif", ".tiff"):
            break  # GIF animado: so o primeiro quadro
    corpo = "\n\n---\n\n".join(textos) if textos else "*(nenhum texto reconhecido na imagem)*"
    return f"# {caminho.stem}\n\n{corpo}\n"


CONVERSORES = {}
for _e in EXT_PDF: CONVERSORES[_e] = converter_pdf
for _e in EXT_WORD: CONVERSORES[_e] = converter_docx
for _e in EXT_PPT: CONVERSORES[_e] = converter_pptx
for _e in EXT_EXCEL: CONVERSORES[_e] = converter_xlsx
for _e in EXT_XLS: CONVERSORES[_e] = converter_xls
for _e in EXT_CSV: CONVERSORES[_e] = converter_csv
for _e in EXT_IMG: CONVERSORES[_e] = converter_imagem


# ----------------------------------------------------------------------------
# Lote
# ----------------------------------------------------------------------------

def listar_arquivos(entradas, subpastas=True):
    """entradas: lista de pastas e/ou arquivos. Retorna lista de (arquivo, pasta_base)."""
    achados = []
    for e in entradas:
        e = Path(e)
        if e.is_file():
            achados.append((e, e.parent))
        elif e.is_dir():
            it = e.rglob("*") if subpastas else e.glob("*")
            for f in sorted(it):
                if f.is_file() and not f.name.startswith("~$"):
                    achados.append((f, e))
    return achados


def converter_lote(entradas, pasta_saida, usar_ocr=True, subpastas=True, sobrescrever=False,
                   log=print, progresso=None, cancelar=None):
    pasta_saida = Path(pasta_saida)
    pasta_saida.mkdir(parents=True, exist_ok=True)
    arquivos = listar_arquivos(entradas, subpastas)
    pasta_saida_res = pasta_saida.resolve()
    arquivos = [(f, b) for (f, b) in arquivos if pasta_saida_res not in f.resolve().parents]

    ocr = None
    if usar_ocr:
        ocr = OCR()
        if ocr.disponivel:
            log(f"OCR ativo (idioma: {ocr.idioma})")
        else:
            log(f"Aviso: OCR indisponivel ({ocr.motivo}). Imagens serao ignoradas.")

    validos = [(f, b) for (f, b) in arquivos if f.suffix.lower() in SUPORTADAS]
    antigos = [f for (f, b) in arquivos if f.suffix.lower() in EXT_ANTIGOS]
    log(f"Destino: {pasta_saida}")
    log(f"{len(validos)} arquivo(s) para converter.")
    for f in antigos:
        log(f"  Ignorado (formato antigo, salve como .docx/.pptx): {f.name}")

    usados = set()
    ok = falhas = pulados = 0
    inicio = time.time()
    for idx, (arq, base) in enumerate(validos, start=1):
        if cancelar and cancelar():
            log("Conversao interrompida pelo usuario.")
            break
        if progresso:
            progresso(idx - 1, len(validos), arq.name)
        try:
            rel = arq.relative_to(base).parent
        except ValueError:
            rel = Path()
        destino_dir = pasta_saida / rel
        destino = destino_dir / (arq.stem + ".md")
        if destino in usados:
            destino = destino_dir / f"{arq.stem}_{arq.suffix.lstrip('.').lower()}.md"
        usados.add(destino)

        if destino.exists() and not sobrescrever:
            log(f"[{idx}/{len(validos)}] Pulado (ja existe): {destino.name}")
            pulados += 1
            continue
        log(f"[{idx}/{len(validos)}] {arq.name}")
        try:
            md = CONVERSORES[arq.suffix.lower()](arq, ocr, log)
            destino_dir.mkdir(parents=True, exist_ok=True)
            destino.write_text(md, encoding="utf-8")
            ok += 1
        except Exception as e:  # noqa: BLE001
            falhas += 1
            log(f"    ERRO: {e}")
            with open(pasta_saida / "_erros_conversao.log", "a", encoding="utf-8") as f:
                f.write(f"\n[{datetime.now():%d/%m/%Y %H:%M}] {arq}\n{traceback.format_exc()}\n")

    if progresso:
        progresso(len(validos), len(validos), "")
    dur = time.time() - inicio
    log(f"\nConcluido em {dur:.0f}s: {ok} convertido(s), {pulados} pulado(s), {falhas} com erro.")
    if falhas:
        log(f"Detalhes dos erros em: {pasta_saida / '_erros_conversao.log'}")
    return ok, pulados, falhas


# ----------------------------------------------------------------------------
# Janela
# ----------------------------------------------------------------------------

def saida_sugerida(entradas):
    """Pasta de saida padrao para o que foi escolhido ou arrastado."""
    p = Path(entradas[0])
    if len(entradas) == 1 and p.is_dir():
        return str(p.parent / (p.name + "_markdown"))
    return str(p.parent / "markdown")


def abrir_janela(entradas_iniciais=None):
    import tkinter as tk
    from tkinter import filedialog, messagebox, ttk
    from tkinter.scrolledtext import ScrolledText

    # arrastar e soltar (tkinterdnd2); sem ela a janela funciona normalmente
    try:
        from tkinterdnd2 import DND_FILES, TkinterDnD
        raiz = TkinterDnD.Tk()
        tem_dnd = True
    except Exception:  # noqa: BLE001
        raiz = tk.Tk()
        tem_dnd = False

    raiz.title(f"Conversor Markdown {VERSAO} (local)")
    raiz.geometry("780x620")
    raiz.minsize(660, 520)

    fila = queue.Queue()
    estado = {"rodando": False, "cancelar": False, "arquivos": [], "saida_auto": None}

    entrada_var = tk.StringVar()
    saida_var = tk.StringVar()
    ocr_var = tk.BooleanVar(value=True)
    sub_var = tk.BooleanVar(value=True)
    sobre_var = tk.BooleanVar(value=False)
    auto_var = tk.BooleanVar(value=True)

    frm = ttk.Frame(raiz, padding=12)
    frm.pack(fill="both", expand=True)
    frm.columnconfigure(1, weight=1)

    ttk.Label(frm, text="Converte PDF, Word, PowerPoint, Excel, CSV e imagens em Markdown. "
                        "Tudo roda no seu computador.", foreground="#444").grid(
        row=0, column=0, columnspan=4, sticky="w", pady=(0, 8))

    # area de soltar
    texto_area = ("Arraste arquivos ou pastas para cá" if tem_dnd
                  else "Arrastar e soltar indisponível. Use os botões abaixo.")
    area = tk.Label(frm, text=texto_area, font=("Segoe UI", 12), fg="#335", bg="#eef2f8",
                    relief="groove", bd=2, height=3, cursor="hand2" if tem_dnd else "")
    area.grid(row=1, column=0, columnspan=4, sticky="ew", pady=(0, 10))

    ttk.Label(frm, text="Origem:").grid(row=2, column=0, sticky="w")
    ttk.Entry(frm, textvariable=entrada_var).grid(row=2, column=1, sticky="ew", padx=6)

    def definir_saida_padrao(entradas):
        # so troca a saida se o usuario nao escolheu uma pasta por conta propria
        if not saida_var.get() or saida_var.get() == estado["saida_auto"]:
            sugerida = saida_sugerida(entradas)
            saida_var.set(sugerida)
            estado["saida_auto"] = sugerida

    def carregar(entradas, iniciar=False):
        entradas = [str(Path(e)) for e in entradas if Path(e).exists()]
        if not entradas:
            return
        if estado["rodando"]:
            messagebox.showinfo("Aguarde", "Já existe uma conversão em andamento.")
            return
        estado["arquivos"] = entradas
        if len(entradas) == 1:
            entrada_var.set(entradas[0])
        else:
            entrada_var.set(f"{len(entradas)} itens em {Path(entradas[0]).parent}")
        definir_saida_padrao(entradas)
        if iniciar:
            converter()

    def escolher_pasta_entrada():
        p = filedialog.askdirectory(title="Pasta com os arquivos a converter")
        if p:
            carregar([p])

    def escolher_arquivos_entrada():
        tipos = [("Suportados", " ".join("*" + e for e in sorted(SUPORTADAS))), ("Todos", "*.*")]
        ps = filedialog.askopenfilenames(title="Arquivos a converter", filetypes=tipos)
        if ps:
            carregar(list(ps))

    ttk.Button(frm, text="Pasta...", command=escolher_pasta_entrada).grid(row=2, column=2)
    ttk.Button(frm, text="Arquivos...", command=escolher_arquivos_entrada).grid(row=2, column=3, padx=(4, 0))

    ttk.Label(frm, text="Salvar em:").grid(row=3, column=0, sticky="w", pady=(8, 0))
    ttk.Entry(frm, textvariable=saida_var).grid(row=3, column=1, sticky="ew", padx=6, pady=(8, 0))

    def escolher_saida():
        p = filedialog.askdirectory(title="Pasta onde salvar os arquivos .md")
        if p:
            saida_var.set(p)
            estado["saida_auto"] = None

    ttk.Button(frm, text="Pasta...", command=escolher_saida).grid(row=3, column=2, pady=(8, 0))

    opc = ttk.Frame(frm)
    opc.grid(row=4, column=0, columnspan=4, sticky="w", pady=(10, 2))
    ttk.Checkbutton(opc, text="Usar OCR (imagens e PDFs escaneados)", variable=ocr_var).pack(side="left")
    ttk.Checkbutton(opc, text="Incluir subpastas", variable=sub_var).pack(side="left", padx=14)
    ttk.Checkbutton(opc, text="Sobrescrever .md existentes", variable=sobre_var).pack(side="left")
    opc2 = ttk.Frame(frm)
    opc2.grid(row=5, column=0, columnspan=4, sticky="w", pady=(0, 10))
    if tem_dnd:
        ttk.Checkbutton(opc2, text="Converter automaticamente ao soltar arquivos",
                        variable=auto_var).pack(side="left")

    barra = ttk.Progressbar(frm, mode="determinate")
    barra.grid(row=6, column=0, columnspan=4, sticky="ew")
    status = ttk.Label(frm, text="Pronto.")
    status.grid(row=7, column=0, columnspan=4, sticky="w", pady=(4, 6))

    caixa = ScrolledText(frm, height=12, font=("Consolas", 9), state="disabled")
    caixa.grid(row=8, column=0, columnspan=4, sticky="nsew")
    frm.rowconfigure(8, weight=1)

    botoes = ttk.Frame(frm)
    botoes.grid(row=9, column=0, columnspan=4, sticky="e", pady=(10, 0))

    def abrir_saida():
        p = saida_var.get()
        if p and Path(p).exists():
            os.startfile(p)

    ttk.Button(botoes, text="Abrir pasta de saida", command=abrir_saida).pack(side="left", padx=4)
    btn_cancelar = ttk.Button(botoes, text="Cancelar", state="disabled",
                              command=lambda: estado.update(cancelar=True))
    btn_cancelar.pack(side="left", padx=4)
    btn_converter = ttk.Button(botoes, text="Converter")
    btn_converter.pack(side="left", padx=4)

    def escrever(msg):
        caixa.configure(state="normal")
        caixa.insert("end", msg + "\n")
        caixa.see("end")
        caixa.configure(state="disabled")

    def processar_fila():
        try:
            while True:
                tipo, dado = fila.get_nowait()
                if tipo == "log":
                    escrever(dado)
                elif tipo == "prog":
                    feito, total, nome = dado
                    barra["maximum"] = max(total, 1)
                    barra["value"] = feito
                    status.configure(text=f"{feito}/{total}  {nome}" if nome else f"{feito}/{total}")
                elif tipo == "fim":
                    estado["rodando"] = False
                    btn_converter.configure(state="normal")
                    btn_cancelar.configure(state="disabled")
                    ok, pul, fal = dado
                    status.configure(text=f"Concluido: {ok} convertido(s), {pul} pulado(s), {fal} com erro.")
        except queue.Empty:
            pass
        raiz.after(100, processar_fila)

    def converter():
        if estado["rodando"]:
            return
        entradas = estado["arquivos"] or ([entrada_var.get()] if entrada_var.get() else [])
        if not entradas or not all(Path(e).exists() for e in entradas):
            messagebox.showwarning("Atencao", "Escolha uma pasta ou arquivos de origem validos.")
            return
        if not saida_var.get():
            messagebox.showwarning("Atencao", "Escolha a pasta onde salvar os arquivos .md.")
            return
        estado.update(rodando=True, cancelar=False)
        btn_converter.configure(state="disabled")
        btn_cancelar.configure(state="normal")
        caixa.configure(state="normal")
        caixa.delete("1.0", "end")
        caixa.configure(state="disabled")

        def tarefa():
            try:
                r = converter_lote(
                    entradas, saida_var.get(), usar_ocr=ocr_var.get(), subpastas=sub_var.get(),
                    sobrescrever=sobre_var.get(),
                    log=lambda m: fila.put(("log", m)),
                    progresso=lambda a, b, c: fila.put(("prog", (a, b, c))),
                    cancelar=lambda: estado["cancelar"])
            except Exception as e:  # noqa: BLE001
                fila.put(("log", f"ERRO GERAL: {e}"))
                r = (0, 0, 0)
            fila.put(("fim", r))

        threading.Thread(target=tarefa, daemon=True).start()

    btn_converter.configure(command=converter)

    if tem_dnd:
        cor_normal, cor_destaque = "#eef2f8", "#d6e6ff"

        def ao_soltar(evento):
            area.configure(bg=cor_normal)
            caminhos = list(raiz.tk.splitlist(evento.data))
            carregar(caminhos, iniciar=auto_var.get())
            return evento.action

        def ao_entrar(evento):
            area.configure(bg=cor_destaque)
            return evento.action

        def ao_sair(evento):
            area.configure(bg=cor_normal)
            return evento.action

        # aceita soltar em qualquer ponto da janela
        for alvo in (raiz, area):
            alvo.drop_target_register(DND_FILES)
            alvo.dnd_bind("<<Drop>>", ao_soltar)
            alvo.dnd_bind("<<DropEnter>>", ao_entrar)
            alvo.dnd_bind("<<DropLeave>>", ao_sair)

    raiz.after(100, processar_fila)
    if entradas_iniciais:
        # arquivos arrastados sobre o icone do programa
        raiz.after(300, lambda: carregar(entradas_iniciais, iniciar=True))
    raiz.mainloop()


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    flags = [a for a in sys.argv[1:] if a.startswith("--")]
    saida = next((f.split("=", 1)[1] for f in flags if f.startswith("--saida=")), None)
    if saida:
        # modo linha de comando: conversor ORIGEM [ORIGEM...] --saida=PASTA
        _, _, falhas = converter_lote(args, saida, usar_ocr="--sem-ocr" not in flags,
                                      subpastas="--sem-subpastas" not in flags,
                                      sobrescrever="--sobrescrever" in flags)
        sys.exit(1 if falhas else 0)
    # sem --saida: abre a janela; arquivos passados (ex.: arrastados no icone) ja sao carregados
    abrir_janela([a for a in args if Path(a).exists()])


if __name__ == "__main__":
    main()
