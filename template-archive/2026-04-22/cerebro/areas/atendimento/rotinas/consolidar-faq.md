# Rotina — Consolidar FAQ Semanal

## Identificação
- **Schedule:** Toda segunda-feira às 09:30 (horário de Brasília)
- **Responsável:** Agente bot-suporte (automático)
- **Duração estimada:** ~5 minutos

---

## Objetivo
Transformar dúvidas respondidas em entradas permanentes da FAQ, mantendo a base de conhecimento atualizada e o arquivo de dúvidas limpo.

---

## Passo a Passo

### 1. Ler Dúvidas Respondidas
- Abrir `areas/atendimento/bot/duvidas.md`
- Filtrar entradas com status `✅ Respondido`
- Para cada entrada respondida, verificar se é genérica o suficiente para virar FAQ (não deve ter dados pessoais do cliente)

### 2. Formatar como FAQ
Para cada dúvida respondida:
- Criar pergunta no formato "P: [pergunta genérica]"
- Criar resposta no formato "R: [resposta completa e útil]"
- Identificar a categoria correta em `faq.md` (Conta, Pagamento, Produto, Técnico, Contratos)
- Se não houver categoria adequada, criar nova seção

### 3. Adicionar ao faq.md
- Abrir `areas/atendimento/bot/faq.md`
- Inserir nova entrada na categoria correta
- Atualizar data de "Última atualização" no cabeçalho do arquivo
- Verificar se alguma resposta existente precisa ser atualizada (dúvida traz nova informação)

### 4. Limpar Dúvidas Respondidas
- Remover do `duvidas.md` APENAS as entradas com status `✅ Respondido` que foram incorporadas ao FAQ
- Manter todas as entradas `🟡 Pendente` intocadas
- Atualizar o número total de dúvidas ativas no cabeçalho se houver contador

### 5. Confirmar e Reportar
Enviar confirmação no tópico de atendimento:
```
✅ FAQ consolidada — {DATA}
Novas entradas adicionadas: {N}
Dúvidas pendentes restantes: {N}
```

---

## Regras
- Nunca incluir nome de cliente ou dado pessoal na FAQ
- Só promover a FAQ dúvidas que sejam relevantes para múltiplos clientes
- Dúvidas muito específicas de um cliente (ex: integração com sistema nichado) vão para a base técnica, não para FAQ
- Em caso de dúvida sobre categorização, deixar pendente e notificar Carla Mendes

---

## Referências
- FAQ: `areas/atendimento/bot/faq.md`
- Dúvidas: `areas/atendimento/bot/duvidas.md`
- Skill de escalação: `areas/atendimento/skills/escalar-duvida/SKILL.md`
