#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Laboratório de Conteúdo — Cruzamento dos rótulos do Jev com o engajamento
-------------------------------------------------------------------------
Engajamento = curtidas + 3x comentários, comparado à MEDIANA do próprio perfil
(assim perfis grandes e pequenos ficam comparáveis). "Campeão" = 3x a mediana.

Rodar:  python3 analisar.py
"""
import glob
import json
import statistics as st
from collections import Counter, defaultdict

CAMPOS = ["gancho", "tema", "publico", "emocao", "intencao"]
PROPRIO = "giselehedler"


def carregar():
    rotulos = json.load(open("dados/rotulos.json", encoding="utf-8"))
    perfis = {}
    for arq in sorted(glob.glob("dados/posts_*.json")):
        nome = arq[len("dados/posts_"):-len(".json")]
        posts = json.load(open(arq, encoding="utf-8"))["posts"]
        for p in posts:
            p["eng"] = (p.get("like_count") or 0) + 3 * (p.get("comments_count") or 0)
        med = st.median(p["eng"] for p in posts) or 1
        for p in posts:
            p["rel"] = p["eng"] / med
            p.update({k: v for k, v in rotulos.get(p["permalink"], {}).items() if k != "tokens"})
        perfis[nome] = posts
    return perfis


def pct(posts, campo, valor):
    return 100.0 * sum(1 for p in posts if p.get(campo) == valor) / max(len(posts), 1)


def main():
    perfis = carregar()
    refs = [p for n, ps in perfis.items() if n != PROPRIO for p in ps]
    meus = perfis[PROPRIO]

    print("=== Mistura de conteúdo: % dos posts (você vs média das referências) ===")
    for campo in CAMPOS:
        valores = Counter(p.get(campo) for p in refs + meus)
        print("\n[%s]" % campo)
        print("  %-26s %7s %7s  %s" % ("", "você", "refs", "  ".join("%-8s" % n[:8] for n in perfis if n != PROPRIO)))
        for v, _ in valores.most_common():
            linha = "  %-26s %6.0f%% %6.0f%%  " % (v, pct(meus, campo, v), pct(refs, campo, v))
            linha += "  ".join("%7.0f%%" % pct(perfis[n], campo, v) for n in perfis if n != PROPRIO)
            print(linha)

    print("\n=== O que rende mais: desempenho mediano (x a mediana do perfil) por rótulo ===")
    for grupo, posts in (("referências", refs), ("você", meus)):
        print("\n--- %s ---" % grupo)
        for campo in CAMPOS:
            por = defaultdict(list)
            for p in posts:
                por[p.get(campo)].append(p["rel"])
            itens = sorted(((st.median(v), k, len(v)) for k, v in por.items() if len(v) >= 5), reverse=True)
            print("  %-10s " % campo + " | ".join("%s %.2fx (n=%d)" % (k, m, n) for m, k, n in itens))

    print("\n=== Sinais contínuos: campeões (>=3x) vs resto ===")
    for grupo, posts in (("referências", refs), ("você", meus)):
        camp = [p for p in posts if p["rel"] >= 3 and "forca_gancho" in p]
        resto = [p for p in posts if p["rel"] < 3 and "forca_gancho" in p]
        for s in ("fala_com_seguidora", "historia_propria", "forca_gancho"):
            print("  %-12s %-20s campeões %.2f | resto %.2f  (n=%d/%d)" % (
                grupo, s, st.mean(p[s] for p in camp) if camp else 0, st.mean(p[s] for p in resto), len(camp), len(resto)))


if __name__ == "__main__":
    main()
