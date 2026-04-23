# Cake Brain — Bootstrap inicial

## Objetivo

Este repositório passa a ser o **cérebro institucional da Cake & Co**.

Ele não é a casa do agente BigDog.
Ele é a casa da **empresa**.

Função deste repo:
- guardar contexto institucional da Cake
- organizar áreas, pessoas, projetos e decisões
- concentrar relatórios e automações da empresa
- virar base consultável por qualquer agente no futuro

## Princípio de separação

### BigDog workspace
Responde:
- quem é João
- quem é BigDog
- como o agente opera
- memória pessoal/operacional do assistente
- runtime, segurança, cron, fallback, handoff

### Cake Brain
Responde:
- o que é a Cake
- como a empresa funciona
- quem são as pessoas-chave
- quais áreas existem
- quais projetos estão vivos
- quais decisões e lições de negócio já foram registradas
- onde moram relatórios, ativos e automações da empresa

## Estado deste bootstrap

Este repo foi criado a partir da base do curso:
- `https://github.com/mayrinck01/imersao-openclaw-negocios`

Nesta fase, ele está servindo como:
- esqueleto estrutural do cérebro da empresa
- destino de migração do conteúdo que hoje está misturado no workspace do BigDog

## Regra operacional

Não mover nada destrutivamente do workspace atual antes de:
1. mapear origem e destino
2. revisar dependências de scripts e crons
3. confirmar que a automação não vai quebrar

## Próximo passo

Usar o manifesto em `docs/MANIFESTO-MIGRACAO-BIGDOG-PARA-CAKE-BRAIN.md` como trilha de migração.
