---
# ⚙️ Gerada automaticamente pelo Gerador de Skills (skill-creator)
# Data de geração: 2026-03-23
# Solicitado por: André Costa (COO)
# Revisão humana: recomendada antes de usar em produção

name: relatorio-rotinas
description: >
  Lista todas as rotinas automáticas (crons) ativas na empresa, mostrando
  área responsável, última execução, próxima execução e status. Identifica
  rotinas com falha ou sem execução recente.
---

# Relatório de Rotinas

## O que faz

Consolida o status de todas as rotinas automáticas (crons) configuradas para a Empresa Exemplo em um único painel. Mostra o estado de saúde de cada automação, alerta sobre falhas e ajuda a equipe a identificar quando uma rotina não está rodando corretamente.

---

## Quando usar

- **Toda segunda-feira às 8h** (rotina automática) — antes do weekly da equipe
- Quando alguém perguntar "todas as automações estão funcionando?"
- Após fazer mudanças no servidor ou nas configurações de cron
- Para auditoria mensal de processos automáticos

---

## Ferramentas necessárias

- Acesso aos logs de execução das rotinas (arquivo de log do sistema ou OpenClaw)
- Lista de rotinas configuradas em `rotinas/README.md`
- Data e hora atual (para calcular próxima execução)

---

## Passo a passo

1. **Ler o arquivo** `rotinas/README.md` para obter a lista de rotinas esperadas
2. **Consultar logs de execução** (arquivo de log ou API do sistema de crons)
3. **Para cada rotina, obter:**
   - Última execução (data e hora)
   - Status da última execução (sucesso / falha / timeout)
   - Próxima execução programada (calcular com base no cron schedule)
   - Área responsável
4. **Classificar o status:**
   - ✅ OK: Rodou na última janela esperada, sem erros
   - ⚠️ ATRASADA: Deveria ter rodado e não rodou (última > 1,5x o intervalo)
   - 🔴 FALHA: Última execução retornou erro
   - ⚪ INATIVA: Rotina configurada mas não ativada
5. **Identificar alertas críticos** (falhas ou rotinas atrasadas > 24h)
6. **Formatar e apresentar o relatório**

---

## Output esperado

```
🔄 RELATÓRIO DE ROTINAS AUTOMÁTICAS
Empresa Exemplo | Segunda, 23/03/2026 | 08:00h
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 STATUS GERAL
   Total de rotinas: 5
   ✅ OK:       3
   ⚠️  Atrasada: 1
   🔴 Falha:    1
   ⚪ Inativa:  0

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔴 ATENÇÃO IMEDIATA
──────────────────
❌ relatorio-vendas (VENDAS)
   Última execução: 16/03/2026 08:01 → FALHA (erro ao ler CSV)
   Próxima tentativa: 23/03/2026 08:00 (hoje)
   Ação: Verificar se o arquivo dados/vendas.csv está acessível

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️  MONITORAR
─────────────
⚠️ follow-up-leads (VENDAS)
   Última execução: 19/03/2026 09:02 → Sucesso
   Dias desde última execução: 4 (esperado: diário)
   Próxima execução: 23/03/2026 09:00 (hoje, em 1h)
   Ação: Aguardar próxima execução. Se não rodar, investigar.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ FUNCIONANDO NORMALMENTE
──────────────────────────
✅ backup-dados (OPERAÇÕES)
   Última execução: 22/03/2026 23:01 → Sucesso
   Próxima execução: 29/03/2026 23:00
   Frequência: Semanal (domingo, 23h)

✅ relatorio-rotinas (OPERAÇÕES)
   Última execução: 16/03/2026 08:00 → Sucesso
   Próxima execução: 23/03/2026 08:00 (agora)
   Frequência: Semanal (segunda, 8h)

✅ sync-repositorio (OPERAÇÕES)
   Última execução: 22/03/2026 21:00 → Sucesso
   Próxima execução: 23/03/2026 21:00
   Frequência: Diário (21h)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚡ 1 rotina com falha requer atenção imediata
📩 Alertas enviados para: André Costa (WhatsApp)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Gerado automaticamente | Empresa Exemplo
```

---

## Notas

- Este relatório **em si mesmo** é uma rotina (roda toda segunda às 8h)
- Se nenhum log de execução estiver disponível, reportar todas as rotinas como "status desconhecido"
- Enviar alerta imediato para o COO (André Costa) quando encontrar rotina com status 🔴
- Para adicionar uma nova rotina ao monitoramento, basta documentá-la em `rotinas/README.md`
- Rotinas marcadas como `inativa` não geram alertas — apenas são listadas para visibilidade

---

*Skill gerada automaticamente pelo Gerador de Skills | Revisar antes de usar em produção*
