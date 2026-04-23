# Setup Pré-Evento — Imersão OpenClaw nos Negócios

> Checklist operacional completo para garantir que nada falhe no dia 28-29/03/2026.  
> Responsável: Cayo + Bruno. Marcar cada item conforme concluído.

---

## 1 Semana Antes (até 21/03/2026)

### Comercial / Produto
- [ ] **⚠️ URGENTE: Decidir produto e preço para o pitch do Dia 2** — ainda placeholder em `imersao/dia2/fechamento.md`
- [ ] Criar link de pagamento/checkout (Hotmart, Kiwify ou Lastlink)
- [ ] Testar fluxo de compra completo (do link até confirmação)
- [ ] Preparar email de boas-vindas pós-compra
- [ ] Preparar mensagem WhatsApp de follow-up pós-evento (para enviar nas 2h após o fim)

### Técnico / Infraestrutura
- [ ] Confirmar plataforma de streaming (Zoom Webinar / StreamYard) e plano suporta 200+ participantes
- [ ] Testar conexão internet backup (celular como hotspot funcional)
- [ ] Confirmar que repo `imersao-openclaw-negocios` está público e atualizado no GitHub
- [ ] Verificar que a URL pública do repo está correta para mostrar ao vivo
- [ ] Confirmar que `cerebro/dados/leads.csv` e `cerebro/dados/vendas.csv` têm dados fake realistas
- [ ] Verificar que `imersao/dados-demo/meta-ads-campanhas.csv` está presente e com dados válidos
- [ ] Verificar que `imersao/dados-demo/relatorio-meta-ads-exemplo.md` está presente (relatório pré-gerado para mostrar como output)
- [ ] Verificar que `imersao/dados-demo/vendas.csv` e `leads.csv` estão presentes
- [ ] Confirmar que skill `relatorio-ads` detecta modo demo (sem META_ADS_TOKEN → lê CSV local)

### Comunicação
- [ ] Enviar lembrete para participantes inscritos com: horário, link de acesso, o que vão ver
- [ ] Criar grupo/canal Telegram ou chat do streaming para interação ao vivo
- [ ] Preparar mensagem de Cayo para postar nas pausas

---

## 1 Dia Antes (27/03/2026)

### Ambiente e Agentes
- [ ] Clonar repo demo em máquina **limpa** (sem cache, sem token pré-carregado — para simular experiência do zero)
- [ ] Testar agente assistente principal: fazer 3 perguntas sobre a empresa demo, confirmar respostas contextualizadas
- [ ] Testar agente de marketing: pedir relatório de ads, confirmar que lê `cerebro/areas/marketing/`
- [ ] Testar bot de suporte (`cerebro/agentes/bot-suporte/`): responder FAQ, escalar dúvida nova, consolidar
- [ ] Verificar que `cerebro/areas/atendimento/bot/faq.md` tem 5+ perguntas reais
- [ ] Verificar que `cerebro/areas/atendimento/bot/duvidas.md` está vazio (para demo funcionar do zero)
- [ ] Verificar que crons configurados **NÃO** vão disparar durante a imersão (9h-12h)
  - Checar `openclaw.json` → desabilitar crons que disparam entre 8h30-12h30 no dia 28 e 29

### Skills
- [ ] Testar skill-creator com o comando: `"Crie uma skill que analisa leads e identifica os 3 mais quentes"`
- [ ] Confirmar que a skill gerada está no formato correto (SKILL.md com Input/Processo/Output)
- [ ] Testar `cerebro/areas/vendas/skills/relatorio-vendas/SKILL.md` executando ao vivo
- [ ] Testar `cerebro/areas/marketing/skills/analise-criativos/SKILL.md` com dados fake
- [ ] Testar `cerebro/areas/atendimento/skills/escalar-duvida/SKILL.md` com pergunta nova

### Dados e Planilhas
- [ ] Testar skill `relatorio-ads` ao vivo: pedir "gera relatório dos últimos 7 dias" e confirmar que lê o CSV e retorna relatório formatado
- [ ] Abrir `imersao/dados-demo/relatorio-meta-ads-exemplo.md` — confirmar que está legível e completo para mostrar durante o bloco
- [ ] Verificar `imersao/dados-demo/vendas.csv` — 52 linhas, dados de vendas OpenClaw fictícios
- [ ] Verificar `imersao/dados-demo/leads.csv` — 31 linhas, pipeline de leads com status variados

### Visual / Apresentação
- [ ] Abrir `imersao/apresentacao-imersao-v3.html` no browser e testar todas as seções
- [ ] Verificar que o HTML carrega sem erros (sem dependências externas quebradas)
- [ ] Testar rolagem, animações e legibilidade em projeção (zoom a 125%)

