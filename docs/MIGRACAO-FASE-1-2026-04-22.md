# Migração Fase 1 — 2026-04-22

## Status
Concluída como **cópia segura**, sem remoção do workspace do BigDog e sem alterar scripts/crons vivos.

## O que foi copiado para o Cake Brain

### 1. Cérebro institucional
Origem:
- `cerebro/empresa/`
- `cerebro/areas/`

Destino:
- `cerebro/empresa/`
- `cerebro/areas/`

### 2. Materiais de marketing
Origem:
- `marketing/`

Destino:
- `marketing/`

### 3. Relatórios de marketing
Origem:
- `relatorios/marketing/`

Destino:
- `relatorios/marketing/`

### 4. Documentação de negócio/marketing
Arquivos copiados para `docs/`:
- `INSTALAR-META-PIXEL-WIX.md`
- `LINKEDIN-SETUP.md`
- `META-PIXEL-ID-FOUND.md`
- `RASTREAMENTO-CONVERSOES-SITE.md`
- `criar-paginas-wix.md`
- `integrations-map.md`

### 5. Assets de marca
Arquivos copiados para `brand/`:
- `logo-cake.pdf`
- `manual-marca-cake.pdf`
- `tipografia-cake.pdf`
- `manual-page-1.png` até `manual-page-8.png`

## O que deliberadamente NÃO foi migrado ainda

### Scripts vivos / automações
- `scripts/mogo-*`
- `scripts/organizar_drive_mogo.py`
- scripts de relatórios, tldv, rede, sprinthub, instagram, linkedin

### Motivo
Ainda dependem de:
- caminhos absolutos do workspace atual
- relatórios e saídas acopladas
- crons ativos no OpenClaw

## Próxima fase recomendada

### Fase 2
- inventariar os scripts empresariais
- mapear todos os crons que apontam para `/root/.openclaw/workspace/scripts/...`
- definir novo destino em `automacoes/scripts/`
- preparar ponte de compatibilidade antes de mover
