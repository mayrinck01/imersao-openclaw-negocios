# SKILL — Responder Cliente

## O Que Faz
Recebe uma mensagem de cliente, busca a resposta na base de conhecimento e formula uma resposta empática e completa. Se não encontrar resposta, escala para a equipe humana.

---

## Input
- Mensagem do cliente (texto completo)
- Canal de origem (WhatsApp / email)
- Nome do cliente (se disponível no contexto)
- Histórico recente da conversa (opcional)

## Processo

### 1. Classificar a Mensagem
Identificar o tipo de solicitação:
- **Dúvida informacional** → buscar na FAQ
- **Erro técnico** → verificar FAQ técnica; se não resolver, escalar
- **Financeiro/Contrato** → buscar FAQ financeira; se específico, escalar
- **Solicitação de ajuste** → escalar direto para Carla
- **Reclamação** → prioridade alta, resposta empática + escalar

### 2. Buscar na FAQ
- Ler `areas/atendimento/bot/faq.md`
- Encontrar a pergunta mais similar à dúvida do cliente
- Adaptar a resposta ao contexto específico do cliente (não copiar roboticamente)

### 3. Formular a Resposta

**Estrutura da resposta:**
```
[Saudação pelo nome, se disponível]
[Reconhecimento da dúvida/situação — 1 frase empática]
[Resposta direta e objetiva]
[Próximo passo concreto, se necessário]
[Convite para mais dúvidas]
```

**Tom:**
- Profissional mas acolhedor
- Direto — sem enrolação
- Empático — o cliente tem um problema real
- Solucional — sempre terminar com próximo passo claro

### 4. Decisão: Responder ou Escalar

| Situação | Ação |
|----------|------|
| Resposta encontrada na FAQ | Responder diretamente |
| Dúvida encontrada mas incompleta | Responder parcialmente + escalação |
| Dúvida não encontrada na FAQ | Usar skill `escalar-duvida` |
| Reclamação ou insatisfação | Resposta empática + escalar para Carla |
| Urgência técnica (sistema parado) | Escalar imediatamente + notificar Diego |

## Output

**Resposta para enviar ao cliente:**
```
Oi [Nome]! 😊

[resposta empática e completa]

Se tiver mais dúvidas, estou aqui!
— Equipe TechFlow
```

**Ou, em caso de escalação:**
```
Oi [Nome]!

Entendi sua situação. Essa é uma questão que nosso time especializado precisa
avaliar com mais atenção para te dar a melhor resposta.

Vou acionar a Carla, nossa analista de sucesso do cliente, e ela entra em contato
com você em até 2 horas (em dias úteis).

Pode deixar que resolvemos! 🙌
— Equipe TechFlow
```

---

## Referências
- FAQ: `areas/atendimento/bot/faq.md`
- Dúvidas pendentes: `areas/atendimento/bot/duvidas.md`
- Skill de escalação: `areas/atendimento/skills/escalar-duvida/SKILL.md`
- SLA e contatos: `areas/atendimento/contexto/geral.md`
