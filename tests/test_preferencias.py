import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

import preferencias  # noqa: E402


def test_sem_arquivo_anonimizacao_vem_ligada(tmp_path):
    prefs = preferencias.carregar(tmp_path / "nao_existe.json")
    assert prefs["anonimizar"] is True
    assert prefs == preferencias.PADRAO


def test_salva_e_lembra_a_escolha(tmp_path):
    arq = tmp_path / "sub" / "preferencias.json"
    prefs = dict(preferencias.PADRAO, anonimizar=False, ocr=False)
    assert preferencias.salvar(prefs, arq)
    assert preferencias.carregar(arq)["anonimizar"] is False
    assert preferencias.carregar(arq)["ocr"] is False


def test_nao_guarda_pastas_nem_sobrescrever(tmp_path):
    arq = tmp_path / "preferencias.json"
    preferencias.salvar({"anonimizar": True, "sobrescrever": True, "pasta": "C:/Joao da Silva"}, arq)
    dados = json.loads(arq.read_text(encoding="utf-8"))
    assert set(dados) <= set(preferencias.PADRAO)
    assert "sobrescrever" not in preferencias.carregar(arq)


def test_arquivo_estragado_volta_ao_padrao(tmp_path):
    arq = tmp_path / "preferencias.json"
    arq.write_text("{isso nao e json", encoding="utf-8")
    assert preferencias.carregar(arq) == preferencias.PADRAO
    arq.write_text(json.dumps({"anonimizar": "nao"}), encoding="utf-8")
    assert preferencias.carregar(arq)["anonimizar"] is True


def test_falha_ao_gravar_nao_quebra(tmp_path):
    bloqueio = tmp_path / "arquivo_comum"
    bloqueio.write_text("x", encoding="utf-8")
    # a "pasta" de destino é um arquivo: não dá para criar
    assert preferencias.salvar(preferencias.PADRAO, bloqueio / "preferencias.json") is False


def test_variavel_de_ambiente_troca_o_caminho(tmp_path, monkeypatch):
    destino = tmp_path / "prefs.json"
    monkeypatch.setenv("CONVERSOR_MARKDOWN_PREFERENCIAS", str(destino))
    assert preferencias.arquivo() == destino
