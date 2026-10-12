---
name: carrossel-fsa
description: Gera carrosséis de Instagram (1080x1350) com a identidade visual da FSA (Faculdade de Saúde Avançada) a partir de textos e fotos que a usuária fornece. Use SEMPRE que a Gisele pedir um carrossel, post ou slides para a FSA, ou disser "carrossel FSA", "monta um carrossel", "faz os slides", mesmo sem detalhar o layout. A skill já contém o layout, as cores, a fonte e as regras de voz da FSA; a usuária só fornece tema, textos e imagens. Também use quando ela enviar fotos dizendo em qual slide cada uma vai, ou quando pedir para adaptar um carrossel existente para a FSA.
---

# Carrossel FSA

Gera carrosséis de Instagram com a identidade visual da Faculdade de Saúde Avançada.
A usuária (Gisele) fornece tema, textos e fotos. A skill cuida do layout, cores,
tipografia, voz e exportação em PNG prontos para postar.

## O que esta skill faz e o que NÃO faz

Faz: monta o layout, aplica as cores e fonte da FSA, escreve/ajusta o texto na voz
da FSA, posiciona as fotos REAIS fornecidas pela Gisele, exporta cada slide como
PNG 1080x1350.

Não faz: gerar fotos por IA. Esse caminho foi testado e descartado (instável, lento,
exige download/upload manual). O modelo que funciona é: fundo gráfico (cor + textura
na paleta FSA) para slides conceituais, e foto REAL que a Gisele sobe para slides com
objeto concreto (produto, exame, foto pessoal, consultório). Slide conceitual em fundo
gráfico é resultado esperado e tem mais autoridade do que foto genérica.

## Regra de marca (obrigatória)

A marca SEMPRE aparece como "Faculdade de Saúde Avançada®", com o símbolo ® de marca
registrada. Nunca escrever o nome sem o ®. No template isso já está aplicado via
`<sup>&reg;</sup>` em todos os slides.

## Fluxo de trabalho

### 1. Entender o pedido
Coletar: tema do carrossel, número de slides (default 6), e se há fotos. Se a Gisele
não passar os textos, escrever os textos seguindo `references/voz_fsa.md` e mostrar
para aprovação ANTES de montar o visual. O texto se aprova primeiro, depois vira imagem.

### 2. Ler as referências
- `references/voz_fsa.md`: regras de escrita e estrutura editorial (LER SEMPRE antes
  de escrever qualquer texto).
- `references/visual_fsa.md`: cores, fontes, tipos de slide, regra de cor das caixas.

### 3. Montar o HTML
Copiar `assets/template_fsa.html` para o diretório de trabalho. Para cada slide,
escolher o TIPO adequado (A a F, descritos no template e em visual_fsa.md) e preencher.
Regras inegociáveis ao preencher:
- Alternar o fundo entre roxo (#2e1a35), magenta (#b13a6a) e creme (#ece4d8).
- Fundo creme inverte as cores (marca escura, dots escuros, caixas roxas).
- Título em caixa alta, 3 a 6 palavras por linha. Comentário em parágrafo único.
- Respeitar TODAS as regras de voz_fsa.md (sem antítese, sem travessão, etc.).

### 4. Embutir as fotos (se houver)
Usar `scripts/embed_images.py` para trocar os placeholders (FOTO_1.jpeg, etc.) pelas
imagens reais em base64:
```
python scripts/embed_images.py carrossel.html FOTO_1.jpeg=/caminho/a.jpg FOTO_2.jpeg=/caminho/b.jpg
```
Antes de usar uma foto, checar a regra de imagem em visual_fsa.md: foto deve combinar
com o tema e com a paleta. Se a foto destoar do tema (ex: foto lifestyle num post
institucional sobre doença), AVISAR a Gisele antes de montar, não montar calado.

### 5. Renderizar
```
python scripts/render_carrossel.py carrossel.html ./out
```
Gera slide_1.png, slide_2.png, ... em ./out, cada um 1080x1350 em 2x.

### 6. Conferir e entregar
Abrir cada PNG gerado e conferir: texto não estourou a caixa, legibilidade boa nos
três fundos, fotos bem enquadradas. Só então entregar à Gisele (via present_files se
disponível). Se algo estourou, ajustar o tamanho da fonte no slide específico e
re-renderizar.

## Dependências
```
pip install playwright --break-system-packages
playwright install chromium
```

## Notas de calibração
- Esta skill é calibrada para a VOZ DA FSA. Para Natural Pure ("bioprecioso", nunca
  "suplemento") ou marca pessoal da Gisele (confrontadora/soberania), o layout serve
  mas o tom precisa ser ajustado: ver voz_fsa.md, seção "Tom por marca".
- Fonte oficial da FSA é uma pendência: o template usa Archivo. Se a Gisele confirmar
  a fonte de marca, trocar em assets/template_fsa.html e em visual_fsa.md.
- O ponto forte do formato é o slide que mais quebra o senso comum. Posicioná-lo por
  último antes do fecho, é o que segura a pessoa até o fim.
