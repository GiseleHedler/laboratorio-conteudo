# Identidade visual do carrossel FSA

Inspirado no formato editorial de caixas de texto sólidas sobre fundo de cor ou foto
(tipografia pesada condensada, nome da marca no topo, dots de paginação embaixo).

## Cores (extraídas do logo FSA)

| Nome   | Hex      | Uso                                            |
|--------|----------|------------------------------------------------|
| Roxo   | #2e1a35  | Fundo principal, texto sobre creme             |
| Magenta| #b13a6a  | Fundo alternado, caixa de destaque             |
| Creme  | #ece4d8  | Fundo claro, texto/caixa sobre roxo e magenta  |

Alternar o fundo dos slides entre as três cores ao longo do carrossel.

## Fontes

- Título: **Archivo Black** (pesada, caixa alta).
- Corpo/comentário e marca: **Archivo** (regular 400, bold 700).
- Se a FSA tiver fonte de marca própria, substituir aqui e no template.
  (Pendência: confirmar fonte oficial da FSA com a Gisele.)

## Regra de cor das caixas (legibilidade)

- Fundo ROXO ou MAGENTA: marca em creme, dots claros. Caixas de texto em creme
  (cx-creme) ou magenta (cx-magenta) com texto branco.
- Fundo CREME: marca em roxo, dots escuros. Caixas em roxo (cx-roxo, texto creme)
  ou magenta (cx-magenta, texto branco).

## Especificações fixas

- Tamanho: 1080 x 1350 px (formato retrato Instagram 4:5).
- Exportar em 2x (device_scale_factor=2) para nitidez.
- Marca no topo: "Faculdade de **Saúde Avançada®**" SEMPRE com o ® de marca registrada.
- Dots de paginação na base, marcando o slide atual.
- Número decorativo grande translúcido no canto inferior direito dos slides de conteúdo
  (opcional, dá profundidade).

## Fundos: chapado ou texturizado

- Chapado: classes bg-roxo / bg-magenta / bg-creme.
- Texturizado (recomendado, dá profundidade sem poluir): classes tex-grad-roxo,
  tex-grad-magenta, tex-grad-creme, tex-linhas-roxo, tex-pontos-magenta. São gradientes
  e padrões gerados por CSS na própria paleta FSA. Foi o que ficou melhor no teste.

## Tipos de slide disponíveis no template (assets/template_fsa.html)

- TIPO A: capa só texto.
- TIPO B: conteúdo (título + comentário + número), fundo roxo/magenta.
- TIPO C: conteúdo com fundo creme (inverte cores).
- TIPO D: foto de fundo ocupando o slide com texto por cima.
- TIPO E: colagem 2x2 de 4 fotos com título no meio.
- TIPO F: foto-destaque (objeto/produto centralizado embaixo) com texto em cima.

## Regra de imagem (importante)

A skill NÃO gera fotos. Fotos reais vêm da Gisele (produto, exame, foto de consultório,
foto pessoal). Foto com fundo limpo ou que combine com a paleta (roxo/magenta/creme)
harmoniza melhor. Foto de banco genérico enfraquece a autoridade da FSA: preferir
imagem real e própria sempre que o slide for institucional.
