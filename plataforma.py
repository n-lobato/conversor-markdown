# -*- coding: utf-8 -*-
# Conversor Markdown
# Copyright (C) 2026 n-lobato
# Licença: GNU AGPL v3.
"""O que muda entre Windows, Mac e Linux: abrir pastas e escolher fontes."""

import os
import subprocess
import sys

WINDOWS = sys.platform.startswith("win")
MAC = sys.platform == "darwin"


def abrir_pasta(caminho):
    """Abre a pasta no gerenciador de arquivos do sistema."""
    caminho = str(caminho)
    if WINDOWS:
        os.startfile(caminho)  # noqa: S606
    elif MAC:
        subprocess.Popen(["open", caminho])
    else:
        subprocess.Popen(["xdg-open", caminho])


def fonte_ui(tamanho=10, *estilo):
    """Fonte comum da janela. Fora do Windows usa a padrão do sistema."""
    if WINDOWS:
        return ("Segoe UI", tamanho, *estilo)
    import tkinter.font as tkfont
    try:
        familia = tkfont.nametofont("TkDefaultFont").actual("family")
    except Exception:  # noqa: BLE001  (sem janela criada ainda)
        familia = "Helvetica"
    return (familia, tamanho + (3 if MAC else 0), *estilo)


def fonte_mono(tamanho=9):
    """Fonte de largura fixa para o registro da conversão."""
    if WINDOWS:
        return ("Consolas", tamanho)
    if MAC:
        return ("Menlo", tamanho + 2)
    return ("DejaVu Sans Mono", tamanho)
