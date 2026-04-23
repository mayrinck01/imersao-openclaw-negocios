# Rotina — Sync Mapa de Criativos (Google Sheets → MAPA.md)

## Identificação
- **Schedule:** Todo dia às 06:00 (horário de Brasília)
- **Responsável:** Agente de marketing (automático)
- **Destino:** Atualização silenciosa no Cérebro (commit no GitHub)
- **Duração estimada:** ~1 minuto

---

## O Que Faz

### 1. Lê a planilha fonte (Google Sheets)
- Acessa a planilha "Mapa de Criativos" via API do Google Sheets
- Puxa todas as linhas da aba principal: Campanha, Nome Interno, Nome Meta Ads, Ângulo, Formato, Arquivo, Status

### 2. Gera o `mapa-criativos.md` atualizado
- Converte a tabela da planilha em formato Markdown
- Mantém a estrutura padrão: cabeçalho, tabela, seção "Como usar" e data de atualização
- Sobrescreve `cerebro/areas/marketing/sub-areas/trafego-pago/contexto/mapa-criativos.md`

### 3. Commit automático
- Commita a alteração no GitHub com mensagem padronizada:
  `sync: mapa-criativos atualizado — {N} criativos — {DATA}`

---

## Regras

- **Fonte da verdade:** sempre a planilha Google Sheets. O `.md` é derivado.
- **Nunca editar o `.md` manualmente** — será sobrescrito no próximo sync.
- **Se a planilha estiver vazia ou inacessível:** não sobrescrever. Logar erro e alertar no tópico #marketing.
- **Novos criativos detectados:** incluir nota no commit indicando quantos foram adicionados.

---

## Por que 06:00?

O sync roda antes do relatório de Meta Ads (08:00). Assim, quando o agente gera o report diário, o MAPA já está atualizado com os criativos mais recentes — incluindo os que foram subidos no dia anterior.

Sequência:
1. 06:00 — sync mapa de criativos (esta rotina)
2. 08:00 — relatório de Meta Ads (usa o mapa atualizado pra cruzar dados)

---

## Referências
- Planilha fonte: Google Sheets (ID configurado no `.env` do agente)
- Arquivo destino: `cerebro/areas/marketing/sub-areas/trafego-pago/contexto/mapa-criativos.md`
- Lookup: coluna **Nome Meta Ads** é a chave de cruzamento com a API do Meta
