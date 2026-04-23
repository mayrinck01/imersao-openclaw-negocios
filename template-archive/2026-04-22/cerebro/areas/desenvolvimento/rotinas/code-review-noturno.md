# Rotina: Code Review Noturno

## O que faz
Revisa todos os PRs abertos no GitHub. Analisa qualidade do código, sugere melhorias, detecta bugs potenciais, verifica cobertura de testes e padrões do projeto. Dev chega de manhã com review pronto.

## Frequência
1x/dia — 00:00 BRT (03:00 UTC), seg a sex

## Entrega
- Comentários direto nos PRs do GitHub
- Resumo no tópico **💻 Desenvolvimento** do Telegram (topic_id: 7) às 07:00

## Exemplo de saída

```
🔍 Code Review — 27/03/2026

4 PRs revisados esta noite:

✅ #142 "Fix checkout flow" — Felipe
  → LGTM, 2 sugestões menores de naming

⚠️ #143 "Add new payment method" — Ana
  → 1 bug potencial: race condition no webhook handler
  → Cobertura de testes: 62% (meta: 80%)
  → 3 comentários no PR

⚠️ #145 "Refactor user service" — João
  → Breaking change na API — precisa de migration
  → Sugestão: split em 2 PRs menores

✅ #146 "Update dependencies" — Bot
  → Sem conflitos, testes passando
```

## Dados necessários
- GitHub API (token com acesso ao repo)
- Padrões do projeto em `areas/desenvolvimento/contexto/padroes.md`

## Configuração do Cron

```
Nome: code-review-noturno
Schedule: 0 3 * * 1-5  (0h BRT, seg-sex)
Prompt: "Revisa todos os PRs abertos no GitHub. Comenta sugestões, detecta bugs, verifica testes. Resumo às 7h no Dev."
Tópico: 💻 Desenvolvimento (topic_id: 7)
```

---

*Atualizado: março 2026*
