#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Laboratório de Conteúdo — Rotulagem dos posts com o Jev (TypeSafe)
------------------------------------------------------------------
Para cada post coletado (dados/posts_*.json), pergunta ao Jev:
gancho, tema, público, emoção, intenção, se fala direto com a seguidora,
se conta história própria e a força do gancho.

O Jev só lê a LEGENDA: não assiste o vídeo nem vê a imagem.

Chave do Jev: segredo de rede "Bearer" para api.typesafe.ai na nuvem,
ou TYPESAFE_API_KEY no .env no computador.

Salva em dados/rotulos.json (retoma de onde parou se rodar de novo).
Rodar:  python3 rotular_jev.py [limite]
"""
import os
import sys
import glob
import json
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor

API_URL = "https://api.typesafe.ai/v1/systemone"
MODEL = "jev-latest"
SAIDA = "dados/rotulos.json"
TRABALHADORES = 6

PERGUNTAS = {
    "gancho": {
        "type": "choice",
        "instructions": "Como a primeira frase de `legenda` tenta prender a atenção de quem rola o feed do Instagram?",
        "criteria": {
            "pergunta_direta": "Faz uma pergunta para a pessoa que está lendo",
            "afirmacao_provocativa": "Afirmação forte, contraintuitiva ou que confronta uma crença",
            "historia_pessoal": "Começa contando algo que aconteceu com quem escreve",
            "lista_dica": "Promete uma lista, passos, dicas ou técnica",
            "curiosidade_dado": "Abre com um fato, dado, notícia ou caso de outra pessoa",
            "humor": "Piada, ironia ou situação engraçada",
            "convite_venda": "Abre convidando para produto, evento, live ou inscrição",
            "sem_gancho": "Legenda vazia, curta demais ou sem frase de abertura clara",
        },
    },
    "tema": {
        "type": "choice",
        "instructions": "Qual é o tema principal de `legenda`?",
        "criteria": {
            "luto_perda": "Morte, luto, perdas e despedidas",
            "relacionamentos": "Casamento, amor, traição, relações afetivas",
            "autoestima_culpa": "Autoestima, culpa, provar valor, se perder de si, autocobrança",
            "familia_maternidade": "Pais, filhos, família, maternidade, herança familiar",
            "espiritualidade": "Deus, fé, alma, propósito espiritual, consciência",
            "saude_corpo": "Doença, tratamento, corpo, hábitos de saúde",
            "dinheiro_negocios": "Dinheiro, empresa, vendas, empreender, riqueza",
            "mente_comportamento": "Mente, hábitos, foco, inteligência, comportamento, constância",
            "posicionamento_comunicacao": "Posicionamento, imagem pessoal, comunicação, marca",
            "outro": "Nenhum dos temas acima",
        },
    },
    "publico": {
        "type": "choice",
        "instructions": "Para quem `legenda` parece ter sido escrita?",
        "criteria": {
            "mulher_madura": "Mulheres de 40 anos ou mais, ou que já viveram muito (casamento longo, filhos criados, 'senhora')",
            "mulher_geral": "Mulheres em geral, sem marca de idade",
            "empreendedores": "Quem empreende, vende ou quer ganhar dinheiro",
            "publico_geral": "Qualquer pessoa",
        },
    },
    "emocao": {
        "type": "choice",
        "instructions": "Qual emoção `legenda` mais provoca em quem lê?",
        "criteria": {
            "dor_identificacao": "A pessoa se reconhece numa dor ou ferida",
            "esperanca_alivio": "Alívio, acolhimento, esperança de mudança",
            "inspiracao_ambicao": "Vontade de crescer, conquistar, agir",
            "provocacao_incomodo": "Incômodo, confronto, choque de realidade",
            "diversao": "Riso, leveza",
            "informacao": "Aprendizado neutro, sem emoção forte",
        },
    },
    "intencao": {
        "type": "choice",
        "instructions": "O que `legenda` quer que a pessoa faça?",
        "criteria": {
            "conectar": "Só gerar identificação e conexão, sem pedir ação",
            "educar": "Ensinar algo útil",
            "engajar": "Pedir comentário, compartilhamento, marcação ou salvamento",
            "convidar_gratuito": "Convidar para live, aula, evento ou material gratuito",
            "vender": "Oferecer produto, curso, mentoria ou evento pago",
        },
    },
    "fala_com_seguidora": {
        "type": "noul",
        "instructions": "`legenda` se dirige diretamente a quem lê, como uma conversa com 'você' sobre a vida dessa pessoa.",
    },
    "historia_propria": {
        "type": "noul",
        "instructions": "Quem escreveu `legenda` conta uma experiência real da própria vida.",
    },
    "forca_gancho": {
        "type": "score",
        "instructions": "Quão forte é a primeira frase de `legenda` para fazer alguém parar de rolar o feed?",
        "criteria": [
            "Fraca: genérica, previsível ou sem gancho",
            "Média: desperta algum interesse, mas é comum",
            "Forte: específica, emocional ou surpreendente; difícil de ignorar",
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


API_KEY = os.environ.get("TYPESAFE_API_KEY") or carregar_env().get("TYPESAFE_API_KEY")


def perguntar(post):
    corpo = json.dumps({
        "model": MODEL,
        "state": {"legenda": (post.get("caption") or "")[:2000], "formato": post.get("media_type")},
        "questions": PERGUNTAS,
    }).encode("utf-8")
    req = urllib.request.Request(API_URL, data=corpo, method="POST")
    req.add_header("Content-Type", "application/json")
    if API_KEY:
        req.add_header("Authorization", "Bearer " + API_KEY)
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))


def rotular(item):
    chave, post = item
    try:
        resp = perguntar(post)
    except urllib.error.HTTPError as e:
        return chave, {"erro": "%s %s" % (e.code, e.read().decode("utf-8", "ignore")[:200])}
    except Exception as e:  # rede, timeout
        return chave, {"erro": str(e)[:200]}
    r = resp["answers"]
    rotulo = {nome: r[nome]["choice"] for nome in ("gancho", "tema", "publico", "emocao", "intencao")}
    rotulo["confianca"] = {nome: round(r[nome]["confidence"], 2) for nome in ("gancho", "tema", "publico", "emocao", "intencao")}
    rotulo["fala_com_seguidora"] = round(r["fala_com_seguidora"]["noul"], 2)
    rotulo["historia_propria"] = round(r["historia_propria"]["noul"], 2)
    rotulo["forca_gancho"] = round(r["forca_gancho"]["score"], 2)
    rotulo["tokens"] = resp.get("usage", {})
    return chave, rotulo


def main():
    limite = int(sys.argv[1]) if len(sys.argv) > 1 else None
    rotulos = {}
    if os.path.exists(SAIDA):
        with open(SAIDA, encoding="utf-8") as f:
            rotulos = json.load(f)

    pendentes = []
    for arquivo in sorted(glob.glob("dados/posts_*.json")):
        with open(arquivo, encoding="utf-8") as f:
            dados = json.load(f)
        for post in dados["posts"]:
            chave = post["permalink"]
            if chave not in rotulos or "erro" in rotulos[chave]:
                pendentes.append((chave, post))
    if limite:
        pendentes = pendentes[:limite]
    print("Rotulando %d posts com o Jev..." % len(pendentes))

    erros = 0
    with ThreadPoolExecutor(TRABALHADORES) as ex:
        for i, (chave, rotulo) in enumerate(ex.map(rotular, pendentes), 1):
            rotulos[chave] = rotulo
            if "erro" in rotulo:
                erros += 1
                if erros <= 3:
                    print("  erro: %s" % rotulo["erro"])
            if i % 50 == 0:
                print("  %d/%d" % (i, len(pendentes)))

    with open(SAIDA, "w", encoding="utf-8") as f:
        json.dump(rotulos, f, ensure_ascii=False, indent=1)
    ok = [r for r in rotulos.values() if "erro" not in r]
    entrada = sum((r.get("tokens") or {}).get("input_tokens") or 0 for r in ok)
    saida = sum((r.get("tokens") or {}).get("output_tokens") or 0 for r in ok)
    print("Pronto: %d rotulados, %d erros. Tokens: %d de entrada, %d de saída." % (len(ok), erros, entrada, saida))


if __name__ == "__main__":
    main()
