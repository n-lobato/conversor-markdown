# -*- coding: utf-8 -*-
"""Confere as licenças das DLLs do Tesseract que vão no pacote do Windows.

1. Cada DLL precisa estar na tabela do THIRD-PARTY-NOTICES.md.
2. Cada DLL precisa ter o texto da licença em LICENCAS/Tesseract/bibliotecas.

Uso: python build/verificar_licencas_dlls.py PASTA_TESSERACT_DO_PACOTE [THIRD-PARTY-NOTICES.md]

Como as DLLs agora são descobertas automaticamente (build/dependencias_windows.py),
uma atualização do Tesseract pode trazer uma biblioteca nova. Este teste falha e
diz qual é, para que a licença dela seja acrescentada à tabela antes de publicar.
"""

import sys
from pathlib import Path


def main() -> int:
    pasta = Path(sys.argv[1])
    avisos = Path(sys.argv[2] if len(sys.argv) > 2 else "THIRD-PARTY-NOTICES.md")
    texto = avisos.read_text(encoding="utf-8").lower()
    dlls = sorted(f.name for f in pasta.glob("*.dll"))
    faltando = [d for d in dlls if d.lower() not in texto]
    print(f"{len(dlls)} DLLs no pacote: {', '.join(dlls)}")
    if faltando:
        print(f"FALHOU: DLLs sem licença documentada em {avisos.name}: {', '.join(faltando)}")
        return 1
    print(f"OK: todas as DLLs estão documentadas em {avisos.name}.")

    # Textos completos das licenças, reunidos no build por build/licencas_windows.py
    indice = pasta.parent / "LICENCAS" / "Tesseract" / "bibliotecas" / "_INDICE.md"
    if not indice.is_file():
        print(f"FALHOU: não há textos de licença das DLLs no pacote ({indice} não existe).")
        return 1
    conteudo = indice.read_text(encoding="utf-8").lower()
    sem_texto = [d for d in dlls if d.lower() not in conteudo]
    if sem_texto or "sem texto de licença" in conteudo:
        print(f"FALHOU: DLLs sem texto de licença em {indice.name}: {', '.join(sem_texto) or 'veja o índice'}")
        return 1
    arquivos = [f for f in indice.parent.rglob("*") if f.is_file() and f.name != "_INDICE.md"]
    print(f"OK: textos de licença de todas as DLLs no pacote ({len(arquivos)} arquivos).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
