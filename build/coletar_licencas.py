# -*- coding: utf-8 -*-
"""
Coleta as licencas das bibliotecas Python instaladas no ambiente de build
e grava em PASTA_DESTINO (uma subpasta por pacote + um indice).

Uso: python coletar_licencas.py PASTA_DESTINO
"""
import shutil
import sys
from importlib import metadata
from pathlib import Path

# pacotes cuja metadata nao declara a licenca (confirmado pelo fabricante)
LICENCA_CONHECIDA = {
    "pymupdf4llm": "AGPL-3.0 ou licenca comercial Artifex",
    "pymupdf-layout": "AGPL-3.0 ou licenca comercial Artifex",
    "pymupdf_layout": "AGPL-3.0 ou licenca comercial Artifex",
}
IGNORAR = {"pip", "setuptools", "wheel", "pyinstaller", "pyinstaller-hooks-contrib",
           "altgraph", "pefile", "pywin32-ctypes"}


def licenca_de(dist):
    md = dist.metadata
    nome = md["Name"]
    if nome.lower() in LICENCA_CONHECIDA:
        return LICENCA_CONHECIDA[nome.lower()]
    for campo in ("License-Expression", "License"):
        v = md.get(campo)
        if v and len(v) < 120 and v.strip().upper() != "UNKNOWN":
            return v.strip()
    cls = [c.split("::")[-1].strip() for c in md.get_all("Classifier") or [] if c.startswith("License ::")]
    return "; ".join(cls) or "nao declarada (ver site do projeto)"


def main():
    destino = Path(sys.argv[1])
    destino.mkdir(parents=True, exist_ok=True)
    linhas = ["# Bibliotecas Python incluidas", "",
              "| Pacote | Versao | Licenca | Site |", "| --- | --- | --- | --- |"]
    for dist in sorted(metadata.distributions(), key=lambda d: d.metadata["Name"].lower()):
        nome = dist.metadata["Name"]
        if nome.lower() in IGNORAR:
            continue
        site = dist.metadata.get("Home-page") or ""
        if not site:
            for url in dist.metadata.get_all("Project-URL") or []:
                site = url.split(",", 1)[-1].strip()
                break
        linhas.append(f"| {nome} | {dist.version} | {licenca_de(dist)} | {site} |")
        arquivos = [f for f in (dist.files or [])
                    if any(k in f.name.upper() for k in ("LICEN", "COPYING", "NOTICE", "AUTHORS"))]
        if arquivos:
            pasta = destino / nome
            pasta.mkdir(exist_ok=True)
            for f in arquivos:
                origem = Path(dist.locate_file(f))
                if origem.is_file():
                    shutil.copy2(origem, pasta / origem.name)
    (destino / "_INDICE.md").write_text("\n".join(linhas) + "\n", encoding="utf-8")
    print(f"{len(linhas) - 4} pacotes listados em {destino}")


if __name__ == "__main__":
    main()
