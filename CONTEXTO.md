# Contexto do projeto (para retomar em sessões novas)

## Objetivo
Descobrir o posicionamento da Gisele no Instagram pessoal (@giselehedler) e
aprender, com perfis que comunicam bem, como comunicar dentro desse
posicionamento — para começar a vender pelo Instagram, que hoje quase não vende.

## O que já se sabe
- Fala de vida, ser humano melhor, empresa e saúde; sente o posicionamento nebuloso.
- Produto em criação: um método próprio baseado no material do Seth
  (Jane Roberts — "suas crenças criam sua realidade") + vivências dela.
  Ainda sem nome nem formato.
- Hipótese: a lente do Seth pode ser o fio condutor que une todos os temas.
- Compradores atuais: 40+. Ex.: mentoria de R$ 20 mil para uma senhora de 68
  anos que já fez dois TDLs (eventos presenciais); busca conexão com Deus,
  espiritualidade, ser um ser humano melhor.
- Hipótese: a venda alta acontece depois de convivência ao vivo; o Instagram
  talvez deva levar para a primeira experiência, não vender direto.
- Cuidados: não vender "Seth" na manchete (ninguém conhece); diferenciar da
  "lei da atração"; cuidado com promessas de saúde; não chamar de psicanálise;
  direitos autorais dos livros.

## Perfis
- @giselehedler (próprio)
- @tay.ldantas — referência favorita: jeito de falar, conexão, cresceu muito rápido
- @analisboa — desenvolvimento pessoal feminino, constelação familiar, vende muito
- @eltoneuler — comunidade forte, fatura muito
- Falta: alguém que fale com mulheres 40+ sobre espiritualidade e venda bem.

## Plano
1. Coletar posts (coletar_posts.py, Business Discovery da Meta).
2. Achar campeões: engajamento vs. média do próprio perfil (código).
3. Jev rotula cada post: tema, formato, gancho, ângulo de posicionamento,
   porta de entrada (dor, desejo, espiritualidade, saúde, dinheiro), CTA.
4. Padrões dos campeões (código).
5. Claude analisa a fundo e propõe 2–3 posicionamentos.
6. Depois: funil (Biblioteca de Anúncios da Meta, link da bio).

## Perguntas em aberto para a Gisele
- O que mudou concretamente na vida dela aplicando o Seth?
- Como as pessoas reagiram quando ela falou dessas ideias?
- Qual dor leva alguém a precisar disso?
- Curso para transformação pessoal ou formação para aplicar com outros?

## Chaves (segredos do ambiente)
Segredos de rede "Bearer" no ambiente: um para api.typesafe.ai (Jev) e um para graph.facebook.com (Meta). Os scripts não leem as chaves: o proxy anexa o cabeçalho Authorization sozinho. No computador, use TYPESAFE_API_KEY e META_TOKEN no .env.

## Atualizações (10/10/2026)
- Escada: Quinta da Mente (grátis, ao vivo) → Integra (R$ 39/mês, ~100 aulas gravadas, ~10 assinantes) → Curso 12 semanas → TDL (~R$ 7 mil, presencial) → Mentoria R$ 20 mil (aplicação) → formação (futuro). Desafio "A Frase" como isca antes da Quinta.
- Livro: depois do curso, a partir do conteúdo do curso.
- Corpo e saúde VOLTAM ao curso e ao conteúdo, com as regras de POSICIONAMENTO.md.
- História da Gisele em metodo/HISTORIA_GISELE.md. Frase-mãe candidata: "Eu herdei a doença do meu pai. Não a história dele."
- Pendências: print das assinaturas INTEGRAL (central), lista dos títulos das ~100 aulas da Integra, ARQUITETURA_MODULOS_v3 e PROTOCOLO_SEGURANCA_CURSO.
