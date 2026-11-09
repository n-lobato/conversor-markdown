# -*- coding: utf-8 -*-
"""Monta a tabela de licenças das fórmulas do Homebrew incluídas no pacote do Mac.

Uso: brew info --json=v2 FORMULAS | python build/licencas_homebrew.py > _INDICE.md
"""
import json
import sys

dados = json.load(sys.stdin)
print("# Tesseract e bibliotecas incluídas (do Homebrew)\n")
print("| Componente | Versão | Licença | Site |")
print("| --- | --- | --- | --- |")
for f in dados["formulae"]:
    instalada = (f.get("installed") or [{}])[0].get("version", "")
    print(f"| {f['name']} | {instalada} | {f.get('license') or 'ver site'} | {f.get('homepage', '')} |")
