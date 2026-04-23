# Migração Fase 2 — 2026-04-22

## Objetivo
Concluir a migração operacional da Cake para o `cake-brain`, saindo da fase estrutural para a fase de automações vivas.

## O que foi feito

### 1. Scripts empresariais copiados para o Cake Brain
Destino:
- `/root/workspaces/cake-brain/automacoes/scripts/`

Entraram principalmente:
- família `mogo-*.py`
- `mogo_login.py`
- `mogo_excel.py`
- `organizar_drive_mogo.py`
- scripts de Instagram, LinkedIn e relatórios de marketing
- scripts de suporte às automações (`filter_pt.py`, `audit_pt.py`)

### 2. Relatórios vivos movidos para o Cake Brain
Movidos de forma operacional:
- `relatorios/Mogo/`
- `relatorios/instagram/`

Novo destino físico:
- `/root/workspaces/cake-brain/relatorios/Mogo/`
- `/root/workspaces/cake-brain/relatorios/instagram/`

### 3. Compatibilidade preservada
Os caminhos antigos foram mantidos como symlink:
- `/root/.openclaw/workspace/relatorios/Mogo` → `cake-brain/relatorios/Mogo`
- `/root/.openclaw/workspace/relatorios/instagram` → `cake-brain/relatorios/instagram`
- scripts empresariais migrados no workspace antigo → `cake-brain/automacoes/scripts/`

### 4. Scripts adaptados para o novo destino
Nos scripts migrados, os caminhos absolutos foram atualizados para o `cake-brain` quando faziam sentido operacional.

### 5. Crons atualizados
Foram atualizados para o novo caminho:
- Mogo diário: Pendentes, Na Entrega, Pedidos Entregues
- Sync Drive Mogo: diário, mensal e verificação
- Toda a bateria mensal do Mogo

### 6. Crons legados desativados
Desativados por redundância/ambiguidade:
- `mogo-contas-assinada`
- `mogo-contas-assinada-send`

O job canônico mantido foi:
- `Venda em Nota Assinada — Mensal (dia 1, 07:00 BRT)`

## Resultado prático
A operação viva da Cake deixou de depender estruturalmente do diretório `scripts/` do workspace principal do BigDog para os relatórios Mogo e sync do Drive.

## O que permanece no BigDog por escolha arquitetural
- memória pessoal/operacional do João
- runtime do OpenClaw
- jobs pessoais do assistente
- alertas e rotinas não institucionais do BigDog
