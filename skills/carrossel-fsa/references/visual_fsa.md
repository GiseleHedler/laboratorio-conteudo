# Identidade visual do carrossel FSA

Inspirado no formato editorial de caixas de texto sólidas sobre fundo de cor ou foto
(tipografia pesada condensada, nome da marca no topo, dots de paginação embaixo).

## Cores (paleta oficial enviada pela Gisele, 12/10/2026)

| Nome          | Hex      | Uso                                              |
|---------------|----------|--------------------------------------------------|
| Roxo FSA      | #2B0739  | Fundo principal; cor do "FS" no logo             |
| Rosa FSA      | #C73E5C  | Fundo alternado; cor do "A" no logo              |
| Rosa destaque | #DC447C  | Detalhe e destaque (palavra, sublinhado, selo)   |
| Vinho fundo   | #14020D  | Fundo mais escuro, alternativa ao roxo           |
| Creme         | #ece4d8  | Fundo claro herdado do template antigo. NÃO está na paleta oficial: confirmar com a Gisele antes de usar |

No código do template, a variável --magenta guarda o Rosa FSA (o nome ficou por compatibilidade).

Contraste com texto branco (mínimo 4,5 para texto corrido):
- Roxo 17,6 e Vinho 20,1: qualquer tamanho.
- Rosa FSA 4,9: passa.
- Rosa destaque 4,1: só título grande ou detalhe, nunca texto corrido em branco.
- Rosa sobre roxo 3,6: só título grande.

## Fontes

- Título: **Archivo Black** (pesada, caixa alta).
- Corpo/comentário e marca: **Archivo** (regular 400, bold 700).
- Pendência: fonte oficial da FSA. A imagem da paleta usa uma sans geométrica parecida com Montserrat,
  mas isso não confirma a fonte da marca. O logo é desenhado (letras entrelaçadas), não é fonte.

## Logo

Arquivo em fsa/marca/logo-fsa.jpg no repositório laboratorio-conteudo: "FS" em roxo e "A" em rosa,
entrelaçados, sobre fundo branco. Para usar sobre fundo escuro, precisa de versão em PNG transparente
ou em negativo (pedir à Gisele).

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
