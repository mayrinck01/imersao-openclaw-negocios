# Run of Show — Imersão OpenClaw nos Negócios

> Documento operacional para o produtor (Cayo). Imprimir 1 página por dia.

---

## DIA 1 — 28/03/2026

| Hora  | Duração | Bloco              | O que acontece                                                          | Visual                          | Ação do Cayo                              |
|-------|---------|--------------------|-------------------------------------------------------------------------|---------------------------------|-------------------------------------------|
| 9:00  | 15min   | Abertura           | Boas-vindas, apresentar Bruno+Cayo, explicar formato sem slides, ativar chat com pergunta "Qual área automatizar?" | `apresentacao-imersao-v3.html` → capa | Confirmar transmissão OK, contagem de participantes, moderar chat |
| 9:15  | 2min    | _Transição_        | Abrir terminal e browser para demo                                      | Terminal + GitHub               | Capturar respostas do chat para usar no bloco |
| 9:17  | 20min   | Bloco 1            | O problema da memória, 3 níveis de agente, arquitetura repo-como-cérebro, COMO-CONECTAR.md, demo `git pull` | Browser: GitHub + `cerebro/agentes/COMO-CONECTAR.md` | Capturar perguntas; anotar as 3 melhores  |
| 9:37  | 2min    | _Transição_        | Abrir `tree` no terminal, preparar 2-3 arquivos para abrir             | Terminal                        | —                                         |
| 9:39  | 25min   | Bloco 2            | Tour completo pelo `cerebro/`, abrir SOUL.md + AGENTS.md, demo dupla OpenClaw+Claude Code com mesma pergunta, interação com chat | Terminal: `tree cerebro/` + arquivos abertos | Passar perguntas do chat para Bruno; anotar top 3 para Bloco 4 |
| 10:04 | 1min    | _Transição_        | Abrir planilha Google Sheets demo e skill template                      | Browser: planilha demo          | —                                         |
| 10:05 | 30min   | Bloco 3 🔥         | Anatomia de skill, conectar planilha ao vivo, gerar relatório, **1º AHA MOMENT** — relatório no Telegram | Terminal + Telegram             | Moderar chat; capturar reações ao AHA moment; anotar pergunta mais comum |
| 10:35 | 5min    | _Transição/Buffer_ | Bruno responde 1 pergunta rápida do chat enquanto prepara ambiente Bloco 4 | —                               | Postar mensagem de pausa no chat: "☕ Pausa de 10 min. Volta 10h40 com 2º AHA." |
| 10:40 | 10min   | **Pausa**          | Descanso — Bruno. Cayo coleta top 3 perguntas do chat                  | —                               | Coletar top 3 perguntas; testar skill-creator pronto; postar no chat |
| 10:50 | 1min    | _Retorno_          | Bruno de volta ao ar, confirmar áudio/vídeo                             | Terminal                        | Confirmar qualidade stream                |
| 10:51 | 35min   | Bloco 4 🔥         | Responder top 3 perguntas (5min), apresentar skill-creator, criar skill com linguagem natural, criar skill baseada em sugestão do chat — **2º AHA MOMENT** | Terminal ao vivo                | Escolher sugestão mais interessante do chat para Bruno criar ao vivo |
| 11:26 | 2min    | _Transição_        | Abrir `openclaw.json` e pasta de rotinas                                | Terminal: openclaw.json         | —                                         |
| 11:28 | 20min   | Bloco 5            | Conceito de cron, criar rotina ao vivo, cron expressions básicas, heartbeat demo | Terminal: openclaw.json + Telegram | Monitorar chat; capturar dúvidas sobre cron |
| 11:48 | 2min    | _Transição_        | Abrir AGENTS.md e seção security do openclaw.json                      | Terminal: AGENTS.md             | —                                         |
| 11:50 | 15min   | Bloco 6            | Dados locais (não nuvem), modo ask ao vivo, AGENTS.md com restrições, controle granular | Terminal: openclaw.json + AGENTS.md | Capturar perguntas finais do dia           |
| 12:05 | 5min    | Fechamento Dia 1   | Recap 6 blocos, tarefa para amanhã (pensar em skill), teaser Dia 2     | —                               | Postar tarefa no chat; informar horário Dia 2 (9h) |
| 12:10 | —       | **FIM DIA 1**      | —                                                                       | —                               | Salvar top perguntas do chat; confirmar ambiente para Dia 2 |

**Total Dia 1:** ~3h10min | Blocos: 6 | AHA moments: 2

---

## DIA 2 — 29/03/2026

