#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Laboratório de Conteúdo — Coleta de perfis de referência (Apify)
----------------------------------------------------------------
A Meta não libera Business Discovery para este app, então os perfis de
referência vêm do Instagram Scraper do Apify (~US$ 0,0027 por post).
Traz também visualizações dos reels, que a Meta não dá.

Token do Apify:
  - na nuvem do Claude: segredo de rede "Bearer" para api.apify.com
  - no computador: APIFY_TOKEN no .env

Salva em dados/posts_<perfil>.json, no mesmo formato do coletar_posts.py.
Rodar:  python3 coletar_apify.py
"""
import os
import json
import time
import urllib.request
import urllib.error

API = "https://api.apify.com/v2"
ATOR = "apify~instagram-scraper"

PERFIS = ["tay.ldantas", "analisboa", "eltoneuler"]
POSTS_POR_PERFIL = 150
TETO_USD = 1.50  # o Apify para a execução se o custo passar disso

TIPOS = {"Video": "VIDEO", "Image": "IMAGE", "Sidecar": "CAROUSEL_ALBUM"}


def carregar_env(caminho=".env"):
    env = {}
    if not os.path.exists(caminho):
        return env
    with open(caminho, encoding="utf-8") as f:
        for linha in f:
            linha = linha.strip()
            if not linha or linha.startswith("#") or "=" not in linha:
                continue
            k, v = linha.split("=", 1)
            v = v.split("#", 1)[0].strip().strip('"').strip("'").replace("cole_aqui", "").strip()
            env[k.strip()] = v
    return env


def chamar(metodo, caminho, token, corpo=None):
    dados = json.dumps(corpo).encode("utf-8") if corpo is not None else None
    req = urllib.request.Request(API + caminho, data=dados, method=metodo)
    req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", "Bearer " + token)
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))


def normalizar(item):
    """Converte um post do Apify para o formato da Graph API usado no projeto."""
    return {
        "caption": item.get("caption"),
        "media_type": TIPOS.get(item.get("type"), item.get("type")),
        "media_product_type": "REELS" if item.get("productType") == "clips" else "FEED",
        "like_count": item.get("likesCount"),
        "comments_count": item.get("commentsCount"),
        "video_views": item.get("videoPlayCount") or item.get("videoViewCount"),
        "timestamp": item.get("timestamp"),
        "permalink": item.get("url"),
        "perfil": item.get("ownerUsername"),
    }


def main():
    token = os.environ.get("APIFY_TOKEN") or carregar_env().get("APIFY_TOKEN")
    entrada = {
        "directUrls": ["https://www.instagram.com/%s/" % p for p in PERFIS],
        "resultsType": "posts",
        "resultsLimit": POSTS_POR_PERFIL,
        "addParentData": False,
    }
    try:
        run = chamar("POST", "/acts/%s/runs?maxTotalChargeUsd=%s" % (ATOR, TETO_USD), token, entrada)["data"]
    except urllib.error.HTTPError as e:
        print("Erro %s ao iniciar o Apify: %s" % (e.code, e.read().decode("utf-8", "ignore")[:300]))
        return

    print("Coleta iniciada no Apify (pode levar alguns minutos)...")
    while run["status"] in ("READY", "RUNNING"):
        time.sleep(15)
        run = chamar("GET", "/actor-runs/" + run["id"], token)["data"]
        print("  status: %s" % run["status"])
    if run["status"] != "SUCCEEDED":
        print("A coleta terminou com status %s." % run["status"])

    itens = chamar("GET", "/datasets/%s/items?clean=true&format=json" % run["defaultDatasetId"], token)
    if isinstance(itens, dict):
        itens = itens.get("data", [])

    os.makedirs("dados", exist_ok=True)
    for perfil in PERFIS:
        posts = [normalizar(i) for i in itens if (i.get("ownerUsername") or "").lower() == perfil]
        posts.sort(key=lambda p: p["timestamp"] or "", reverse=True)
        with open("dados/posts_%s.json" % perfil, "w", encoding="utf-8") as f:
            json.dump({"username": perfil, "posts": posts}, f, ensure_ascii=False, indent=1)
        print("@%s: %d posts" % (perfil, len(posts)))
    print("Custo desta coleta: US$ %.2f" % (run.get("usageTotalUsd") or 0))


if __name__ == "__main__":
    main()
