#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Laboratório de Conteúdo — Transcrição de reels (Apify)
------------------------------------------------------
Transcreve a fala de reels pelo ator steadyfetch/instagram-reel-transcript-scraper
(~US$ 0,015 por reels; a transcrição roda no Apify, sem baixar nada aqui).

Entradas:
  dados/reels_para_transcrever.json  lista de links de reels (opcional)
  argumentos: @perfil:N  para incluir os N reels mais recentes de um perfil

Token do Apify: segredo de rede "Bearer" para api.apify.com na nuvem,
ou APIFY_TOKEN no ambiente no computador.

Salva em dados/transcricoes.json (acumula entre execuções).
Rodar:  python3 transcrever_reels.py @tay.ldantas:3
"""
import os
import sys
import json
import time
import urllib.request

API = "https://api.apify.com/v2"
ATOR = "steadyfetch~instagram-reel-transcript-scraper"
TETO_USD = 1.00
SAIDA = "dados/transcricoes.json"


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
    links = []
    if os.path.exists("dados/reels_para_transcrever.json"):
        links = json.load(open("dados/reels_para_transcrever.json", encoding="utf-8"))
    handles, maximo = [], 0
    for arg in sys.argv[1:]:
        nome, _, n = arg.lstrip("@").partition(":")
        handles.append(nome)
        maximo = max(maximo, int(n or 3))

    entrada = {"reelUrls": links, "maxItems": len(links) + maximo * len(handles)}
    if handles:
        entrada.update({"handles": handles, "maxReelsPerHandle": maximo})
    run = chamar("POST", "/acts/%s/runs?maxTotalChargeUsd=%s" % (ATOR, TETO_USD), entrada)["data"]
    print("Transcrevendo %d reels..." % entrada["maxItems"])
    while run["status"] in ("READY", "RUNNING"):
        time.sleep(15)
        run = chamar("GET", "/actor-runs/" + run["id"])["data"]
    itens = chamar("GET", "/datasets/%s/items?clean=true&format=json" % run["defaultDatasetId"])

    salvas = json.load(open(SAIDA, encoding="utf-8")) if os.path.exists(SAIDA) else []
    salvas += itens
    os.makedirs("dados", exist_ok=True)
    with open(SAIDA, "w", encoding="utf-8") as f:
        json.dump(salvas, f, ensure_ascii=False, indent=1)
    print("%d transcrições (status %s, custo US$ %.2f)" % (len(itens), run["status"], run.get("usageTotalUsd") or 0))


if __name__ == "__main__":
    main()