| Hora  | Duração | Bloco              | O que acontece                                                          | Visual                          | Ação do Cayo                              |
|-------|---------|--------------------|-------------------------------------------------------------------------|---------------------------------|-------------------------------------------|
| 9:00  | 15min   | Abertura Dia 2     | Recap Dia 1 em 5 bullets, coletar tarefas que participantes pensaram, roteiro do Dia 2, reativar engajamento | Terminal: recap rápido          | Confirmar ambiente OK; monitorar chat; selecionar 2-3 respostas para Bruno ler |
| 9:15  | 2min    | _Transição_        | Criar pasta `cerebro/agentes/suporte/` no terminal                     | Terminal                        | —                                         |
| 9:17  | 30min   | Bloco 7            | Conceito 1→sistema de agentes, criar SOUL.md do agente de suporte ao vivo, demo lado a lado dois agentes, quando usar multi-agente | Terminal + Telegram (2 grupos)  | Monitorar ambos os chats; capturar reações |
| 9:47  | 2min    | _Transição_        | Abrir AGENTS.md com estrutura de escopo                                 | Terminal: AGENTS.md             | —                                         |
| 9:49  | 20min   | Bloco 8            | Duas camadas de controle (escopo + whitelist), cenário A (grupos) vs B (tópicos), demo acesso negado + acesso autorizado | Terminal + Telegram             | Selecionar 1-2 perguntas do chat sobre permissões |
| 10:09 | 2min    | _Transição_        | Abrir estrutura de pastas do marketing no terminal                      | Terminal                        | —                                         |
| 10:11 | 30min   | Bloco 9            | Ciclo hipótese→criativo→teste→dado, estrutura `cerebro/areas/marketing/`, 3 skills (relatorio-ads, analise-criativos, criacao-criativos), daily report ao vivo + resposta do agente, 3 crons | Terminal + Browser: planilha/report | Capturar perguntas sobre marketing; testar que bot de suporte está pronto para Bloco 10 |
| 10:41 | 1min    | _Transição/Buffer_ | Bruno responde 1 pergunta rápida                                        | —                               | Postar no chat: "☕ Última pausa. Volta 10h50 com o maior AHA MOMENT da imersão." |
| 10:42 | 8min    | **Pausa**          | Descanso. Cayo testa bot de suporte demo ao vivo                       | —                               | Testar: faq.md + duvidas.md + skill consolidar-faq; confirmar Telegram do bot OK |
| 10:50 | 1min    | _Retorno_          | Bruno de volta, confirmar áudio                                         | —                               | Confirmar stream OK                       |
| 10:51 | 35min   | Bloco 10 🔥        | Loop de aprendizado (diagrama), estrutura 3 arquivos, demo bot responde FAQ, demo bot escala dúvida nova, consolidar FAQ + bot aprende — **3º AHA MOMENT** | Terminal + Telegram: bot demo   | Monitorar reações do chat; deixar "explodir" nos últimos 7min |
| 11:26 | 2min    | _Transição_        | Abrir arquivo markdown com tabela de roadmap                            | Terminal                        | —                                         |
| 11:28 | 22min   | Bloco 11           | Armadilha de fazer tudo de uma vez, roadmap 4 semanas, critérios de sucesso por semana, onde buscar ajuda | Terminal: tabela roadmap        | Preparar para pitch: confirmar link de pagamento ativo |
| 11:50 | 10min   | Fechamento + Pitch | Recap 2 dias, virada de mentalidade, **PITCH DA OFERTA**, abertura de carrinho, link no chat | —                               | Postar link de compra no chat imediatamente no pitch; monitorar vendas em tempo real |
| 12:00 | —       | **FIM DA IMERSÃO** | —                                                                       | —                               | Manter link ativo; enviar email/WhatsApp de follow-up pós-evento |

**Total Dia 2:** ~3h00min | Blocos: 5 | AHA moments: 1 (o maior)

---

## Legenda

| Símbolo | Significado |
|---------|-------------|
| 🔥 | AHA Moment — pausa intencional no chat |
| _Itálico_ | Transição — Bruno prepara ambiente, não fala |
| **Negrito** | Marco crítico de operação |

## Contatos de Emergência (Plano B)

- **Agent travou:** Abrir Claude Code como backup → mesmo repo
- **Streaming caiu:** Backup celular hotspot + reiniciar StreamYard
- **API falhou:** Usar relatório pré-gerado salvo em `cerebro/dados/`
- **GitHub fora:** Cópia local do repo no desktop

---

*Versão: 1.0 | Criado: 2026-03-25*
