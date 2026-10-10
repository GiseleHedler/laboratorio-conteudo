#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Laboratório de Conteúdo — Anúncios ativos (Biblioteca de Anúncios da Meta)
-------------------------------------------------------------------------
Busca os anúncios ativos no Brasil de um nome na Biblioteca de Anúncios,
via Apify (~US$ 0,00075 por anúncio), para estudar o funil de quem anuncia.

Token do Apify: segredo de rede "Bearer" para api.apify.com na nuvem,
ou APIFY_TOKEN no .env no computador.

Salva em dados/anuncios_<slug>.json
Rodar:  python3 coletar_anuncios.py "Ana Lisboa" [limite]
        python3 coletar_anuncios.py pagina:387087041810736 [limite]   (todos os anúncios da página, ativos e antigos)
"""
import os
import sys
import json
import time
import urllib.parse
import urllib.request

API = "https://api.apify.com/v2"
ATOR = "curious_coder~facebook-ads-library-scraper"
TETO_USD = 0.40


def chamar(metodo, caminho, corpo=None):
    dados = json.dumps(corpo).encode("utf-8") if corpo is not None else None
    req = urllib.request.Request(API + caminho, data=dados, method=metodo)
    req.add_header("Content-Type", "application/json")
    token = os.environ.get("APIFY_TOKEN")
    if token:
        req.add_header("Authorization", "Bearer " + token)
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))


def main():
    nome = sys.argv[1]
    limite = int(sys.argv[2]) if len(sys.argv) > 2 else 150
    if nome.startswith("pagina:"):
        params = {"active_status": "all", "ad_type": "all", "country": "BR",
                  "view_all_page_id": nome.split(":", 1)[1], "search_type": "page", "media_type": "all"}
    else:
        params = {"active_status": "active", "ad_type": "all", "country": "BR",
                  "q": nome, "search_type": "keyword_unordered", "media_type": "all"}
    busca = "https://www.facebook.com/ads/library/?" + urllib.parse.urlencode(params)
    entrada = {"urls": [{"url": busca}], "count": limite, "scrapeAdDetails": False}
    run = chamar("POST", "/acts/%s/runs?maxTotalChargeUsd=%s" % (ATOR, TETO_USD), entrada)["data"]
    print("Buscando anúncios de \"%s\"..." % nome)
    while run["status"] in ("READY", "RUNNING"):
        time.sleep(10)
        run = chamar("GET", "/actor-runs/" + run["id"])["data"]
    itens = chamar("GET", "/datasets/%s/items?clean=true&format=json" % run["defaultDatasetId"])
    slug = nome.lower().replace(" ", "_").replace(":", "_")
    os.makedirs("dados", exist_ok=True)
    with open("dados/anuncios_%s.json" % slug, "w", encoding="utf-8") as f:
        json.dump(itens, f, ensure_ascii=False, indent=1)
    print("%d anúncios (status %s, custo US$ %.2f)" % (len(itens), run["status"], run.get("usageTotalUsd") or 0))


if __name__ == "__main__":
    main()
