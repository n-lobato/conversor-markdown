# -*- coding: utf-8 -*-
"""Confere se cada DLL do Tesseract que vai no pacote está documentada no THIRD-PARTY-NOTICES.md.

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
    return 0


if __name__ == "__main__":
    sys.exit(main())
