# -*- coding: utf-8 -*-
"""Copia os textos de licença das DLLs do Tesseract para o pacote do Windows.

Uso:
  python build/licencas_windows.py --destino PASTA [--msys C:\\msys64] [--obrigatorio] DLL [DLL ...]

O Tesseract para Windows (UB Mannheim, instalado pelo Chocolatey no build) é
compilado com bibliotecas do MSYS2 (repositório mingw64). Para cada DLL, o script:
  1. descobre o pacote MSYS2 que a contém (pacman -F);
  2. baixa esse pacote, sem instalar nada (pacman -Sw);
  3. copia os arquivos de licença dele (share/licenses/<pacote>/, ou COPYING,
     LICENSE etc. em share/doc) para PASTA/<pacote>/;
  4. escreve PASTA/_INDICE.md, com DLL, pacote, versão e arquivos copiados.

Os textos vêm da versão atual do pacote no MSYS2, que pode ser mais nova que a
usada na compilação do Tesseract; o texto de licença dessas bibliotecas
raramente muda entre versões.

Com --obrigatorio (usado no GitHub Actions), falha se alguma DLL ficar sem
pacote identificado ou sem texto de licença.
"""

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

PREFIXO = "mingw-w64-x86_64-"
REPO = "mingw64"
NOME_LICENCA = re.compile(r"^(copying|licen[cs]e|copyright|notice|unlicense|patents)", re.I)  # COPYING, COPYINGv2, LICENSE.md...


class Msys:
    def __init__(self, raiz: Path):
        self.bash = raiz / "usr" / "bin" / "bash.exe"
        if not self.bash.is_file():
            raise FileNotFoundError(f"MSYS2 não encontrado em {raiz}")
        self.env = {**os.environ, "MSYSTEM": "MSYS", "CHERE_INVOKING": "1"}

    def rodar(self, comando: str, verificar: bool = True) -> str:
        r = subprocess.run([str(self.bash), "-lc", comando], capture_output=True, env=self.env)
        saida = r.stdout.decode("utf-8", "replace")
        if verificar and r.returncode != 0:
            raise RuntimeError(f"Falhou: {comando}\n{saida}\n{r.stderr.decode('utf-8', 'replace')}")
        return saida

    def posix(self, caminho: Path) -> str:
        return self.rodar(f"cygpath -u '{caminho}'").strip()


def pacotes_das_dlls(msys: Msys, dlls: list[str]) -> tuple[dict, list[str]]:
    """{pacote: {"versao": ..., "dlls": [...]}} e a lista de DLLs sem pacote."""
    alvos = " ".join(f"'{REPO}/bin/{d}'" for d in dlls)
    saida = msys.rodar(f"pacman -F --machinereadable {alvos}", verificar=False)
    por_dll: dict[str, tuple[str, str]] = {}
    for linha in saida.splitlines():
        partes = linha.split("\0")
        if len(partes) < 4 or partes[0] != REPO:
            continue
        repo, pacote, versao, caminho = partes[:4]
        por_dll.setdefault(Path(caminho).name.lower(), (pacote, versao))
    pacotes: dict[str, dict] = {}
    sem_pacote = []
    for d in dlls:
        if d.lower() not in por_dll:
            sem_pacote.append(d)
            continue
        pacote, versao = por_dll[d.lower()]
        pacotes.setdefault(pacote, {"versao": versao, "dlls": []})["dlls"].append(d)
    return pacotes, sem_pacote


def arquivos_de_licenca(conteudo: list[str], pacote: str) -> list[str]:
    curto = pacote[len(PREFIXO):] if pacote.startswith(PREFIXO) else pacote
    arquivos = [c for c in conteudo if not c.endswith("/")]
    proprios = [c for c in arquivos if c.startswith(f"{REPO}/share/licenses/")]
    if proprios:
        return proprios
    docs = [c for c in arquivos if c.startswith(f"{REPO}/share/doc/") and NOME_LICENCA.match(Path(c).name)]
    if docs:
        return docs
    return [c for c in arquivos if curto in c and NOME_LICENCA.match(Path(c).name)]


FONTES = "https://repo.msys2.org/mingw/sources"


