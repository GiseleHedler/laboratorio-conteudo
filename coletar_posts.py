#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Laboratório de Conteúdo — Coleta de posts (API oficial da Meta)
---------------------------------------------------------------
Puxa os últimos posts de cada perfil via Business Discovery:
legenda, formato, data, curtidas, comentários e link.
Só funciona com perfis comerciais ou de criador.

Token da Meta (permissão instagram_basic + pages_show_list):
  - na nuvem do Claude: segredo de rede "Bearer" para graph.facebook.com
    (o token é anexado sozinho; o script não precisa vê-lo)
  - no computador: META_TOKEN no .env
  META_IG_USER_ID  (opcional) ID da sua conta comercial; se faltar, é descoberto pelo token

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

PERFIL_PROPRIO = "giselehedler"
PERFIS = [PERFIL_PROPRIO, "tay.ldantas", "analisboa", "eltoneuler"]
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


def buscar(caminho, params, token):
    """GET na Graph API. Sem token, conta com o segredo de rede da nuvem."""
    url = "%s/%s?%s" % (BASE, caminho, urllib.parse.urlencode(params))
    req = urllib.request.Request(url)
    if token:
        req.add_header("Authorization", "Bearer " + token)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


def chamar(ig_user_id, token, perfil, cursor=None):
    media = "media.after(%s).limit(50)" % cursor if cursor else "media.limit(50)"
    campos = "business_discovery.username(%s){username,name,biography,followers_count,media_count,%s{%s}}" % (
        perfil, media, CAMPOS_POST)
    return buscar(ig_user_id, {"fields": campos}, token)["business_discovery"]


def coletar_proprio(ig_user_id, token):
    """O próprio perfil é lido direto da conta, sem Business Discovery."""
    info = buscar(ig_user_id, {"fields": "username,name,biography,followers_count,media_count"}, token)
    info.pop("id", None)
    posts, params = [], {"fields": CAMPOS_POST, "limit": 50}
    while len(posts) < POSTS_POR_PERFIL:
        pagina = buscar(ig_user_id + "/media", params, token)
        posts += pagina.get("data", [])
        cursor = pagina.get("paging", {}).get("cursors", {}).get("after")
        if not cursor or not pagina.get("data"):
            break
        params = dict(params, after=cursor)
    info["posts"] = posts[:POSTS_POR_PERFIL]
    return info


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


def descobrir_ig_user_id(token):
    """Acha o ID da conta comercial do Instagram ligada às páginas do token."""
    paginas = buscar("me/accounts", {"fields": "instagram_business_account{id,username}"}, token).get("data", [])
    contas = [p["instagram_business_account"] for p in paginas if p.get("instagram_business_account")]
    for c in contas:
        print("Conta do Instagram encontrada: @%s (id %s)" % (c.get("username"), c["id"]))
    for c in contas:
        if c.get("username") == PERFIL_PROPRIO:
            return c["id"]
    return contas[0]["id"] if contas else None


def main():
    env = carregar_env()
    token = os.environ.get("META_TOKEN") or env.get("META_TOKEN")
    ig_user_id = os.environ.get("META_IG_USER_ID") or env.get("META_IG_USER_ID")
    if not ig_user_id:
        try:
            ig_user_id = descobrir_ig_user_id(token)
        except urllib.error.HTTPError as e:
            print("Erro %s ao buscar a conta do Instagram: %s" % (e.code, e.read().decode("utf-8", "ignore")[:300]))
            return
        except urllib.error.URLError as e:
            print("Não consegui chegar na Meta (%s)." % e.reason)
            return
        if not ig_user_id:
            print("Nenhuma conta comercial do Instagram ligada a este token.")
            print("-> Confira se o Instagram está ligado a uma Página do Facebook e se deu permissão a ela.")
            return

    os.makedirs("dados", exist_ok=True)
    for perfil in PERFIS:
        try:
            if perfil == PERFIL_PROPRIO:
                info = coletar_proprio(ig_user_id, token)
            else:
                info = coletar(ig_user_id, token, perfil)
        except urllib.error.HTTPError as e:
            erro = e.read().decode("utf-8", "ignore")[:300]
            print("@%s: erro %s — %s" % (perfil, e.code, erro))
            if "permission" in erro.lower() or e.code in (400, 403):
                print("   -> A Meta não liberou este app para ver outros perfis (Business Discovery).")
            continue
        except urllib.error.URLError as e:
            print("Não consegui chegar na Meta (%s)." % e.reason)
            return
        with open("dados/posts_%s.json" % perfil, "w", encoding="utf-8") as f:
            json.dump(info, f, ensure_ascii=False, indent=1)
        print("@%s: %d posts (%s seguidores)" % (perfil, len(info["posts"]), info["followers_count"]))


if __name__ == "__main__":
    main()
