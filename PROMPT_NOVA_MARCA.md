# Prompt para abrir o laboratório de outra marca

Copie tudo entre as linhas, troque os campos [ENTRE COLCHETES] e cole no chat novo.

---

Sou a Gisele Hedler. Já fiz um laboratório de conteúdo para o meu perfil pessoal (@giselehedler) no repositório GiseleHedler/laboratorio-conteudo. Agora quero repetir o mesmo trabalho para outra marca minha: **[NATURAL PURE ou FSA]** (@[perfil]).

**Como quero que você trabalhe comigo:** seja direto, mostre pontos cegos, não concorde sempre comigo. Me desafie para eu crescer.

## Onde trabalhar
- Use o mesmo repositório, numa pasta só desta marca: `[natural-pure/ ou fsa/]`. Não misture com os arquivos do perfil pessoal.
- Reaproveite os scripts que já existem na raiz:
  - `analisar_viral.py`: ranqueia o export do Viral Finder;
  - `transcrever_reels.py`: transcreve reels pelo Apify;
  - `coletar_anuncios.py`: puxa a Biblioteca de Anúncios da Meta pelo Apify;
  - `coletar_apify.py`: puxa posts recentes de um perfil.
- Leia `GANCHOS.md`, `analises/giselehedler.md` e `REFERENCIAS_E_ADAPTACOES.md` para ver o formato de entrega que eu aprovei.
- Os scripts salvam em `dados/`, que fica fora do git. Tudo o que importar precisa ir para um arquivo versionado (análise, ganchos, referências), senão se perde quando o ambiente desligar.

## Regras que valem sempre
- **Custo:** antes de gastar qualquer crédito (Apify, geração de imagem ou vídeo), me diga quanto custa e espere eu confirmar. Depois, me diga quanto gastou de verdade.
- **Métrica:** cada post é comparado com a mediana do próprio perfil na mesma época (os 40 reels vizinhos). Nunca com número absoluto, nunca com outro perfil.
  - Reel com menos de 8 curtidas por mil visualizações é provável anúncio e fica de fora.
  - Viral fora do nicho (humor, trend) traz gente que não compra: aponte, mas não use como molde.
- **Ordem:** primeiro o perfil da própria marca, depois os concorrentes. Planejar pelos outros antes de olhar os próprios números foi um erro que cometemos no perfil pessoal.
- **Venda:** no perfil pessoal descobrimos que vender no feed derrubou o alcance. Lá, a venda vai para o direct e os stories, e o post termina com "comenta PALAVRA".
  - **Não aplique isso no automático aqui:** confira nos dados desta marca se a venda no feed realmente derruba o alcance. Uma marca de produto ou uma faculdade pode ter regra diferente.
- **Fatos:** nunca invente dado, estudo, depoimento ou história. Dado de pesquisa precisa de fonte conferida. Depoimento de cliente ou aluna só com consentimento.
- **Saúde:** nunca prometa cura nem tratamento, nunca diga que crença causa doença. [Natural Pure: siga as regras da Anvisa para o tipo de produto e não faça alegação terapêutica.] [FSA: siga as regras de publicidade dos conselhos profissionais dos alunos (CFN, CRN e outros) e não prometa resultado de carreira.]
- **Texto:** sem travessão. Português do Brasil.

## Passo a passo
1. **Contexto (me pergunte o que faltar):** o que a marca vende, preços, público (quem compra e quem só segue), oferta principal do momento, identidade visual (cores, fontes, kit da marca no Canva), links e diferenças em relação aos concorrentes.
2. **Meu perfil:** eu mando o CSV do Viral Finder da marca.
   - Rode o `analisar_viral.py`.
   - Mostre a curva de alcance por ano e trimestre.
   - Mostre quanto do feed é venda e como os posts de venda se saem.
   - Liste os campeões e os formatos que deram certo mais de uma vez.
   - Salve em `[pasta]/analises/[perfil].md`.
3. **Concorrentes:**
   - Me ajude a escolher de 3 a 5 (diretos e de referência de formato). Eu mando os CSVs.
   - Para cada um: ranking e a transcrição dos 15 a 20 melhores reels orgânicos.
   - Salve uma análise por concorrente.
4. **Anúncios:** puxe da Biblioteca de Anúncios da Meta os anúncios ativos de cada concorrente.
   - O que anunciam, que gancho usam, para onde mandam (site, WhatsApp, direct, aula grátis).
   - Há quanto tempo cada anúncio roda: anúncio antigo é anúncio que dá lucro.
5. **Lista de ganchos:** `[pasta]/GANCHOS.md`, organizada por molde. Cada molde traz o original (com link e multiplicador) e as versões para esta marca.
6. **Referências:** `[pasta]/REFERENCIAS_E_ADAPTACOES.md`, com o conteúdo original, o link e o que criamos a partir dele, para nada se perder.
7. **Semana 1:** só depois de tudo isso.
   - Os roteiros completos, a legenda e por que cada post existe (qual dado sustenta).
   - Onde entra a venda (direct e stories).
8. **Pauta quente:** proponha um radar semanal de notícias que combinem com a marca, com o gancho e o ângulo prontos.

Comece pelo passo 1: me diga o que precisa saber e quais arquivos eu devo mandar.

---

## O que levar já separado
- CSV do Viral Finder da marca e de 3 a 5 concorrentes.
- Nome das páginas dos concorrentes no Facebook, para a Biblioteca de Anúncios.
- Kit da marca: cores, fontes e logo.
- Ofertas e preços atuais.
