# -*- coding: utf-8 -*-
# Conversor Markdown
# Copyright (C) 2026 n-lobato
# Licença: GNU AGPL v3.
"""Tela de revisão da anonimização (tkinter).

Mostra tudo o que foi encontrado antes de gravar. A pessoa desmarca o que não é
dado pessoal, inclui o que faltou e une linhas que são a mesma pessoa.
"""

import tkinter as tk
from pathlib import Path
from tkinter import messagebox, simpledialog, ttk

from anonimizador.deteccao.modelo import descricao

from anonimizacao import TIPOS_DISPONIVEIS

MARCADO, DESMARCADO = "☑", "☐"

AVISO = ("Confira antes de salvar. Nenhum programa encontra tudo: na medição do anonimizador, "
         "cerca de 1 em cada 10 nomes passou. Desmarque o que não é dado pessoal (duplo clique "
         "ou barra de espaço) e use \"Incluir termo\" para o que faltou. Os nomes dos arquivos "
         "não são alterados.")


class JanelaRevisao(tk.Toplevel):
    def __init__(self, mestre, anonimizacao):
        super().__init__(mestre)
        self.anon = anonimizacao
        self.confirmado = False
        self.title("Revisar anonimização")
        self.geometry("900x620")
        self.minsize(720, 480)
        self.transient(mestre)
        self.protocol("WM_DELETE_WINDOW", self.cancelar)

        frm = ttk.Frame(self, padding=10)
        frm.pack(fill="both", expand=True)
        frm.columnconfigure(0, weight=1)
        frm.rowconfigure(1, weight=3)
        frm.rowconfigure(3, weight=1)

        ttk.Label(frm, text=AVISO, wraplength=860, foreground="#7a3b00", justify="left").grid(
            row=0, column=0, sticky="ew", pady=(0, 8))

        colunas = ("sub", "tipo", "texto", "codigo", "vezes")
        self.tabela = ttk.Treeview(frm, columns=colunas, show="headings", selectmode="extended")
        for col, titulo, larg, est in (("sub", "Trocar", 60, False), ("tipo", "Tipo", 170, False),
                                       ("texto", "Encontrado", 330, True), ("codigo", "Código", 120, False),
                                       ("vezes", "Vezes", 60, False)):
            self.tabela.heading(col, text=titulo)
            self.tabela.column(col, width=larg, stretch=est, anchor="center" if col in ("sub", "vezes") else "w")
        rolagem = ttk.Scrollbar(frm, orient="vertical", command=self.tabela.yview)
        self.tabela.configure(yscrollcommand=rolagem.set)
        self.tabela.grid(row=1, column=0, sticky="nsew")
        rolagem.grid(row=1, column=1, sticky="ns")
        self.tabela.tag_configure("desmarcado", foreground="#999")
        self.tabela.bind("<Double-1>", lambda e: self.alternar())
        self.tabela.bind("<space>", lambda e: self.alternar())
        self.tabela.bind("<<TreeviewSelect>>", lambda e: self.mostrar_contexto())

        ttk.Label(frm, text="Onde aparece:").grid(row=2, column=0, sticky="w", pady=(8, 2))
        self.contexto = tk.Text(frm, height=7, wrap="word", font=("Segoe UI", 9), state="disabled",
                                background="#f7f7f7")
        self.contexto.grid(row=3, column=0, columnspan=2, sticky="nsew")
        self.contexto.tag_configure("arq", foreground="#335", font=("Segoe UI", 9, "bold"))

        botoes = ttk.Frame(frm)
        botoes.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        ttk.Button(botoes, text="Marcar/desmarcar", command=self.alternar).pack(side="left")
        ttk.Button(botoes, text="Incluir termo...", command=self.incluir).pack(side="left", padx=4)
        ttk.Button(botoes, text="Unir selecionados", command=self.unir).pack(side="left")
        self.resumo = ttk.Label(botoes, text="")
        self.resumo.pack(side="left", padx=12)
        ttk.Button(botoes, text="Salvar anonimizado", command=self.salvar).pack(side="right")
        ttk.Button(botoes, text="Cancelar (não salvar nada)", command=self.cancelar).pack(side="right", padx=4)

        self.atualizar_tabela()

    # ------------------------------------------------------------ tabela
    def atualizar_tabela(self, manter=None):
        manter = set(manter or self.tabela.selection())
        self.tabela.delete(*self.tabela.get_children())
        for e in self.anon.entidades():
            iid = str(e.id)
            self.tabela.insert("", "end", iid=iid, values=(
                MARCADO if e.ativo else DESMARCADO, descricao(e.tipo), e.rotulo,
                e.codigo if e.ativo else "(mantido)", e.total),
                tags=() if e.ativo else ("desmarcado",))
            if iid in manter:
                self.tabela.selection_add(iid)
        ativos = sum(1 for e in self.anon.entidades() if e.ativo)
        self.resumo.configure(text=f"{ativos} de {len(self.anon.entidades())} itens serão trocados")

    def selecionadas(self):
        ents = self.anon.registro.entidades
        return [ents[int(i)] for i in self.tabela.selection() if int(i) in ents]

    def alternar(self):
        sel = self.selecionadas()
        if not sel:
            return
        novo = not all(e.ativo for e in sel)
        for e in sel:
            e.ativo = novo
        self.atualizar_tabela()

    def mostrar_contexto(self):
        sel = self.selecionadas()
        self.contexto.configure(state="normal")
        self.contexto.delete("1.0", "end")
        if sel:
            for arq, trecho in self.anon.contextos(sel[0]):
                self.contexto.insert("end", Path(arq).name + ": ", "arq")
                self.contexto.insert("end", trecho.replace("\n", " ") + "\n")
        self.contexto.configure(state="disabled")

    # ------------------------------------------------------------ ações
    def incluir(self, termo=None, tipo=None):
        if termo is None:
            termo = simpledialog.askstring("Incluir termo", "Texto que deve ser trocado (exatamente como aparece):",
                                           parent=self)
        if not termo:
            return None
        if tipo is None:
            tipo = self._perguntar_tipo()
            if tipo is None:
                return None
        ent = self.anon.adicionar(termo, tipo)
        if ent is not None and ent.total == 0:
            messagebox.showinfo("Incluir termo", f"\"{termo}\" não aparece nos textos convertidos.", parent=self)
        self.atualizar_tabela(manter=[str(ent.id)] if ent else None)
        return ent

    def _perguntar_tipo(self):
        caixa = tk.Toplevel(self)
        caixa.title("Tipo do dado")
        caixa.transient(self)
        escolha = tk.StringVar(value=descricao("PESSOA"))
        nomes = {descricao(t): t for t in TIPOS_DISPONIVEIS}
        ttk.Label(caixa, text="Que tipo de dado é?", padding=(10, 10, 10, 4)).pack(anchor="w")
        ttk.Combobox(caixa, textvariable=escolha, values=list(nomes), state="readonly", width=45).pack(padx=10)
        resultado = {}

        def ok():
            resultado["tipo"] = nomes.get(escolha.get(), "PESSOA")
            caixa.destroy()

        ttk.Button(caixa, text="OK", command=ok).pack(pady=10)
        caixa.grab_set()
        self.wait_window(caixa)
        return resultado.get("tipo")

    def unir(self):
        sel = self.selecionadas()
        if len(sel) < 2:
            messagebox.showinfo("Unir", "Selecione duas ou mais linhas que sejam a mesma pessoa ou o mesmo dado.",
                                parent=self)
            return
        alvo = self.anon.unir([e.id for e in sel])
        self.atualizar_tabela(manter=[str(alvo.id)] if alvo else None)

    def salvar(self):
        self.confirmado = True
        self.destroy()

    def cancelar(self):
        self.confirmado = False
        self.destroy()


def revisar(mestre, anonimizacao):
    """Abre a revisão e espera. Devolve True se a pessoa mandou salvar."""
    janela = JanelaRevisao(mestre, anonimizacao)
    janela.grab_set()
    mestre.wait_window(janela)
    return janela.confirmado
