#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Laboratório de Conteúdo — Coleta de posts (API oficial da Meta)
---------------------------------------------------------------
Puxa os últimos posts de cada perfil via Business Discovery:
legenda, formato, data, curtidas, comentários e link.
Só funciona com perfis comerciais ou de criador.

Lê do .env:
  META_TOKEN       token com permissão instagram_basic (+ pages_show_list)
  META_IG_USER_ID  ID da SUA conta comercial do Instagram (não é o @)

Salva em dados/posts_<perfil>.json
Rodar:  python3 coletar_posts.py
"""
import os
import json
import urllib.parse
import urllib.request
import urllib.error

API_VERSION = "v21.0"
BASE = "https://graph.facebook.com/" + API_VERSION

PERFIS = ["tay.ldantas", "analisboa", "eltoneuler"]
POSTS_POR_PERFIL = 150

CAMPOS_POST = "caption,media_type,media_product_type,like_count,comments_count,timestamp,permalink"


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


def chamar(ig_user_id, token, perfil, cursor=None):
    media = "media.after(%s).limit(50)" % cursor if cursor else "media.limit(50)"
    campos = "business_discovery.username(%s){username,name,biography,followers_count,media_count,%s{%s}}" % (
        perfil, media, CAMPOS_POST)
    url = "%s/%s?%s" % (BASE, ig_user_id, urllib.parse.urlencode({"fields": campos, "access_token": token}))
    with urllib.request.urlopen(url, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))["business_discovery"]


def coletar(ig_user_id, token, perfil):
    posts, cursor, info = [], None, None
    while len(posts) < POSTS_POR_PERFIL:
        bd = chamar(ig_user_id, token, perfil, cursor)
        if info is None:
            info = {k: bd.get(k) for k in ("username", "name", "biography", "followers_count", "media_count")}
        media = bd.get("media", {})
        posts += media.get("data", [])
        cursor = media.get("paging", {}).get("cursors", {}).get("after")
        if not cursor or not media.get("data"):
            break
    info["posts"] = posts[:POSTS_POR_PERFIL]
    return info


def main():
    env = carregar_env()
    token = os.environ.get("META_TOKEN") or env.get("META_TOKEN")
    ig_user_id = os.environ.get("META_IG_USER_ID") or env.get("META_IG_USER_ID")
    if not token or not ig_user_id:
        print("Faltam no .env: META_TOKEN e/ou META_IG_USER_ID.")
        return

    os.makedirs("dados", exist_ok=True)
    for perfil in PERFIS:
        try:
            info = coletar(ig_user_id, token, perfil)
        except urllib.error.HTTPError as e:
            erro = e.read().decode("utf-8", "ignore")[:300]
            print("@%s: erro %s — %s" % (perfil, e.code, erro))
            if "permission" in erro.lower() or e.code in (400, 403):
                print("   -> O token precisa de instagram_basic, ou o perfil não é comercial/criador.")
            continue
        except urllib.error.URLError as e:
            print("Não consegui chegar na Meta (%s)." % e.reason)
            return
        with open("dados/posts_%s.json" % perfil, "w", encoding="utf-8") as f:
            json.dump(info, f, ensure_ascii=False, indent=1)
        print("@%s: %d posts (%s seguidores)" % (perfil, len(info["posts"]), info["followers_count"]))


if __name__ == "__main__":
    main()
