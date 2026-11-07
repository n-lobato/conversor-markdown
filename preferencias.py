# -*- coding: utf-8 -*-
# Conversor Markdown
# Copyright (C) 2026 n-lobato
# Licença: GNU AGPL v3.
"""Lembra as opções da janela entre um uso e outro.

Guarda só as caixas de marcar (sim/não). Não guarda pastas nem nomes de arquivos,
que podem ter dados pessoais. "Sobrescrever .md existentes" também fica de fora de
propósito: volta sempre desmarcada, para ninguém apagar um arquivo sem perceber.

Local do arquivo:
  Windows: %APPDATA%\\Conversor Markdown\\preferencias.json
  Mac:     ~/Library/Application Support/Conversor Markdown/preferencias.json
  Linux:   ~/.config/conversor-markdown/preferencias.json
A variável de ambiente CONVERSOR_MARKDOWN_PREFERENCIAS troca o caminho (usada nos testes).
"""

import json
import os
import sys
from pathlib import Path

# anonimizar vem ligado: quem desliga é que precisa decidir isso de propósito
PADRAO = {"ocr": True, "subpastas": True, "auto": True, "anonimizar": True}


def arquivo():
    caminho = os.environ.get("CONVERSOR_MARKDOWN_PREFERENCIAS")
    if caminho:
        return Path(caminho)
    if os.name == "nt":
        base = Path(os.environ.get("APPDATA") or Path.home())
        return base / "Conversor Markdown" / "preferencias.json"
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / "Conversor Markdown" / "preferencias.json"
    base = Path(os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config")
    return base / "conversor-markdown" / "preferencias.json"


def carregar(caminho=None):
    """Devolve as opções salvas. Se o arquivo não existir ou estiver estragado, usa o padrão."""
    prefs = dict(PADRAO)
    try:
        dados = json.loads(Path(caminho or arquivo()).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return prefs
    if isinstance(dados, dict):
        for chave, valor in dados.items():
            if chave in PADRAO and isinstance(valor, bool):
                prefs[chave] = valor
    return prefs


def salvar(prefs, caminho=None):
    """Grava as opções. Falhar aqui não pode atrapalhar a conversão: devolve False e segue."""
    destino = Path(caminho or arquivo())
    dados = {k: bool(prefs[k]) for k in PADRAO if k in prefs}
    try:
        destino.parent.mkdir(parents=True, exist_ok=True)
        tmp = destino.with_suffix(".tmp")
        tmp.write_text(json.dumps(dados, indent=2), encoding="utf-8")
        os.replace(tmp, destino)
        return True
    except OSError:
        return False
