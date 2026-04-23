# MAPA — Área: Marketing

## O que cobre
- Instagram (@cakeco ou similar)
- Meta Ads (tráfego pago)
- Conteúdo e criativos
- LinkedIn (em estruturação)

## Pessoas-chave
| Pessoa | Papel |
|--------|-------|
| **Eduarda** | Marketing interno |

## Sistemas
- **Instagram API** — token configurado, coleta mensal de insights
- **Meta Ads API** — token (necessita renovação periódica)
- **Cron mensal:** `instagram-insights-coletor.sh` (1º do mês às 9h)

## Automações ativas
| Horário | Script | O que faz |
|---------|--------|-----------|
| 1º mês 09:00 | instagram-insights-coletor.sh | Coleta métricas Instagram |

## Pendências
- [ ] Relatório Instagram Mensal Detalhado — breakdown demográfico, top posts, novos seguidores
- [ ] Token Meta Ads permanente (atual expira semanalmente)
- [ ] Campanhas ativas — mapeamento e acompanhamento

## Contexto
Ver `cerebro/empresa/contexto/geral.md` para posicionamento da marca.
