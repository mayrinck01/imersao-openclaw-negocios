# Rotina: Onboarding Check

## O que faz
Verifica etapas pendentes de onboarding de novos funcionários: documentos enviados, acessos criados, equipamento entregue, treinamentos concluídos. Cobra gestor responsável se etapa atrasada.

## Frequência
1x/dia — 03:00 BRT (06:00 UTC), seg a sex

## Entrega
- Alerta no tópico **👥 Pessoas** do Telegram (topic_id: 8) às 08:00
- Cobrança direta ao gestor se item > 2 dias atrasado

## Exemplo de saída

```
👋 Onboarding Check — 27/03/2026

2 pessoas em onboarding:

📌 Marina Silva (Dev — início: 24/03)
  ✅ Contrato assinado
  ✅ Notebook entregue
  ⚠️ Acesso ao GitHub — pendente há 3 dias → Cobrar João (TI)
  ❌ Treinamento segurança — não iniciado
  → Gestor: Felipe — alertado

📌 Pedro Souza (Marketing — início: 27/03)
  ✅ Contrato assinado
  ✅ Acesso ao Slack
  🔄 Notebook — saindo pra entrega hoje
  ❌ Tour pelo produto — agendar com Ana
  → Gestor: Bruno — alertado
```

## Dados necessários
- Checklist de onboarding em `areas/pessoas/contexto/checklist-onboarding.md`
- Lista de novos em `areas/pessoas/contexto/novos-funcionarios.md`

## Configuração do Cron

```
Nome: onboarding-check
Schedule: 0 6 * * 1-5  (3h BRT, seg-sex)
Prompt: "Verifica etapas pendentes de onboarding e cobra gestores. Entrega às 8h em Pessoas."
Tópico: 👥 Pessoas (topic_id: 8)
```

---

*Atualizado: março 2026*
