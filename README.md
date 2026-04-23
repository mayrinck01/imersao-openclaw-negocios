# Cake Brain

Repositório do **cérebro institucional da Cake & Co**.

Este repositório existe para guardar o que é **empresa**:
- contexto institucional
- áreas
- pessoas
- decisões
- projetos
- relatórios
- ativos de marca
- automações operacionais da Cake

## O que este repo NÃO é

Este repo não é a casa do BigDog.

A casa do BigDog continua sendo o workspace principal do assistente, onde ficam:
- identidade do agente
- memória pessoal/operacional do João
- runtime do OpenClaw
- fallback, segurança, handoff, heartbeat e governança do agente

## Regra simples

- **Como a Cake funciona** → fica aqui
- **Como o BigDog funciona** → fica no workspace do BigDog

## Estrutura principal

```text
cake-brain/
├── MEMORY.md
├── cerebro/
├── automacoes/
├── relatorios/
├── brand/
├── marketing/
└── docs/
```

## Status atual

Este repo foi inicializado a partir da base do curso `imersao-openclaw-negocios` e já passou por uma primeira limpeza do template demo.

Documentos úteis:
- `docs/CAKE-BRAIN-BOOTSTRAP.md`
- `docs/MANIFESTO-MIGRACAO-BIGDOG-PARA-CAKE-BRAIN.md`
- `docs/MIGRACAO-FASE-1-2026-04-22.md`

## Próximo passo

Continuar a migração das automações da empresa para `automacoes/`, sem quebrar os crons ainda ativos no workspace do BigDog.
