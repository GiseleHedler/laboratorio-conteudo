#!/usr/bin/env python3
"""Análise da FSA: curva por trimestre, collab x exclusivo, venda x conteúdo.
Mesma métrica do analisar_viral.py: reel = views ÷ mediana dos 40 reels vizinhos;
carrossel/foto = (curtidas + 3x comentários) ÷ mediana dos 30 vizinhos. Reel com menos de
8 curtidas por mil views = provável anúncio, fica de fora.
Uso: python3 fsa/analisar_fsa.py dados/viral_fsa_saudeavancada.csv dados/viral_gabrieldecarvalho_professor.csv
"""
import csv, re, sys, statistics as st, datetime as dt, collections

VENDA = re.compile(r"matr[ií]cula|inscri[çc]|\bvagas?\b|black ?friday|desconto|\blote\b|r\$|garanta|cupom|parcel|lista de espera|\bturma\b|\boferta\b|investimento", re.I)
CONVITE = re.compile(r"\blives?\b|aula gratuita|aul[ãa]o|ao vivo|imers[ãa]o|congresso|\bevento\b|workshop|masterclass|webinar", re.I)

def ler(arq):
    R = list(csv.DictReader(open(arq, encoding="utf-8")))
    for r in R:
        r["d"] = dt.datetime.strptime(r["post_date"], "%m/%d/%Y")
        for k in ("likes", "comments", "views"):
            try: r[k] = int(float(r[k] or 0))
            except ValueError: r[k] = 0
        c = r["caption"]
        r["tipo"] = "venda" if VENDA.search(c) else ("convite" if CONVITE.search(c) else "conteudo")
    return R

def ranquear(itens, valor, viz):
    itens.sort(key=lambda r: r["d"])
    for i, r in enumerate(itens):
        m = st.median(valor(x) for x in itens[max(0, i - viz):i + viz + 1]) or 1
        r["x"] = valor(r) / m

def med(v): return "%.1fx" % st.median(v) if v else "-"

def tri(d): return "%d T%d" % (d.year, (d.month - 1) // 3 + 1)

arqs = sys.argv[1:3]
P = {a: ler(a) for a in arqs}
urls = [set(r["url"] for r in P[a]) for a in arqs]
comuns = urls[0] & urls[1]

for a in arqs:
    R = P[a]
    reels = [r for r in R if r["type"] == "clips" and r["views"] > 0]
    ranquear(reels, lambda r: r["views"], 20)
    org = [r for r in reels if r["likes"] * 1000 / r["views"] >= 8]
    outros = [r for r in R if r["type"] != "clips"]
    ranquear(outros, lambda r: r["likes"] + 3 * r["comments"], 15)
    print("\n#####", a)
    print("posts %d | reels %d (anúncios fora: %d) | carrosséis/fotos %d | collab %d (%.0f%%)" % (
        len(R), len(reels), len(reels) - len(org), len(outros),
        sum(r["url"] in comuns for r in R), 100 * sum(r["url"] in comuns for r in R) / len(R)))
    print("\nCurva (reels orgânicos): trimestre | reels | mediana views | % venda no feed (todos os posts)")
    g = collections.defaultdict(list); gt = collections.defaultdict(list)
    for r in org: g[tri(r["d"])].append(r["views"])
    for r in R: gt[tri(r["d"])].append(r["tipo"] == "venda")
    for k in sorted(g, key=lambda s: (int(s[:4]), s[-1])):
        print("  %s | %3d | %7d | %3.0f%%" % (k, len(g[k]), st.median(g[k]), 100 * sum(gt[k]) / len(gt[k])))
    print("\nVenda x conteúdo (multiplicador mediano):")
    for t in ("conteudo", "convite", "venda"):
        rr = [r for r in org if r["tipo"] == t]; oo = [r for r in outros if r["tipo"] == t]
        print("  %-9s reels %3d %s | carrosséis/fotos %3d %s" % (t, len(rr), med([r["x"] for r in rr]), len(oo), med([r["x"] for r in oo])))
    print("\nCollab x exclusivo (multiplicador mediano):")
    for nome, f in (("collab", lambda r: r["url"] in comuns), ("exclusivo", lambda r: r["url"] not in comuns)):
        rr = [r for r in org if f(r)]; oo = [r for r in outros if f(r)]
        print("  %-9s reels %3d %s | carrosséis/fotos %3d %s" % (nome, len(rr), med([r["x"] for r in rr]), len(oo), med([r["x"] for r in oo])))
    print("\nPosts de venda com melhor desempenho:")
    for r in sorted([r for r in org + outros if r["tipo"] == "venda"], key=lambda r: -r["x"])[:8]:
        print("  %5.1fx %-18s %s %s | %s" % (r["x"], r["type"], r["post_date"], r["url"], r["caption"][:80].replace("\n", " ")))
    print("\nBlack Friday 2025 (nov/2025):")
    for r in sorted([r for r in R if r["d"].year == 2025 and r["d"].month == 11 and re.search("black", r["caption"], re.I)], key=lambda r: r["d"]):
        print("  %5.1fx %-18s %s views %6d L%5d C%4d | %s" % (r.get("x", 0), r["type"], r["post_date"], r["views"], r["likes"], r["comments"], r["caption"][:70].replace("\n", " ")))
