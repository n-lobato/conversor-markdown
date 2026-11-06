# -*- coding: utf-8 -*-
# Conversor Markdown
# Copyright (C) 2026 n-lobato
# Licença: GNU AGPL v3. Usa o motor de detecção do Anonimizador LGPD (GPL-3.0),
# copiado na pasta anonimizador/.
"""Anonimização do Markdown gerado, antes de gravar.

Usa o mesmo motor do Anonimizador LGPD (https://github.com/n-lobato/anonimizador-lgpd):
encontra nomes, CPF, RG, endereços e outros dados pessoais e troca cada um por um
código ([PESSOA_1], [CPF_1]...). A mesma pessoa recebe o mesmo código em todos os
arquivos do lote.
"""

from collections import Counter

from anonimizador import __version__ as VERSAO_MOTOR  # noqa: F401
from anonimizador.deteccao.detector import Detector
from anonimizador.deteccao.modelo import TIPOS, descricao
from anonimizador.registro import GLOBAL, Registro, Substituidor

TIPOS_DISPONIVEIS = [t for t in TIPOS if t != "TERMO"]


class Anonimizacao:
    """Analisa um conjunto de textos e aplica os códigos depois da revisão."""

    def __init__(self, tipos=None):
        self.registro = Registro(por_arquivo=False)
        self.detector = Detector(set(tipos or TIPOS_DISPONIVEIS) | {"TERMO"})
        self.textos = {}

    def analisar(self, textos):
        """textos: {identificador (ex.: caminho de saída): conteúdo em Markdown}."""
        self.textos = dict(textos)
        for chave, texto in self.textos.items():
            for achado in self.detector.detectar(texto):
                self.registro.registrar(achado, chave)
        self.atualizar()

    def atualizar(self):
        """Reconta ocorrências e renumera (depois de unir, incluir ou remover itens)."""
        self.registro.consolidar_nomes(self.textos)
        self.registro.recontar(self.textos)
        self.registro.descartar_sem_ocorrencias()
        self.registro.numerar()

    # ------------------------------------------------------------ revisão
    def entidades(self):
        return self.registro.ordenadas()

    def contextos(self, entidade, limite=8):
        return self.registro.contextos(entidade, self.textos, limite)

    def adicionar(self, termo, tipo="PESSOA"):
        termo = (termo or "").strip()
        if not termo:
            return None
        ent = self.registro.adicionar_manual(termo, tipo)
        ent.ativo = True
        self.registro.recontar(self.textos)
        self.registro.numerar()
        return ent

    def unir(self, ids):
        ent = self.registro.unir(list(ids))
        self.registro.recontar(self.textos)
        self.registro.numerar()
        return ent

    def resumo(self):
        """Contagem por tipo dos itens que serão substituídos."""
        c = Counter(e.tipo for e in self.registro.entidades.values() if e.ativo and e.pai is None)
        return [(descricao(t), n) for t, n in sorted(c.items(), key=lambda x: (x[0] != "PESSOA", x[0]))]

    # ------------------------------------------------------------ aplicação
    def aplicar(self, texto):
        self.registro.numerar()
        return Substituidor(self.registro, GLOBAL).substituir(texto)
