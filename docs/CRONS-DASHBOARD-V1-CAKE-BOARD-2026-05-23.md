# Cron — Dashboard V1 para Cake Board

Criado em: 2026-05-23

## Objetivo

Enviar toda segunda-feira o Dashboard V1 de vendas para o grupo WhatsApp **Cake Board**, usando a instância Evolution **cake-interno**.

## Cron OpenClaw

| Campo | Valor |
|---|---|
| ID | `2d21485b-17b3-4d09-9e13-2af5c1017584` |
| Nome | `Dashboard V1 — vendas Cake Board (segunda 08:15 BRT)` |
| Agenda | `15 8 * * 1` |
| Timezone | `America/Sao_Paulo` |
| Sessão | `isolated` |
| Delivery | `none` |
| Failure alert | Telegram do Zão, após 1 falha |

## Comando executado

```bash
cd /root/workspaces/cake-brain && python3 automacoes/scripts/cake_dashboard_weekly_board.py
```

## Comportamento do script

1. Define o período como mês corrente até o dia anterior à execução.
2. Atualiza o Mogo `Vendas Analitico` com filtro **Data Pedido**.
3. Garante comparativo de 2025 para o mesmo mês.
4. Gera PDF executivo do Dashboard V1.
5. Checa se a Evolution `cake-interno` está conectada.
6. Envia texto + PDF para o grupo Cake Board.

## Destino

| Grupo | JID |
|---|---|
| Cake Board | `120363346768054790@g.us` |

## Regras

- O envio só ocorre se a instância `cake-interno` estiver `open`.
- Se a instância estiver `close` / `device_removed`, o script falha e o cron gera alerta.
- Não expor API key, cookies, base64 do PDF nem dados brutos do Mogo.
- Raw JSON do Mogo fica local e não deve subir ao GitHub.