def licencas_do_codigo_fonte(msys: Msys, curto: str, versao: str, pasta: Path) -> list[str]:
    """Baixa o pacote de código-fonte do MSYS2 e extrai os arquivos de licença do projeto.

    Devolve caminhos relativos a ``pasta``. O pacote-fonte traz o PKGBUILD e o
    arquivo original do projeto (.tar.gz, .tar.xz...), de onde saem os arquivos
    de licença da raiz (e, se houver, os da pasta lib/, caso do lz4).
    """
    import urllib.request

    nome = f"mingw-w64-{curto}-{versao}.src.tar.zst"
    destino_arq = pasta / nome
    with urllib.request.urlopen(f"{FONTES}/{nome}", timeout=120) as r, open(destino_arq, "wb") as f:
        shutil.copyfileobj(r, f)
    pasta_p = msys.posix(pasta)
    msys.rodar(f"bsdtar -xf '{pasta_p}/{nome}' -C '{pasta_p}'")
    tarballs = [t for t in pasta.rglob("*") if t.is_file() and re.search(r"\.(tar\.(gz|xz|bz2|zst|lz)|tgz|zip)$", t.name)
                and t.name != nome]
    achados: list[str] = []
    for t in tarballs:
        t_p = msys.posix(t)
        itens = [i for i in msys.rodar(f"bsdtar -tf '{t_p}'").splitlines() if i and not i.endswith("/")]
        escolhidos = []
        for i in itens:
            partes = i.split("/")
            if not NOME_LICENCA.match(partes[-1]):
                continue
            if len(partes) == 2 or (len(partes) == 3 and partes[1] == "lib"):
                escolhidos.append(i)
        if escolhidos:
            saida = pasta / "x"
            saida.mkdir(exist_ok=True)
            lista = " ".join(f"'{i}'" for i in escolhidos)
            msys.rodar(f"bsdtar -xf '{t_p}' -C '{msys.posix(saida)}' {lista}")
            achados += [f"x/{i}" for i in escolhidos]
    return achados


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--destino", required=True, type=Path)
    ap.add_argument("--msys", default=os.environ.get("MSYS2_ROOT", r"C:\msys64"), type=Path)
    ap.add_argument("--obrigatorio", action="store_true")
    ap.add_argument("--tesseract-licenca", type=Path,
                    help="LICENSE do Tesseract (a libtesseract é compilada pela UB Mannheim, não vem do MSYS2)")
    ap.add_argument("dlls", nargs="+")
    a = ap.parse_args()

    msys = Msys(a.msys)
    print("    Atualizando os índices do MSYS2...")
    msys.rodar("pacman -Sy --noconfirm >/dev/null && pacman -Fy --noconfirm >/dev/null")
    tess_dlls = [d for d in a.dlls if d.lower().startswith("libtesseract")]
    outras = [d for d in a.dlls if d not in tess_dlls]
    pacotes, sem_pacote = pacotes_das_dlls(msys, outras)

    a.destino.mkdir(parents=True, exist_ok=True)
    problemas = [f"{d}: nenhum pacote do MSYS2 ({REPO}) contém esta DLL" for d in sem_pacote]
    linhas = []
    if tess_dlls:
        if a.tesseract_licenca and a.tesseract_licenca.is_file():
            (a.destino / "tesseract").mkdir(exist_ok=True)
            shutil.copy2(a.tesseract_licenca, a.destino / "tesseract" / "LICENSE.txt")
            linhas.append(f"| tesseract (UB Mannheim) | - | {', '.join(tess_dlls)} | tesseract/LICENSE.txt |")
        else:
            problemas += [f"{d}: informe --tesseract-licenca" for d in tess_dlls]
    with tempfile.TemporaryDirectory() as tmp:
        cache, extraido = Path(tmp) / "cache", Path(tmp) / "x"
        cache.mkdir()
        extraido.mkdir()
        cache_p, extraido_p = msys.posix(cache), msys.posix(extraido)
        alvos = " ".join(f"{REPO}/{p}" for p in pacotes)
        if alvos:
            msys.rodar(f"pacman -Sw --noconfirm -dd --cachedir '{cache_p}' {alvos} >/dev/null")
        for pacote, info in sorted(pacotes.items()):
            curto = pacote[len(PREFIXO):] if pacote.startswith(PREFIXO) else pacote
            padrao = re.compile(rf"^{re.escape(pacote)}-[^-]+-[^-]+-any\.pkg\.tar\.(zst|xz)$")
            arquivo = next((f for f in cache.iterdir() if padrao.match(f.name)), None)
            if arquivo is None:
                problemas.append(f"{pacote}: pacote não foi baixado")
                continue
            arq_p = f"{cache_p}/{arquivo.name}"
            conteudo = msys.rodar(f"bsdtar -tf '{arq_p}'").splitlines()
            licencas = arquivos_de_licenca(conteudo, pacote)
            base_extracao = extraido
            fonte = ""
            if licencas:
                lista = " ".join(f"'{c}'" for c in licencas)
                msys.rodar(f"bsdtar -xf '{arq_p}' -C '{extraido_p}' {lista}")
            else:
                # o pacote binário não traz licença: busca no código-fonte da mesma versão
                base_extracao = Path(tmp) / f"fonte-{curto}"
                base_extracao.mkdir()
                try:
                    licencas = licencas_do_codigo_fonte(msys, curto, info["versao"], base_extracao)
                    fonte = " (do código-fonte)"
                except Exception as e:  # rede, formato inesperado etc.
                    print(f"    falha ao ler o código-fonte de {curto}: {e}")
                if not licencas:
                    problemas.append(f"{pacote}: sem arquivo de licença no pacote nem no código-fonte")
                    continue
            pasta = a.destino / curto
            pasta.mkdir(exist_ok=True)
            copiados = []
            for c in licencas:
                origem = base_extracao / c
                nome = origem.name
                if (pasta / nome).exists():  # mesmo nome em pastas diferentes (ex.: LICENSE e lib/LICENSE)
                    nome = f"{origem.parent.name}_{origem.name}"
                shutil.copy2(origem, pasta / nome)
                copiados.append(nome)
            linhas.append(f"| {curto} | {info['versao']} | {', '.join(sorted(info['dlls'], key=str.lower))} "
                          f"| {', '.join(f'{curto}/{n}' for n in copiados)}{fonte} |")

    indice = [
        "# Textos de licença das bibliotecas do Tesseract (Windows)",
        "",
        "Gerado no build a partir dos pacotes do MSYS2 (repositório mingw64), de onde vêm as",
        "DLLs do Tesseract para Windows. O código-fonte de cada pacote está em",
        "https://packages.msys2.org. A versão é a do pacote consultado no build.",
        "",
        "| Pacote | Versão | DLLs | Arquivos |",
        "| --- | --- | --- | --- |",
        *linhas,
    ]
    if problemas:
        indice += ["", "## Sem texto de licença encontrado", "", *[f"- {p}" for p in problemas]]
    (a.destino / "_INDICE.md").write_text("\n".join(indice) + "\n", encoding="utf-8")

    print(f"    Licenças de {len(linhas)} pacote(s) copiadas para {a.destino}")
    for p in problemas:
        print(f"    AVISO: {p}")
    if problemas and a.obrigatorio:
        print("FALHOU: há DLLs sem texto de licença (veja os avisos acima).")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
