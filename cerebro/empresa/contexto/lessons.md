# Lições Aprendidas

> 🔒 Estratégicas = permanentes | ⏳ Táticas = expiram em 30 dias

## 🔒 Estratégicas

- **Mogo é SPA pesada** — headless trava no spinner infinito; API interna funciona perfeitamente via HTTP
- **OAuth codes expiram em ~2 min** — processar imediatamente quando recebido
- **State do OAuth é por sessão** — nunca misturar callback de sessão diferente da que gerou o link
- **agentTurn crons gastam tokens** — para tarefas simples, usar bash puro via crontab
- **Michel (23 anos de Cake&Co)** é ativo estratégico raro — considerar nas decisões de produção
- **Frottas quebrou na pandemia** — Zão já viveu o downside real; não proteger emocionalmente sobre risco, trazer dados claros
- **Zão decide com 80% de confiança** — ajudar a chegar nos 80% rápido, não forçar análise infinita
- **Não usar foto pra passar URLs** — texto direto é mais rápido e preciso
- **Bullet points > parágrafos longos** sempre com o Zão
- **Ter opinião** — ele não quer 5 opções, quer a melhor com justificativa clara

## ⏳ Táticas

- **Compactação em 80%** é suficiente — reserveTokensFloor: 40000 (configurado 14/03/2026)
- **Token OpenAI expira ~22/03/2026** — renovar antes dessa data

---

*Revisão mensal: deletar táticas vencidas.*
