#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Central de Comando — Teste do Jev (TypeSafe)
--------------------------------------------
Manda 6 comentários de exemplo pro Jev e mostra, pra cada um:
  - tipo do comentário (escolha entre opções)
  - chance de ser intenção de compra (sim/não com probabilidade)
  - urgência de resposta (nota 0 a 2)
Objetivo: você conferir se o Jev decide igual você decidiria.

Lê a chave de TYPESAFE_API_KEY (variável de ambiente ou .env).
Rodar:  python3 testar_jev.py
"""
import os
import json
import urllib.request
import urllib.error

API_URL = "https://api.typesafe.ai/v1/systemone"
MODEL = "jev-latest"

# Troque pelos comentários reais do seu Instagram pra um teste de verdade.
COMENTARIOS = [
    "Quanto custa a pós? Parcela no cartão?",
    "Amei esse conteúdo, salvei aqui!",
    "Comprei faz 10 dias e até agora não recebi o acesso, ninguém responde",
    "Isso tem comprovação científica ou é achismo?",
    "Tô pensando em entrar na próxima turma, quando abre?",
    "Muito caro pro que entrega",
]

PERGUNTAS = {
    "tipo": {
        "type": "choice",
        "instructions": "Que tipo de comentário é `comentario`, deixado num post de Instagram de uma marca de educação em saúde?",
        "criteria": {
            "duvida": "Pergunta sobre o conteúdo ou o tema do post",
            "interesse_compra": "Pergunta sobre preço, turma, matrícula ou como comprar",
            "objecao": "Resistência à compra: acha caro, duvida da qualidade ou da credibilidade",
            "reclamacao": "Cliente com problema de acesso, entrega ou atendimento",
            "elogio": "Elogio ou reação positiva sem pergunta",
        },
    },
    "quer_comprar": {
        "type": "noul",
        "instructions": "A pessoa que escreveu `comentario` demonstra intenção de comprar um curso ou produto.",
    },
    "urgencia": {
        "type": "score",
        "instructions": "Com que urgência a equipe deve responder `comentario`?",
        "criteria": [
            "Pode esperar ou nem precisa de resposta",
            "Responder hoje: é uma oportunidade de venda ou uma dúvida legítima",
            "Responder já: cliente pagante com problema, risco de reclamação pública",
        ],
    },
}


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


def perguntar_jev(api_key, comentario):
    corpo = json.dumps({
        "model": MODEL,
        "state": {"comentario": comentario},
        "questions": PERGUNTAS,
    }).encode("utf-8")
    req = urllib.request.Request(API_URL, data=corpo, method="POST")
    req.add_header("Authorization", "Bearer " + api_key)
    req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


def main():
    api_key = os.environ.get("TYPESAFE_API_KEY") or carregar_env().get("TYPESAFE_API_KEY")
    if not api_key:
        print("Falta TYPESAFE_API_KEY (no .env ou nas variáveis do ambiente).")
        return

    for comentario in COMENTARIOS:
        try:
            resp = perguntar_jev(api_key, comentario)
        except urllib.error.HTTPError as e:
            print("Erro %s do Jev: %s" % (e.code, e.read().decode("utf-8", "ignore")[:200]))
            if e.code in (401, 403):
                print("-> Chave recusada. Confira se colou a chave inteira, sem espaços.")
            return
        except urllib.error.URLError as e:
            print("Não consegui chegar no Jev (%s)." % e.reason)
            print("-> Se estiver na nuvem do Claude, libere typesafe.ai em Network access.")
            return

        r = resp["answers"]
        tipo, compra, urg = r["tipo"], r["quer_comprar"], r["urgencia"]
        print("\n\"%s\"" % comentario)
        print("  tipo:        %s (confiança %.0f%%)" % (tipo["choice"], tipo["confidence"] * 100))
        print("  quer comprar: %.0f%%" % (compra["noul"] * 100))
        print("  urgência:    %.1f de 2" % urg["score"])

    print("\nConfira: o Jev decidiu igual você decidiria? Se errou, anote quais.")


if __name__ == "__main__":
    main()
