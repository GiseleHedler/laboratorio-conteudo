#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Laboratório de Conteúdo: mecanismo de gancho dos reels com o Jev (TypeSafe)
--------------------------------------------------------------------------
Para cada reel orgânico de dados/vf_<perfil>.csv (export do Viral Finder), pergunta ao Jev
qual mecanismo de gancho a abertura usa, a intenção e se fala com quem prescreve.
Usa a fala transcrita (dados/transcricoes.json) quando existe; senão, a legenda.

Chave do Jev: segredo de rede "Bearer" para api.typesafe.ai na nuvem, ou TYPESAFE_API_KEY no ambiente.
Salva em dados/ganchos_jev.json (retoma de onde parou).
Rodar:  python3 rotular_ganchos_jev.py perfil1 perfil2 ... [--limite N]
"""
import csv, json, os, sys, urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor

API_URL = "https://api.typesafe.ai/v1/systemone"
SAIDA = "dados/ganchos_jev.json"
PERGUNTAS = {
    "mecanismo": {"type": "choice",
        "instructions": "Que mecanismo a abertura de `texto` (primeiras frases de um vídeo ou legenda de uma marca de saúde ou suplemento) usa para prender a atenção?",
        "criteria": {
            "denuncia_fraude": "Denuncia fraude, falsificação, produto adulterado ou algo escondido que engana o consumidor",
            "numero_impacto": "Abre com um número, dado ou estudo que choca",
            "mito_desmontado": "Contradiz uma crença comum ou um conselho popular (não é bem assim, você está fazendo errado)",
            "noticia_reacao": "Reage a uma notícia, reportagem, diretriz ou acontecimento recente",
            "pergunta_duvida": "Abre com a pergunta ou dúvida frequente do público (pode tomar X? qual o melhor horário?)",
            "lista": "Promete uma lista, um ranking ou passos",
            "receita": "Receita ou preparo de comida ou bebida",
            "uso_proprio": "A pessoa conta o que ela mesma usa, toma ou faz na própria rotina",
            "historia_pessoal": "Conta uma história ou experiência da própria vida",
            "depoimento_terceiro": "Cliente ou influenciadora conta que recebeu, provou ou gostou",
            "sintoma_identificacao": "Lista sintomas ou sinais para a pessoa se reconhecer",
            "oferta_lancamento": "Promoção, lançamento, desconto, sorteio ou convite para comprar",
            "institucional": "Apresenta a marca, evento, bastidor ou data comemorativa",
            "humor_trend": "Humor, trend, meme",
        }},
    "fala_com_prescritor": {"type": "noul",
        "instructions": "`texto` se dirige a profissionais de saúde que prescrevem (nutricionistas, médicos), e não ao consumidor final."},
    "forca_gancho": {"type": "score",
        "instructions": "Quão forte é a abertura de `texto` para fazer alguém parar de rolar o feed?",
        "criteria": ["Fraca: genérica ou previsível", "Média: algum interesse", "Forte: específica, surpreendente, difícil de ignorar"]},
}

def perguntar(texto):
    corpo = json.dumps({"model": "jev-latest", "state": {"texto": texto[:1500]}, "questions": PERGUNTAS}).encode("utf-8")
    req = urllib.request.Request(API_URL, data=corpo, method="POST")
    req.add_header("Content-Type", "application/json")
    if os.environ.get("TYPESAFE_API_KEY"):
        req.add_header("Authorization", "Bearer " + os.environ["TYPESAFE_API_KEY"])
    with urllib.request.urlopen(req, timeout=90) as r:
        return json.loads(r.read().decode("utf-8"))

def rotular(item):
    url, texto = item
    try:
        r = perguntar(texto)
    except urllib.error.HTTPError as e:
        return url, {"erro": "%s %s" % (e.code, e.read().decode("utf-8", "ignore")[:200])}
    except Exception as e:
        return url, {"erro": str(e)[:200]}
    a = r["answers"]
    return url, {"mecanismo": a["mecanismo"]["choice"], "conf": round(a["mecanismo"]["confidence"], 2),
                 "prescritor": round(a["fala_com_prescritor"]["noul"], 2), "forca": round(a["forca_gancho"]["score"], 2),
                 "tokens": r.get("usage", {})}

def main():
    args = sys.argv[1:]
    limite = None
    if "--limite" in args:
        i = args.index("--limite"); limite = int(args[i + 1]); args = args[:i] + args[i + 2:]
    trans = {}
    if os.path.exists("dados/transcricoes.json"):
        for t in json.load(open("dados/transcricoes.json", encoding="utf-8")):
            sc = t.get("shortCode") or (t.get("postUrl") or "").rstrip("/").split("/")[-1]
            if t.get("transcript"): trans[sc] = t["transcript"]
    feitos = json.load(open(SAIDA, encoding="utf-8")) if os.path.exists(SAIDA) else {}
    pend = []
    for p in args:
        for r in csv.DictReader(open("dados/vf_%s.csv" % p, encoding="utf-8")):
            v, l = float(r["views"] or 0), float(r["likes"] or 0)
            if r["type"] != "clips" or v <= 0 or l * 1000 / v < 8: continue
            if r["url"] in feitos and "erro" not in feitos[r["url"]]: continue
            sc = r["url"].rstrip("/").split("/")[-1]
            texto = trans.get(sc, "")[:600] or r["caption"]
            if texto.strip(): pend.append((r["url"], texto))
    if limite: pend = pend[:limite]
    print("Rotulando %d reels com o Jev..." % len(pend))
    with ThreadPoolExecutor(6) as ex:
        for i, (url, rot) in enumerate(ex.map(rotular, pend), 1):
            feitos[url] = rot
            if "erro" in rot and i < 4: print("  erro:", rot["erro"])
            if i % 100 == 0: print("  %d/%d" % (i, len(pend)))
    json.dump(feitos, open(SAIDA, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    ok = [r for r in feitos.values() if "erro" not in r]
    tin = sum((r.get("tokens") or {}).get("input_tokens") or 0 for r in ok)
    tout = sum((r.get("tokens") or {}).get("output_tokens") or 0 for r in ok)
    print("Pronto: %d rotulados. Tokens: %d entrada, %d saída." % (len(ok), tin, tout))

if __name__ == "__main__":
    main()
