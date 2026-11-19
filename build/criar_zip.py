# -*- coding: utf-8 -*-
"""Cria o .zip da versão portátil com caminhos no padrão do formato zip (barra "/").

Uso: python build/criar_zip.py PASTA_DE_ORIGEM ARQUIVO.zip

Substitui o [IO.Compression.ZipFile]::CreateFromDirectory do Windows PowerShell 5.1,
que grava os caminhos com barra invertida ("Conversor Markdown\\LICENCAS\\..."). O
Windows entende, mas descompactadores de Mac e Linux mostram nomes estranhos.
O conteúdo da pasta de origem vai para a raiz do .zip.
"""

import sys
import zipfile
from pathlib import Path


def criar(origem: Path, destino: Path) -> int:
    destino.parent.mkdir(parents=True, exist_ok=True)
    total = 0
    with zipfile.ZipFile(destino, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for item in sorted(origem.rglob("*")):
            nome = item.relative_to(origem).as_posix()
            if item.is_dir():
                if not any(item.iterdir()):
                    z.writestr(nome + "/", "")
                continue
            z.write(item, nome)
            total += 1
    return total


def main() -> int:
    if len(sys.argv) != 3:
        print(__doc__)
        return 2
    origem, destino = Path(sys.argv[1]), Path(sys.argv[2])
    if not origem.is_dir():
        print(f"Pasta não encontrada: {origem}", file=sys.stderr)
        return 1
    if destino.exists():
        destino.unlink()
    total = criar(origem, destino)
    with zipfile.ZipFile(destino) as z:
        ruins = [n for n in z.namelist() if "\\" in n]
    if ruins:
        print(f"Caminhos com barra invertida no .zip: {ruins[:3]}", file=sys.stderr)
        return 1
    print(f"    {total} arquivos em {destino.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
