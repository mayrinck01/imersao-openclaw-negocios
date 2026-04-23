# SKILL — Relatório de Ads

## O Que Faz
Analisa performance de criativos e campanhas do Meta Ads e gera relatório formatado com métricas, alertas e recomendações. Funciona em dois modos: **Demo** (lê CSV local) e **Produção** (conecta na Meta Ads API).

---

## Modo de Operação

### 🟡 MODO DEMO (padrão para imersão)
Lê os dados do arquivo CSV local. Não precisa de credenciais.

**Fonte de dados:** `imersao/dados-demo/meta-ads-campanhas.csv`

**Para ativar:** não configurar `META_ADS_TOKEN` no ambiente. O agente detecta automaticamente a ausência da variável e usa o CSV.

---

### 🟢 MODO PRODUÇÃO (para o participante configurar)
Conecta na Meta Ads API com as credenciais do participante.

**Para ativar:**
1. Criar app no Facebook Developers (developers.facebook.com)
2. Gerar token de acesso: Marketing API → Permissões: `ads_read`, `ads_management`
3. Configurar no OpenClaw:
   ```
   openclaw config set META_ADS_TOKEN="seu_token_aqui"
   openclaw config set META_ADS_ACCOUNT_ID="act_seu_id_aqui"
   ```
4. Testar: `openclaw run skill relatorio-ads --periodo ontem`

---

## Input
- Período desejado (padrão: últimas 24h)
- Nível de análise: criativo (padrão), conjunto ou campanha
- Opcional: ROAS mínimo alvo da empresa (padrão: 2.0x)

## Processo

### 1. Verificar modo de operação
```python
if META_ADS_TOKEN exists:
    modo = "producao"
    dados = fetch_meta_ads_api(token, account_id, periodo)
else:
    modo = "demo"
    dados = ler_csv("imersao/dados-demo/meta-ads-campanhas.csv")
```

### 2. Filtrar período solicitado
- Filtrar coluna `data` pelo período
- Agregar por `criativo_id` se múltiplos dias

### 3. Calcular métricas
- **ROAS** = receita ÷ gasto
- **CPA** = gasto ÷ compras
- **CTR** = cliques ÷ impressões × 100
- **CPC** = gasto ÷ cliques

### 4. Ranquear criativos
- Ordenar por ROAS (decrescente)
- Identificar: top performers (ROAS > 3x), monitorar (1.5–3x), avaliar pausar (< 1.5x)

### 5. Gerar recomendações
- Criativos com ROAS > 3x nos últimos 7 dias → recomendar escala
- Criativos novos (< R$150 gasto) → aguardar aprendizado
- Criativos com ROAS caindo > 20% semana a semana → alertar

### 6. Comparar com testes abertos
- Ler `trafego-pago/testes/abertos/` — checar se algum teste atingiu limiar de decisão
- Se sim: notificar que o teste pode ser consolidado

### 7. Gerar relatório
- Seguir template em `rotinas/meta-ads-report.md`

## Output

**Formato padrão: arquivo HTML** — sempre enviar o arquivo `wizard-imersao/dados-demo/meta-ads-report-exemplo.html` diretamente no canal (Telegram ou outro). Não usar canvas, não usar markdown inline, não perguntar ao usuário qual formato prefere.

**Antes de enviar, atualizar a data no HTML:**
```bash
# Gerar data por extenso em pt-BR via python3 (locale-independent)
DATA_HOJE=$(python3 -c "
import datetime
meses = ['janeiro','fevereiro','março','abril','maio','junho','julho','agosto','setembro','outubro','novembro','dezembro']
hoje = datetime.date.today()
print(f'{hoje.day} de {meses[hoje.month-1]} de {hoje.year}')
")
# Substituir a data hardcoded no arquivo → arquivo temporário
sed "s/[0-9]\{1,2\} de [a-záéíóúâêîôûãõç]* de [0-9]\{4\}/$DATA_HOJE/g" \
  /root/.openclaw/workspace-marketing/wizard-imersao/dados-demo/meta-ads-report-exemplo.html \
  > /tmp/meta-ads-report-hoje.html
# Enviar /tmp/meta-ads-report-hoje.html (não o original)
```
O arquivo original **nunca é modificado**. O `/tmp/` é descartado após o envio.

Após enviar o arquivo, incluir um resumo compacto em texto com os destaques principais:

```
📊 Report Meta Ads — OpenClaw
Período: {DATA} | Gerado às 08:00 BRT

💰 Resumo: Gasto R$X | Compras N | Receita R$X | ROAS Xx

🏆 Top criativos: [tabela ranqueada]

🚀 Recomendações: [escalar / monitorar / pausar]

🧪 Testes: [status dos testes em aberto]

💡 Insight do dia: [observação mais relevante]
```

---

## Referências
- Dados demo: `imersao/dados-demo/meta-ads-campanhas.csv`
- Exemplo de relatório gerado: `imersao/dados-demo/relatorio-meta-ads-exemplo.md`
- Ângulos documentados: `trafego-pago/angulos/`
- Learnings: `trafego-pago/learnings/resumo.md`
- Testes em aberto: `trafego-pago/testes/abertos/`
- Template: `trafego-pago/rotinas/meta-ads-report.md`
