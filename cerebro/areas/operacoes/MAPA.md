# MAPA — Área: Operações

## O que cobre
Tudo relacionado à operação diária da Cake & Co:
- Loja (atendimento, vendas, experiência)
- Fábrica (produção, qualidade)
- Sistema Mogo Gourmet (ERP)
- Scripts e automações

## Pessoas-chave
| Pessoa | Papel |
|--------|-------|
| **Alex Gonzaga** | Gerente — equipe loja, manutenção, compras (20 anos com família Mayrinck) |
| **Michel** | Líder de produção — 23 anos de Cake & Co |
| **Samuel** | Expedição |
| **Deivilene** | Expedição |

## Sistemas
- **Mogo Gourmet:** ERP principal — https://app3.mogogourmet.com.br/cakeeco
- **Endpoint API:** `Financeiro/BillsToReceiveJqGrid`, `/relatorios/BuscaDadosRelatorioDinamico`
- **Scripts:** `/root/workspaces/cake-brain/automacoes/scripts/mogo-*.py`

## Automações ativas (crons)

### Diários
| Horário | Script | O que faz |
|---------|--------|-----------|
| 00:01 BRT | mogo-pendentes.py | Pedidos pendentes por data/hora → email |
| 08:28 BRT | mogo-na-entrega.py | Alerta Na Entrega (se problema) → email |
| 09:00 BRT | mogo-pedidos-entregues.py | Pedidos entregues do dia anterior → email |

### Mensais (dia 1 de cada mês)
| Horário | Script | Relatório |
|---------|--------|-----------|
| 07:00 | mogo-faturamento-detalhado.py | Faturamento Detalhado |
| 07:00 | mogo-venda-nota-assinada.py | Venda em Nota Assinada |
| 07:15 | mogo-ticket-medio.py | Ticket Médio |
| 07:30 | mogo-vendas-analitico.py | Vendas Analítico |
| 08:00 | mogo-vendas-sintetico.py | Vendas Sintético |
| 08:15 | mogo-vendas-adicionais.py | Vendas Adicionais |
| 08:30 | mogo-lucratividade-produto.py | Lucratividade por Produto |
| 08:45 | mogo-descontos-concedidos.py | Descontos Concedidos |
| 09:00 | mogo-saldo-credito-carteira.py | Saldo Crédito Carteira |
| 09:15 | mogo-movimentacao-credito-cliente.py | Movimentação Crédito |
| 09:30 | mogo-taxa-servico.py | Taxa de Serviço |
| 09:45 | mogo-analise-cortesias.py | Cortesias |
| 10:00 | mogo-lancamentos-pedidos.py | Lançamentos de Pedidos |
| 10:30 | mogo-historico-pagamento.py | Histórico de Pagamento |
| 11:00 | mogo-entradas-xml-detalhado.py | Entradas XML |
| 11:15 | mogo-compra-produtos.py | Compra de Produtos |
| 11:30 | mogo-variacao-preco-compra.py | Variação Preço de Compra |
| 11:45 | mogo-analise-quantidades-produzidas.py | Quantidades Produzidas |
| 12:00 | mogo-analise-insumos-producao.py | Insumos na Produção |
| 12:15 | mogo-analise-cadastro-clientes.py | Cadastro de Clientes |
| 12:30 | mogo-itens-vendidos-agendamento.py | Itens por Agendamento |

## Estado atual da migração
- Os relatórios operacionais vivos do Mogo agora moram em `/root/workspaces/cake-brain/relatorios/Mogo/`
- O caminho legado `/root/.openclaw/workspace/relatorios/Mogo` foi mantido como symlink de compatibilidade
- Os crons ativos do Mogo foram atualizados para executar a partir de `/root/workspaces/cake-brain/automacoes/scripts/`
