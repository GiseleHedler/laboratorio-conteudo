#!/usr/bin/env python3
"""Ranqueia o export do Viral Finder (CSV) de um perfil.
Reels: visualizações ÷ mediana dos 40 reels vizinhos no tempo. Menos de 8 curtidas por mil
visualizações = provável anúncio (fica de fora). Carrosséis/fotos: curtidas + 3x comentários
contra a mediana dos vizinhos.
Uso: python3 analisar_viral.py export.csv perfil   -> dados/viral_<perfil>.json
"""
import csv, json, sys, statistics as st, datetime as dt

arq, perfil = sys.argv[1], sys.argv[2]
R = list(csv.DictReader(open(arq, encoding="utf-8")))
for r in R:
    r["d"] = dt.datetime.strptime(r["post_date"], "%m/%d/%Y")
    for k in ("likes", "comments", "views"):
        try: r[k] = int(float(r[k] or 0))
        except ValueError: r[k] = 0

def ranquear(itens, valor, viz):
    itens.sort(key=lambda r: r["d"])
    for i, r in enumerate(itens):
        m = st.median(valor(x) for x in itens[max(0, i - viz):i + viz + 1]) or 1
        r["x"] = round(valor(r) / m, 1)

reels = [r for r in R if r["type"] == "clips" and r["views"] > 0]
ranquear(reels, lambda r: r["views"], 20)
anuncios = [r for r in reels if r["likes"] * 1000 / r["views"] < 8]
organicos = sorted((r for r in reels if r not in anuncios), key=lambda r: -r["x"])
outros = [r for r in R if r["type"] != "clips"]
if outros: ranquear(outros, lambda r: r["likes"] + 3 * r["comments"], 15)
outros.sort(key=lambda r: -r["x"])

campos = ("x", "views", "likes", "comments", "post_date", "url", "caption")
sai = {"perfil": perfil, "posts": len(R), "reels": len(reels), "anuncios": len(anuncios),
       "mediana_views": st.median(r["views"] for r in reels) if reels else 0,
       "reels_top": [{k: r[k] for k in campos} for r in organicos[:30]],
       "carrosseis_top": [{k: r[k] for k in campos if k != "views"} for r in outros[:15]]}
json.dump(sai, open("dados/viral_%s.json" % perfil, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("%s: %d posts, %d reels (%d anúncios), mediana %d views" % (perfil, len(R), len(reels), len(anuncios), sai["mediana_views"]))
for r in organicos[:30]:
    print("%5.1fx %9d C%-5d %s %s | %s" % (r["x"], r["views"], r["comments"], r["post_date"], r["url"], r["caption"][:90].replace("\n", " ")))
print("--- carrosséis")
for r in outros[:10]:
    print("%5.1fx L%-6d C%-5d %s %s | %s" % (r["x"], r["likes"], r["comments"], r["post_date"], r["url"], r["caption"][:120].replace("\n", " ")))
