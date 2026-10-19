# Black Vitalícia · Oferta personalizada para quem já é FSA

Listas (dados pessoais, NÃO vão para o repositório): `black-alunos-email.csv` e `black-alunos-whatsapp.csv`, 28.379 alunos, uma linha por e-mail.
Os links levam direto ao checkout do valor da pessoa, com o e-mail preenchido e a origem marcada (`sck=email_alunos` ou `sck=whatsapp_alunos`).

## Campos da lista (para usar como variáveis)
- `primeiro_nome`, `email`
- `segmento`: todas_4 (1.802) · ja_fez_3 (577) · ja_fez_2 (2.399) · ja_fez_1 (10.119) · aluno_outros_cursos (13.482)
- `abertura`: "Você já fez Nutrição Funcional e Suplementação com a gente." ou "Você já estudou com a gente."
- `destaque`: o pacote com o maior benefício para a pessoa (Hipócrates, Galeno ou Olimpo)
- `destaque_parcela`, `destaque_vista`, `destaque_separado`, `destaque_preco_publico`, `destaque_economia_vs_separado`, `destaque_link`
- `hipocrates_parcela/vista/link`, `galeno_...`, `olimpo_...`: o valor da pessoa nos três pacotes
- só no WhatsApp: `botao_sufixo` (final do link do botão)

## E-mail

**Assunto (A):** {{primeiro_nome}}, o seu valor na Black Vitalícia
**Assunto (B):** Só para quem já é FSA: o seu {{destaque}} por {{destaque_vista}}
**Pré-cabeçalho:** Separado, {{destaque_separado}}. Para você, {{destaque_vista}}. Com acesso vitalício.

Olá, {{primeiro_nome}}.

{{abertura}} Por isso, nesta Black, o seu valor não é o da página. É ainda mais especial.

Pela primeira vez, as formações da FSA têm acesso vitalício. Elas ficam com você para sempre, com todas as atualizações. Quando aquele caso difícil chegar, daqui a um mês ou daqui a cinco anos, a aula vai estar lá.

**O seu valor no Pacote {{destaque}}**
Comprando as formações separadas: ~~{{destaque_separado}}~~
Na Black, para quem ainda não é FSA: ~~{{destaque_preco_publico}}~~
**Para você: {{destaque_parcela}}, ou {{destaque_vista}} à vista com desconto**
Você economiza {{destaque_economia_vs_separado}}.

[ Quero o {{destaque}} com o meu valor ] → {{destaque_link}}

Prefere outro pacote? O seu valor em cada um:
- Hipócrates (a base): {{hipocrates_parcela}} ou {{hipocrates_vista}} → {{hipocrates_link}}
- Galeno (além da referência): {{galeno_parcela}} ou {{galeno_vista}} → {{galeno_link}}
- Olimpo (tudo, mais a Formação Avançada): {{olimpo_parcela}} ou {{olimpo_vista}} → {{olimpo_link}}

Esse valor é exclusivo para quem já estudou na FSA e vale até 31/10, às 23h59, quando o vitalício fecha.
15 dias de garantia incondicional.
Ficou com dúvida? Fala com a equipe no WhatsApp: (51) 98983-1882.

Gisele e Gabriel

## WhatsApp (modelo para a API, categoria Marketing)
Precisa ser aprovado pela Meta antes do envio (de minutos a 24 h).

Oi, {{1}}! Aqui é a Gisele, da FSA.

{{2}} Por isso, na Black Vitalícia, o seu valor é ainda mais especial.

Pacote {{3}}, com acesso vitalício:
Comprando separado: {{4}}
Para você: {{5}}, ou {{6}} à vista.

Esse valor é só para quem já é FSA e vale até 31/10, às 23h59.

Botão (URL dinâmica): "Ver o meu valor" → https://pay.hotmart.com/{{1}}

Variáveis: {{1}} primeiro_nome · {{2}} abertura · {{3}} destaque · {{4}} destaque_separado · {{5}} destaque_parcela · {{6}} destaque_vista · botão: botao_sufixo

## Ordem de envio sugerida
1. E-mail para todos: terça 20/10, de manhã (quem viu a live já tem o contexto; quem não viu recebe o próprio valor).
2. WhatsApp: quinta 22/10, só para quem NÃO comprou. Começar pelos segmentos de maior desconto (todas_4, ja_fez_3, ja_fez_2: 4.778 pessoas). Os outros, só se o custo valer.
3. Antes de cada envio, tirar da lista quem já comprou (exportar compradores da Black na Hotmart e remover pelo e-mail).
