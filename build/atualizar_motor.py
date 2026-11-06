"""Copia o motor de detecção do Anonimizador LGPD para dentro do conversor.

O conversor usa só a parte de detecção e substituição (Python puro, sem
dependências). A cópia fica em `anonimizador/` e não deve ser editada aqui:
as correções vão para o repositório do anonimizador e depois são trazidas
com este script.

Uso:
    python build/atualizar_motor.py CAMINHO_DO_REPOSITORIO_DO_ANONIMIZADOR
"""

import shutil
import subprocess
import sys
from pathlib import Path

ARQUIVOS = [
    "__init__.py", "texto.py", "registro.py",
    "deteccao/__init__.py", "deteccao/dados_nomes.py", "deteccao/detector.py",
    "deteccao/modelo.py", "deteccao/nomes.py", "deteccao/padroes.py", "deteccao/validadores.py",
]


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 1
    origem_repo = Path(sys.argv[1]).resolve()
    origem = origem_repo / "src" / "anonimizador"
    destino = Path(__file__).resolve().parents[1] / "anonimizador"
    if not (origem / "registro.py").exists():
        print(f"Não encontrei o anonimizador em {origem}")
        return 1
    if destino.exists():
        shutil.rmtree(destino)
    for rel in ARQUIVOS:
        (destino / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(origem / rel, destino / rel)
    try:
        commit = subprocess.run(["git", "-C", str(origem_repo), "describe", "--tags", "--always"],
                                capture_output=True, text=True, check=True).stdout.strip()
    except Exception:  # noqa: BLE001
        commit = "desconhecido"
    versao = next(l.split('"')[1] for l in (origem / "__init__.py").read_text(encoding="utf-8").splitlines()
                  if l.startswith("__version__"))
    (destino / "ORIGEM.txt").write_text(
        "Motor de detecção copiado do Anonimizador LGPD\n"
        "https://github.com/n-lobato/anonimizador-lgpd (licença GPL-3.0)\n"
        f"Versão: {versao}\nReferência: {commit}\n\n"
        "Não edite estes arquivos aqui. Corrija no anonimizador e rode\n"
        "python build/atualizar_motor.py CAMINHO_DO_ANONIMIZADOR\n", encoding="utf-8")
    print(f"Motor {versao} ({commit}) copiado para {destino}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
