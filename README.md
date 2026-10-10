# Laboratório de Conteúdo

Análise de conteúdo e posicionamento no Instagram usando o Jev (TypeSafe).

## Como funciona

1. **Coletar** — posts dos perfis de referência e do perfil próprio (API oficial da Meta).
2. **Achar os campeões** — engajamento de cada post comparado à média do próprio perfil.
3. **Rotular em massa (Jev)** — tema, formato, gancho, promessa, chamada para ação, ângulo de posicionamento.
4. **Achar padrões** — o que os campeões têm em comum.
5. **Análise profunda e modelagem (Claude)** — destrinchar os melhores e adaptar ao posicionamento próprio.

## Chaves (.env, nunca versionado)

- `TYPESAFE_API_KEY` — chave do Jev
- token da Meta (a definir)

## Teste rápido do Jev

    python3 testar_jev.py
