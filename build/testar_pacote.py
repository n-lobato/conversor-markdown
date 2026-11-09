# -*- coding: utf-8 -*-
"""Testa o programa já empacotado (Windows, Mac ou Linux), do jeito que o usuário recebe.

Uso: python build/testar_pacote.py CAMINHO_DO_EXECUTAVEL [--janela]

1. Converte uma planilha e uma imagem (com OCR) sem anonimizar e confere o texto.
2. Converte de novo com --anonimizar e confere que o nome e o CPF sumiram.
3. Com --janela, abre a janela e confere que ela fica aberta (não fechou com erro).
"""

import subprocess
import sys
import tempfile
import time
from pathlib import Path

NOME = "Maria Aparecida de Souza"
CPF = "529.982.247-25"


def fonte(tamanho=48):
    from PIL import ImageFont
    for nome in ("arial.ttf", "DejaVuSans.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                 "/System/Library/Fonts/Supplemental/Arial.ttf", "/Library/Fonts/Arial.ttf"):
        try:
            return ImageFont.truetype(nome, tamanho)
        except OSError:
            continue
    return ImageFont.load_default(size=tamanho)


def preparar(pasta):
    from PIL import Image, ImageDraw
    pasta.mkdir(parents=True, exist_ok=True)
    (pasta / "lista.csv").write_text(f"Nome;CPF\n{NOME};{CPF}\n", encoding="utf-8")
    img = Image.new("RGB", (1500, 300), "white")
    d = ImageDraw.Draw(img)
    d.text((60, 60), "Requerente: " + NOME, fill="black", font=fonte())
    d.text((60, 160), "CPF " + CPF, fill="black", font=fonte())
    img.save(pasta / "imagem.png")


def rodar(exe, *args):
    r = subprocess.run([str(exe), *map(str, args)], capture_output=True, text=True, timeout=600)
    print(f"$ {Path(exe).name} {' '.join(map(str, args))}  -> código {r.returncode}")
    return r


def ler(caminho):
    if not caminho.is_file():
        raise SystemExit(f"FALHOU: não gerou {caminho}")
    return caminho.read_text(encoding="utf-8")


def main():
    exe = Path(sys.argv[1]).resolve()
    if not exe.is_file():
        raise SystemExit(f"Executável não encontrado: {exe}")
    base = Path(tempfile.mkdtemp(prefix="teste_pacote_"))
    origem = base / "amostra"
    preparar(origem)

    rodar(exe, origem, f"--saida={base / 'normal'}")
    csv = ler(base / "normal" / "lista.md")
    img = ler(base / "normal" / "imagem.md")
    print("--- lista.md\n" + csv + "--- imagem.md (OCR)\n" + img)
    assert CPF in csv, "conversão da planilha falhou"
    assert "529" in img and "Souza" in img, "OCR não leu a imagem (Tesseract incluído não funcionou?)"

    rodar(exe, origem, f"--saida={base / 'anon'}", "--anonimizar")
    anon = ler(base / "anon" / "lista_anonimizado.md") + ler(base / "anon" / "imagem_anonimizado.md")
    print("--- anonimizados\n" + anon)
    assert "Maria" not in anon and "529.982" not in anon, "anonimização falhou"
    assert "[PESSOA_1]" in anon, "código de pessoa não apareceu"

    if "--janela" in sys.argv:
        proc = subprocess.Popen([str(exe)])
        time.sleep(20)
        if proc.poll() is not None:
            raise SystemExit(f"FALHOU: a janela fechou sozinha (código {proc.returncode})")
        proc.terminate()
        print("Janela abriu e continuou aberta.")

    print("OK: pacote testado.")


if __name__ == "__main__":
    main()