### Terminal e Streaming
- [ ] Configurar fonte do terminal: **mínimo 18px** (idealmente 20-22px para projeção)
- [ ] Testar `tree` instalado e funcionando: `tree cerebro/ -L 2`
- [ ] Configurar OBS/StreamYard com 3 cenas:
  - **Cena 1:** Terminal (80% tela)
  - **Cena 2:** Browser (GitHub / editor de arquivos)
  - **Cena 3:** Tela cheia do apresentador (para pitch)
- [ ] Testar transição entre cenas sem glitch
- [ ] Preparar segundo monitor: Telegram + chat do streaming + este run-of-show aberto

### Logística
- [ ] Preparar: água (2 garrafas), fone com fio (backup), cadeira ajustada
- [ ] Avisar moradores/família: não interromper 9h-12h nos dois dias
- [ ] Carregar notebook 100% na noite anterior
- [ ] Fechar apps desnecessários (notificações, Slack, email)

---

## 30 Minutos Antes (Dia 28: 8h30 | Dia 29: 8h30)

### Terminal
- [ ] Abrir terminal com repo clonado e no diretório raiz de `imersao-openclaw-negocios`
- [ ] Rodar `tree cerebro/ -L 2` para confirmar estrutura OK
- [ ] Abrir SOUL.md e AGENTS.md em abas do terminal/editor

### Browser
- [ ] Aba 1: `imersao/apresentacao-imersao-v3.html` (capa abertura)
- [ ] Aba 2: GitHub público do repo demo
- [ ] Aba 3: `imersao/dados-demo/relatorio-meta-ads-exemplo.md` aberto no editor
- [ ] Aba 4: `cerebro/agentes/assistente/SOUL.md` aberto no GitHub

### Agentes / Comunicação
- [ ] Abrir Telegram com agente assistente respondendo normalmente
- [ ] Abrir grupo/canal de demo do bot de suporte (Bloco 10)
- [ ] Abrir Claude Code como backup — apontar para o mesmo repo
- [ ] Confirmar que OpenClaw está rodando: enviar "oi" e aguardar resposta

### Streaming
- [ ] Entrar na sala de streaming 30min antes
- [ ] Testar áudio (fone + microfone backup)
- [ ] Testar vídeo (câmera)
- [ ] Confirmar que câmera está em posição e iluminação OK
- [ ] Cayo: entrar no chat como moderador — testar que consegue postar

### Último Checado
- [ ] Link de pagamento funcionando (abrir em aba anônima e testar fluxo)
- [ ] Este `RUN-OF-SHOW.md` aberto em segundo monitor ou impresso
- [ ] Horário sincronizado com Cayo via mensagem às 8h55

---

## Entre Dia 1 e Dia 2 (28/03 — tarde/noite)

- [ ] Revisar as 10 perguntas mais frequentes do chat do Dia 1
- [ ] Identificar se alguma demo travou — preparar versão mais simples como fallback
- [ ] Checar se demo do bot de suporte (Bloco 10) precisa de ajuste baseado no feedback
- [ ] Preparar **recap em 3 bullets** para abrir o Dia 2 (baseado no que realmente aconteceu)
- [ ] Confirmar que ambiente do bot de atendimento (`faq.md`, `duvidas.md`) está resetado para demo
- [ ] Ajustar crons: verificar novamente que nenhum vai disparar no Dia 2 (9h-12h)
- [ ] Descansar — o Dia 2 tem o pitch, o maior AHA moment e o fechamento. Energia é fundamental.

---

## Rollback / Plano B

| Cenário | Ação imediata |
|---------|--------------|
| GitHub fora do ar | Usar cópia local do repo no desktop; mostrar arquivos diretamente no terminal |
| Agente principal trava | Abrir Claude Code apontando para o mesmo `cerebro/` como substituto imediato |
| API Meta Ads falhar (Bloco 9) | Abrir relatório pré-gerado salvo em `cerebro/areas/marketing/sub-areas/trafego-pago/` |
| Bot de suporte não responde | Mostrar screenshot de conversa preparada; explicar o fluxo verbalmente |
| Skill não retorna relatório | Abrir `imersao/dados-demo/relatorio-meta-ads-exemplo.md` direto no terminal — "esse foi gerado às 8h" |
| Streaming cai (Zoom/StreamYard) | Backup: reiniciar streaming em 3min; Cayo avisa no chat com horário de retorno |
| Internet cai | Hotspot celular pré-configurado — testar antes. Cayo assume comunicação com participantes |
| Cayo precisa sair | Bruno continua sozinho — moderar chat e apresentar simultaneamente |

---

## Contatos de Operação

| Papel | Pessoa | Contato |
|-------|--------|---------|
| Apresentador | Bruno | — |
| Produtor / Moderador | Cayo | — |
| Suporte técnico backup | — | definir antes do evento |
| Plataforma streaming (suporte) | — | ter número/chat de suporte aberto |

---

*Versão: 1.0 | Criado: 2026-03-25*
