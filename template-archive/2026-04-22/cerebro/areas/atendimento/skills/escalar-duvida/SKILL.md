# SKILL — Escalar Dúvida

## O Que Faz
Registra dúvidas sem resposta na FAQ no arquivo de pendências e notifica a equipe responsável para resolução.

---

## Input
- Dúvida original do cliente (texto completo)
- Nome e canal do cliente
- Classificação de prioridade (urgente / alta / normal)
- Contexto adicional (tentativa de resposta já feita? cliente irritado?)

## Processo

### 1. Criar ID da Dúvida
- Formato: `DÚV-{NNN}` (incrementar o último número em `duvidas.md`)
- Verificar o arquivo para não duplicar

### 2. Classificar a Dúvida
| Prioridade | Critério | Responsável |
|------------|---------|-------------|
| 🔴 Urgente | Sistema parado, cliente bloqueado | Diego Farias (técnico) — notificar imediatamente |
| 🟡 Alta | Bug ou contrato em risco | Carla Mendes (CSM) |
| 🟢 Normal | Dúvida técnica ou produto | Carla Mendes (CSM) |
| ⚪ Informação | Dúvida para virar FAQ | Fila semanal |

### 3. Registrar em duvidas.md
Adicionar nova entrada no arquivo `areas/atendimento/bot/duvidas.md`:

```markdown
### DÚV-{NNN}
- **Data:** {DATA-ATUAL}
- **Canal:** {CANAL}
- **Cliente:** {NOME} ({EMPRESA})
- **Pergunta original:** "{MENSAGEM DO CLIENTE}"
- **Status:** 🟡 Pendente
- **Obs:** {CONTEXTO ADICIONAL E RESPONSÁVEL DESIGNADO}
```

### 4. Notificar Equipe
Enviar mensagem no canal de atendimento:

```
🆕 Nova dúvida registrada — DÚV-{NNN}

📋 Cliente: {NOME} ({CANAL})
❓ Dúvida: {RESUMO EM 1 LINHA}
🎯 Prioridade: {URGENTE/ALTA/NORMAL}
👤 Responsável: {NOME}

Ver detalhes em duvidas.md
```

**Para urgências:** notificar diretamente Diego via WhatsApp além do canal.

### 5. Confirmar ao Cliente
Enviar mensagem de confirmação ao cliente:
```
Oi [Nome]! Registrei sua dúvida e nosso time especializado vai te responder
em até [SLA conforme prioridade]. Fique tranquilo(a), estamos em cima! 💪
```

## Output

**Confirmação de registro:**
```
✅ Dúvida registrada como DÚV-{NNN}
Responsável: {NOME}
SLA: {TEMPO}
Cliente notificado: ✅
```

---

## Referências
- Dúvidas: `areas/atendimento/bot/duvidas.md`
- SLA e responsáveis: `areas/atendimento/contexto/geral.md`
- Rotina de consolidação: `areas/atendimento/rotinas/consolidar-faq.md`
