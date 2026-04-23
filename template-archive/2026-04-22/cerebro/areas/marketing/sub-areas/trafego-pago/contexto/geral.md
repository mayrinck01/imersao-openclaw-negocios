# PROCESSO.md — Como o Agente Opera o Marketing

Este documento descreve o fluxo completo de como o agente opera o ciclo de marketing de criativos.

**Por que este arquivo é importante:** É o documento central que conecta todas as peças. Sem ele, você tem arquivos soltos sem saber como se relacionam. Com ele, você entende exatamente o que acontece em cada etapa, quem é responsável, e onde cada informação é registrada.

---

## O Ciclo

```
HIPÓTESE → CRIATIVO → TESTE → DADO → CONCLUSÃO → NOVA HIPÓTESE
    ↑                                                    │
    └────────────────────────────────────────────────────┘
```

Cada etapa tem responsabilidades divididas entre **humano** e **agente**.

---

## Etapas do Ciclo

### 1. Hipótese

| Tarefa | Responsável |
|--------|-------------|
| Formular a hipótese | Humano |
| Consultar learnings anteriores | Agente |
| Verificar se já foi testado | Agente |
| Sugerir variações baseadas em gaps | Agente |

**Arquivos consultados:** `learnings/`, `angulos/`, `formatos/`, `testes/consolidados/`

### 2. Criativo

| Tarefa | Responsável |
|--------|-------------|
| Verificar se formato existe | Agente |
| Gerar visual/roteiro | Agente |
| Documentar em descriptions/ | Agente |
| Aprovar criativo final | Humano |

**Se formato novo:** documentar em `formatos/` antes de criar.
**Se ângulo novo:** documentar em `angulos/` antes de criar.

### 3. Teste

| Tarefa | Responsável |
|--------|-------------|
| Aprovar upload | Humano |
| Subir na campanha de teste | Humano (por enquanto — pode automatizar via API) |
| Registrar no MAPA.md | Agente |
| Criar arquivo em testes/abertos/ | Agente |

### 4. Dado

| Tarefa | Responsável |
|--------|-------------|
| Buscar dados da API | Agente (cron automático) |
| Gerar relatório | Agente |
| Enviar no Telegram | Agente |
| Ler e interpretar | Humano |

**Crons ativos:**
| Cron | Horário | O que faz |
|------|---------|-----------|
| Relatório de ads | 8h, 12h, 20h BRT | Performance de todas as campanhas |
| Pipeline de criativos | 9h30 BRT | Recomendações: pausar/escalar |
| Relatório de funil | 8h BRT | Conversão por etapa do funil |

### 5. Conclusão

| Tarefa | Responsável |
|--------|-------------|
| Identificar testes prontos | Agente |
| Sugerir conclusão | Agente |
| Aprovar conclusão | Humano |
| Mover para consolidados/ | Agente |
| Atualizar learnings/ | Agente |

### 6. Nova Hipótese

| Tarefa | Responsável |
|--------|-------------|
| Identificar gaps nos ângulos/formatos | Agente |
| Sugerir próximas hipóteses | Agente |
| Escolher o que testar | Humano |

---

## Pontos de Intervenção Humana

Só **2 momentos** exigem ação humana:

1. **Decisões estratégicas** — qual hipótese testar, aprovar conclusão
2. **Aprovação de criativos** — revisar antes do upload

Todo o resto é automático.

---

## Regras de Decisão

| Situação | Ação | Quem |
|----------|------|------|
| ROAS < 1.0x por 5 dias | Pausar criativo | Agente (automático) |
| ROAS > 2.0x sustentado | Sugerir escalar +30% | Agente sugere, humano aprova |
| Frequency > 3.0 | Alertar fadiga | Agente alerta |
| Teste atingiu threshold | Sugerir fechar | Agente sugere, humano aprova |
| Sem conversões após R$ 150 | Pausar e documentar | Agente |

---

## Fluxo de Dados

```
        META ADS API
             │
             ▼
    ┌────────────────────┐
    │  Crons automáticos │
    │  (3x/dia + diário) │
    └────────────────────┘
             │
     ┌───────┼───────┐
     ▼       ▼       ▼
  reports/ testes/ pipeline/
     │       │       │
     └───────┼───────┘
             ▼
         TELEGRAM
    (relatórios + alertas)
             │
             ▼
          HUMANO
     (lê, decide, aprova)
```

---

*Última atualização: março 2026*
