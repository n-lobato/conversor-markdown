# -*- coding: utf-8 -*-
"""Lista as DLLs de que um executável do Windows precisa, dentro da própria pasta dele.

Uso: python build/dependencias_windows.py PASTA_DO_TESSERACT [tesseract.exe]

Lê a tabela de importação (normal e "sob demanda") do executável e de cada DLL
encontrada, de forma recursiva, e imprime uma DLL por linha. As DLLs do próprio
Windows (KERNEL32, msvcrt, WS2_32...) ficam de fora, porque não estão na pasta.

Substitui a lista fixa de DLLs que existia no build_portatil.ps1: quando o
Tesseract instalado pelo Chocolatey passou a depender da libcurl-4.dll, a lista
fixa deixou essa DLL de fora e o OCR das versões 1.2.0 e 1.3.0 não abria.
"""

import sys
from pathlib import Path

import pefile

TABELAS = ("IMAGE_DIRECTORY_ENTRY_IMPORT", "IMAGE_DIRECTORY_ENTRY_DELAY_IMPORT")


def importadas(arquivo: Path) -> list[str]:
    pe = pefile.PE(str(arquivo), fast_load=True)
    try:
        pe.parse_data_directories(directories=[pefile.DIRECTORY_ENTRY[t] for t in TABELAS])
        nomes = [e.dll.decode("ascii", "replace") for e in getattr(pe, "DIRECTORY_ENTRY_IMPORT", [])]
        nomes += [e.dll.decode("ascii", "replace") for e in getattr(pe, "DIRECTORY_ENTRY_DELAY_IMPORT", [])]
        return nomes
    finally:
        pe.close()


def dependencias(pasta: Path, executavel: str = "tesseract.exe") -> list[str]:
    na_pasta = {f.name.lower(): f.name for f in pasta.iterdir() if f.suffix.lower() == ".dll"}
    pendentes, achadas = [executavel], {}
    while pendentes:
        atual = pendentes.pop()
        for dll in importadas(pasta / atual):
            chave = dll.lower()
            if chave in na_pasta and chave not in achadas:
                achadas[chave] = na_pasta[chave]
                pendentes.append(na_pasta[chave])
    return sorted(achadas.values(), key=str.lower)


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    pasta = Path(sys.argv[1])
    exe = sys.argv[2] if len(sys.argv) > 2 else "tesseract.exe"
    if not (pasta / exe).is_file():
        print(f"Não encontrado: {pasta / exe}", file=sys.stderr)
        return 1
    for nome in dependencias(pasta, exe):
        print(nome)
    return 0


if __name__ == "__main__":
    sys.exit(main())
