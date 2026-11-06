"""Testes da conversão de cada formato. Os arquivos são criados durante o teste."""

import sys
from datetime import datetime
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

import conversor_markdown as cm  # noqa: E402


def _log():
    linhas = []
    return linhas, linhas.append


@pytest.fixture(scope="module")
def ocr():
    o = cm.OCR()
    if not o.disponivel:
        pytest.skip(f"OCR indisponível: {o.motivo}")
    return o


def _fonte(tamanho=40):
    from PIL import ImageFont
    for nome in ("arial.ttf", "DejaVuSans.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                 "LiberationSans-Regular.ttf"):
        try:
            return ImageFont.truetype(nome, tamanho)
        except OSError:
            continue
    pytest.skip("nenhuma fonte TrueType para desenhar a imagem de teste")


def _imagem_com_texto(caminho, linhas):
    from PIL import Image, ImageDraw
    img = Image.new("RGB", (1400, 140 + 80 * len(linhas)), "white")
    d = ImageDraw.Draw(img)
    fonte = _fonte()
    for i, linha in enumerate(linhas):
        d.text((60, 60 + 80 * i), linha, fill="black", font=fonte)
    img.save(caminho)
    return caminho


# ------------------------------------------------------------------ Word
def test_docx_titulos_negrito_listas_e_tabela(tmp_path):
    docx = pytest.importorskip("docx")
    pytest.importorskip("mammoth")
    d = docx.Document()
    d.add_heading("Relatório Anual", level=1)
    p = d.add_paragraph("Texto com ")
    p.add_run("destaque").bold = True
    p.add_run(" no meio.")
    d.add_paragraph("Primeiro item", style="List Bullet")
    d.add_paragraph("Segundo item", style="List Bullet")
    t = d.add_table(rows=2, cols=2)
    t.cell(0, 0).text, t.cell(0, 1).text = "Coluna A", "Coluna B"
    t.cell(1, 0).text, t.cell(1, 1).text = "Ação", "100"
    f = tmp_path / "relatorio.docx"
    d.save(f)

    md = cm.converter_docx(f, None, print)
    assert "# Relatório Anual" in md
    assert "**destaque**" in md
    assert "- Primeiro item" in md and "- Segundo item" in md
    assert "| Coluna A | Coluna B |" in md and "| Ação | 100 |" in md


# ------------------------------------------------------------------ PowerPoint
def test_pptx_titulo_topicos_tabela_e_notas(tmp_path):
    pptx = pytest.importorskip("pptx")
    from pptx.util import Inches
    prs = pptx.Presentation()
    s1 = prs.slides.add_slide(prs.slide_layouts[1])
    s1.shapes.title.text = "Resultados"
    corpo = s1.placeholders[1].text_frame
    corpo.text = "Primeiro ponto"
    sub = corpo.add_paragraph()
    sub.text, sub.level = "Detalhe do ponto", 1
    s1.notes_slide.notes_text_frame.text = "Lembrar de citar a fonte."
    s2 = prs.slides.add_slide(prs.slide_layouts[5])
    s2.shapes.title.text = "Tabela"
    tab = s2.shapes.add_table(2, 2, Inches(1), Inches(2), Inches(6), Inches(1)).table
    tab.cell(0, 0).text, tab.cell(0, 1).text = "Ano", "Total"
    tab.cell(1, 0).text, tab.cell(1, 1).text = "2026", "42"
    f = tmp_path / "apresentacao.pptx"
    prs.save(f)

    md = cm.converter_pptx(f, None, print)
    assert "## Slide 1: Resultados" in md and "## Slide 2: Tabela" in md
    assert "- Primeiro ponto" in md and "  - Detalhe do ponto" in md
    assert "Notas do apresentador" in md and "Lembrar de citar a fonte." in md
    assert "| Ano | Total |" in md and "| 2026 | 42 |" in md


# ------------------------------------------------------------------ Excel
def test_xlsx_varias_planilhas_numeros_datas_e_formula(tmp_path):
    openpyxl = pytest.importorskip("openpyxl")
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Dados"
    ws.append(["Item", "Quantidade", "Data", "Dobro"])
    ws.append(["Caneta | azul", 100.0, datetime(2026, 11, 5), "=B2*2"])
    wb.create_sheet("Vazia")
    f = tmp_path / "planilha.xlsx"
    wb.save(f)

    md = cm.converter_xlsx(f, None, print)
    assert "## Planilha: Dados" in md and "## Planilha: Vazia" in md
    assert "| Item | Quantidade | Data | Dobro |" in md
    assert "| Caneta \\| azul | 100 | 05/11/2026 | =B2*2 |" in md  # sem valor salvo, mostra a fórmula
    assert "*(planilha vazia)*" in md


# ------------------------------------------------------------------ CSV
def test_csv_em_cp1252_com_ponto_e_virgula(tmp_path):
    f = tmp_path / "lista.csv"
    f.write_bytes("Município;Situação\nBrasília;Ação concluída\n".encode("cp1252"))
    md = cm.converter_csv(f, None, print)
    assert "# lista" in md
    assert "| Município | Situação |" in md and "| Brasília | Ação concluída |" in md


# ------------------------------------------------------------------ PDF
def _pdf_com_texto_e_pagina_escaneada(caminho, img_escaneada=None):
    pymupdf = pytest.importorskip("pymupdf")
    doc = pymupdf.open()
    p = doc.new_page()
    p.insert_text((72, 72), "Ata da reunião ordinária de novembro", fontsize=14)
    p.insert_text((72, 110), "Foram aprovadas as contas do exercício anterior.", fontsize=11)
    if img_escaneada:
        p2 = doc.new_page()
        p2.insert_image(p2.rect, filename=str(img_escaneada))
    doc.save(caminho)
    return caminho


def test_pdf_com_texto(tmp_path):
    f = _pdf_com_texto_e_pagina_escaneada(tmp_path / "ata.pdf")
    md = cm.converter_pdf(f, None, print)
    assert "reunião ordinária" in md and "aprovadas as contas" in md


def test_pdf_pagina_escaneada_sem_ocr_avisa(tmp_path):
    img = _imagem_com_texto(tmp_path / "scan.png", ["Certidão de casamento"])
    f = _pdf_com_texto_e_pagina_escaneada(tmp_path / "misto.pdf", img)
    linhas, log = _log()
    md = cm.converter_pdf(f, None, log)
    assert "reunião ordinária" in md
    assert any("sem texto digital" in l for l in linhas)


def test_pdf_pagina_escaneada_com_ocr(tmp_path, ocr):
    img = _imagem_com_texto(tmp_path / "scan.png", ["Certidão de casamento", "Livro 12 folha 34"])
    f = _pdf_com_texto_e_pagina_escaneada(tmp_path / "misto.pdf", img)
    linhas, log = _log()
    md = cm.converter_pdf(f, ocr, log)
    assert "reunião ordinária" in md
    assert "Certidão de casamento" in md and "folha 34" in md
    assert any("OCR aplicado em 1" in l for l in linhas)


# ------------------------------------------------------------------ imagem
def test_imagem_com_ocr(tmp_path, ocr):
    f = _imagem_com_texto(tmp_path / "aviso.png", ["Aviso importante", "Reunião às 14h na sala 3"])
    md = cm.converter_imagem(f, ocr, print)
    assert md.startswith("# aviso")
    assert "Aviso importante" in md and "sala 3" in md


def test_imagem_sem_ocr_da_erro_claro(tmp_path):
    pytest.importorskip("PIL")
    f = _imagem_com_texto(tmp_path / "aviso.png", ["Teste"])
    with pytest.raises(RuntimeError, match="OCR"):
        cm.converter_imagem(f, None, print)


# ------------------------------------------------------------------ lote
def test_lote_continua_depois_de_um_erro_e_mantem_subpastas(tmp_path):
    origem = tmp_path / "origem"
    (origem / "sub").mkdir(parents=True)
    (origem / "sub" / "lista.csv").write_text("A;B\n1;2\n", encoding="utf-8")
    (origem / "quebrado.xlsx").write_bytes(b"isto nao e uma planilha")
    (origem / "antigo.doc").write_bytes(b"x")
    (origem / "~$temporario.csv").write_text("x", encoding="utf-8")
    saida = tmp_path / "saida"
    linhas, log = _log()
    ok, pulados, falhas = cm.converter_lote([origem], saida, usar_ocr=False, log=log)
    assert (ok, pulados, falhas) == (1, 0, 1)
    assert (saida / "sub" / "lista.md").exists()
    assert (saida / "_erros_conversao.log").exists()
    assert any("antigo.doc" in l and "formato antigo" in l for l in linhas)
    assert not (saida / "~$temporario.md").exists()

    # segunda vez: o que já existe é pulado, a menos que se peça para sobrescrever
    ok, pulados, _ = cm.converter_lote([origem], saida, usar_ocr=False, log=log)
    assert (ok, pulados) == (0, 1)
    ok, pulados, _ = cm.converter_lote([origem], saida, usar_ocr=False, log=log, sobrescrever=True)
    assert (ok, pulados) == (1, 0)


def test_mesmo_nome_com_extensoes_diferentes_nao_se_sobrescrevem(tmp_path):
    openpyxl = pytest.importorskip("openpyxl")
    origem = tmp_path / "origem"
    origem.mkdir()
    (origem / "dados.csv").write_text("A;B\n1;2\n", encoding="utf-8")
    wb = openpyxl.Workbook()
    wb.active.append(["X", "Y"])
    wb.save(origem / "dados.xlsx")
    saida = tmp_path / "saida"
    ok, _, falhas = cm.converter_lote([origem], saida, usar_ocr=False, log=lambda m: None)
    assert (ok, falhas) == (2, 0)
    assert sorted(p.name for p in saida.glob("*.md")) == ["dados.md", "dados_xlsx.md"]


# ------------------------------------------------------------------ cabeçalhos repetidos
def test_remove_so_cabecalhos_e_rodapes_que_se_repetem():
    paginas = [
        f"TRIBUNAL DE JUSTIÇA DO DISTRITO FEDERAL\nProcesso 0701234-93\n\n{corpo}\n\nPágina {n} de 4"
        for n, corpo in enumerate(["# SENTENÇA\n\nRelatório do caso.", "Fundamentação longa.",
                                   "Mais fundamentação.", "Dispositivo. Publique-se."], start=1)]
    saida = cm.remover_cabecalhos_repetidos(paginas)
    assert saida[0].startswith("# SENTENÇA")
    assert all("TRIBUNAL DE JUSTIÇA" not in p and "Página" not in p for p in saida)
    assert "Dispositivo. Publique-se." in saida[3]


def test_documento_curto_fica_intacto():
    paginas = ["ATA DA REUNIÃO\n\nTexto.", "ATA DA REUNIÃO\n\nMais texto."]
    assert cm.remover_cabecalhos_repetidos(paginas) == paginas


def test_linha_repetida_no_meio_da_pagina_nao_e_removida():
    paginas = [f"Título {n}\n\nL1\nL2\nL3\nL4\nItem aprovado por unanimidade.\nL5\nL6\nL7\nL8\nFim {n}"
               for n in range(1, 6)]
    saida = cm.remover_cabecalhos_repetidos(paginas)
    assert all("Item aprovado por unanimidade." in p for p in saida)


def test_pdf_mantem_o_titulo_no_topo_da_pagina(tmp_path):
    pymupdf = pytest.importorskip("pymupdf")
    doc = pymupdf.open()
    for n in range(1, 5):
        p = doc.new_page()
        p.insert_text((72, 40), "TRIBUNAL DE JUSTIÇA DO DISTRITO FEDERAL", fontsize=9)
        if n == 1:
            p.insert_text((72, 72), "EXCELENTÍSSIMO SENHOR JUIZ DE DIREITO", fontsize=14)
        corpo = ["Dos fatos narrados pela autora.", "Do direito aplicável ao caso.",
                 "Da tutela de urgência requerida.", "Dos pedidos finais e do valor da causa."][n - 1]
        p.insert_text((72, 200), corpo, fontsize=11)
        p.insert_text((72, 810), f"Página {n} de 4", fontsize=9)
    f = tmp_path / "peticao.pdf"
    doc.save(f)
    md = cm.converter_pdf(f, None, print)
    assert "EXCELENTÍSSIMO SENHOR JUIZ DE DIREITO" in md
    assert "Dos fatos narrados pela autora." in md and "Dos pedidos finais e do valor da causa." in md
    assert "TRIBUNAL DE JUSTIÇA" not in md and "de 4" not in md
