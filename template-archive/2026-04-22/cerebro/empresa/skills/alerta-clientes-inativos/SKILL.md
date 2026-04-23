---
name: alerta-clientes-inativos
description: "Verifica clientes que nao compram ha mais de N dias (padrao: 30) com base no vendas.csv e gera alerta para a equipe. Use quando alguem pedir para monitorar clientes inativos, identificar quem nao compra ha muito tempo, ou configurar alerta de retencao/recompra."
---

# Alerta de Clientes Inativos

## Quando usar

- Pedido manual: "me avise quando um cliente não comprar há 30 dias"
- Execução via cron periódico (semanal recomendado)

## Passos

### 1. Executar o script

```bash
python3 second-brain/cerebro/empresa/skills/alerta-clientes-inativos/scripts/checar_inativos.py \
  --csv <caminho_do_csv> \
  --dias <N>
```

Padrões:
- `--csv`: `second-brain/wizard-imersao/dados-demo/vendas.csv`
- `--dias`: `30`

> ⚠️ O CSV de demo não tem campo `cliente/email` — o script agrupa por produto como fallback. Com um CSV real (Hotmart, Kiwify), o campo `email` ou `nome` será usado automaticamente.

### 2. Interpretar o resultado

- **Sem inativos** → nenhuma ação necessária; confirmar para o solicitante
- **Com inativos** → gerar alerta com lista

### 3. Enviar alerta

Enviar no tópico 💰 Vendas (topic_id: 4) do grupo principal:

```
⚠️ Alerta de Clientes Inativos — DD/MM/YYYY

X cliente(s) sem compra há mais de N dias:

• [nome/email] — última compra: DD/MM (X dias atrás)
• ...

💡 Ação sugerida: acionar follow-up ou campanha de reativação.
```

Se nenhum inativo:
```
✅ Nenhum cliente inativo há mais de N dias.
```

### 4. (Opcional) Sugerir ação

Se houver inativos, sugerir próximo passo concreto:
- Lead de alto valor → follow-up direto pelo Felipe/Juliana
- Produto de entrada (Minicurso) → campanha de upsell automática
