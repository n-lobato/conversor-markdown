import os
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

import conversor_markdown as cm  # noqa: E402
from anonimizacao import Anonimizacao  # noqa: E402

CSV = (
    "Nome;CPF;Telefone;Observação\n"
    "Maria Aparecida de Souza;529.982.247-25;(61) 99876-5432;Requerente, residente na SQS 308, Bloco C, Apto 101\n"
    "José Carlos da Silva Filho;083.016.613-05;(61) 98412-3377;Testemunha: Kauã Ribeiro\n"
)


def _lote(tmp_path, **kw):
    origem = tmp_path / "origem"
    origem.mkdir()
    (origem / "lista.csv").write_text(CSV, encoding="utf-8")
    saida = tmp_path / "saida"
    logs = []
    r = cm.converter_lote([origem], saida, usar_ocr=False, log=logs.append, **kw)
    return saida, r, "\n".join(logs)


def test_sem_anonimizar_mantem_o_comportamento(tmp_path):
    saida, (ok, _, falhas), _ = _lote(tmp_path)
    assert (ok, falhas) == (1, 0)
    texto = (saida / "lista.md").read_text(encoding="utf-8")
    assert "Maria Aparecida" in texto and "529.982.247-25" in texto


def test_anonimiza_depois_da_revisao(tmp_path):
    vistos = []

    def revisar(anon):
        vistos.extend(e.rotulo for e in anon.entidades())
        return True

    saida, (ok, _, falhas), log = _lote(tmp_path, anonimizar=True, revisar=revisar)
    assert (ok, falhas) == (1, 0)
    assert not (saida / "lista.md").exists()
    texto = (saida / "lista_anonimizado.md").read_text(encoding="utf-8")
    for dado in ("Maria", "Souza", "529.982", "99876", "José Carlos", "Kauã", "SQS 308"):
        assert dado not in texto, dado
    assert "[PESSOA_1]" in texto and "[CPF_1]" in texto and "|" in texto  # tabela continua tabela
    assert any("Maria" in v for v in vistos)
    assert "Pessoa" in log or "Nome de pessoa" in log


def test_revisao_cancelada_nao_grava_nada(tmp_path):
    saida, (ok, _, _), log = _lote(tmp_path, anonimizar=True, revisar=lambda anon: False)
    assert ok == 0
    assert not list(saida.rglob("*.md"))
    assert "nenhum arquivo foi salvo" in log


def test_item_desmarcado_na_revisao_fica_no_texto(tmp_path):
    def revisar(anon):
        for e in anon.entidades():
            if e.tipo == "TELEFONE":
                e.ativo = False
        return True

    saida, _, _ = _lote(tmp_path, anonimizar=True, revisar=revisar)
    texto = (saida / "lista_anonimizado.md").read_text(encoding="utf-8")
    assert "(61) 99876-5432" in texto and "529.982" not in texto


def test_erro_na_anonimizacao_nao_grava_texto_original(tmp_path, monkeypatch):
    def falha(self, texto):
        raise RuntimeError("falha simulada")

    monkeypatch.setattr(Anonimizacao, "aplicar", falha)
    saida, (ok, _, _), log = _lote(tmp_path, anonimizar=True, revisar=lambda a: True)
    assert ok == 0 and not list(saida.rglob("*.md"))
    assert "Nenhum arquivo foi salvo" in log


def test_mesmo_codigo_em_arquivos_diferentes():
    anon = Anonimizacao()
    anon.analisar({"a.md": "Requerente: Pedro Henrique Alves, CPF 529.982.247-25.",
                   "b.md": "O Sr. Pedro Henrique Alves compareceu."})
    a, b = anon.aplicar(anon.textos["a.md"]), anon.aplicar(anon.textos["b.md"])
    assert "[PESSOA_1]" in a and "[PESSOA_1]" in b and "Pedro" not in a + b


def test_incluir_e_unir():
    anon = Anonimizacao()
    anon.analisar({"a.md": "Testemunha: Kauã Ribeiro. Depois falou o Zeca do Pandeiro."})
    ent = anon.adicionar("Zeca do Pandeiro", "PESSOA")
    assert ent.total == 1
    anon.unir([e.id for e in anon.entidades() if e.tipo == "PESSOA"])
    saida = anon.aplicar(anon.textos["a.md"])
    assert "Zeca" not in saida and "Kauã" not in saida
    assert saida.count("[PESSOA_1]") == 2


# --------------------------------------------------------------- tela (tkinter)
def _tk():
    try:
        import tkinter as tk
        raiz = tk.Tk()
    except Exception as e:  # noqa: BLE001  (sem tkinter ou sem tela)
        pytest.skip(f"tkinter indisponível: {e}")
    raiz.withdraw()
    return raiz


def test_janela_de_revisao():
    raiz = _tk()
    from revisao_tk import JanelaRevisao
    anon = Anonimizacao()
    anon.analisar({"a.md": "Requerente: Maria Aparecida de Souza, CPF 529.982.247-25. Apelido: Tchuca."})
    try:
        j = JanelaRevisao(raiz, anon)
        linhas = j.tabela.get_children()
        assert len(linhas) >= 2
        cpf = next(e for e in anon.entidades() if e.tipo == "CPF")
        j.tabela.selection_set(str(cpf.id))
        j.mostrar_contexto()
        assert "529.982.247-25" in j.contexto.get("1.0", "end")
        j.alternar()
        assert cpf.ativo is False
        assert j.tabela.set(str(cpf.id), "sub") == "☐"
        ent = j.incluir("Tchuca", "PESSOA")
        assert ent is not None and str(ent.id) in j.tabela.get_children()
        j.salvar()
        assert j.confirmado
        saida = anon.aplicar(anon.textos["a.md"])
        assert "529.982.247-25" in saida and "Tchuca" not in saida and "Maria" not in saida
    finally:
        raiz.destroy()


@pytest.mark.skipif(os.name != "nt" and not os.environ.get("DISPLAY"), reason="sem tela")
def test_janela_principal_tem_a_opcao():
    raiz = _tk()
    raiz.destroy()
    import tkinter as tk
    criadas = []
    original = tk.Tk.mainloop

    def sem_loop(self, n=0):
        criadas.append(self)
        textos = []

        def coletar(w):
            for c in w.winfo_children():
                try:
                    textos.append(str(c.cget("text")))
                except Exception:  # noqa: BLE001
                    pass
                coletar(c)

        coletar(self)
        self.textos = textos
        self.destroy()

    tk.Tk.mainloop = sem_loop
    try:
        cm.abrir_janela()
    finally:
        tk.Tk.mainloop = original
    assert criadas and any("Anonimizar dados pessoais" in t for t in criadas[0].textos)
