# Manifesto de migração — BigDog workspace → Cake Brain

## Objetivo

Migrar o que é **empresa** para o novo repositório `cake-brain/`, deixando o workspace atual cada vez mais limpo e focado só no BigDog como assistente pessoal.

## Regra-mãe

- **Não apagar nada do workspace atual nesta fase**
- **Não mover scripts com cron ativo sem revisar caminhos antes**
- **Migrar primeiro contexto e documentação, depois automações**

---

## Fase 1 — Migração segura imediata

### 1. Contexto institucional

#### Origem atual
- `cerebro/empresa/`
- `cerebro/areas/`
- parte institucional de `cerebro/seguranca/`

#### Destino no Cake Brain
- `cerebro/empresa/`
- `cerebro/areas/`
- `cerebro/seguranca/`

#### Observação
Essa é a migração mais importante. Aqui mora o cérebro da empresa de verdade.

---

### 2. Relatórios e ativos da empresa

#### Origem atual
- `relatorios/`
- `marketing/`
- PDFs e ativos de marca na raiz

#### Destino sugerido
- `relatorios/`
- `brand/`
- `areas/marketing/`

#### Itens típicos
- relatórios Mogo
- relatórios de marketing
- materiais de marca
- manuais, logos, tipografia, assets

---

### 3. Documentação de negócio

#### Origem atual
Exemplos do workspace atual:
- `docs/INSTALAR-META-PIXEL-WIX.md`
- `docs/META-PIXEL-ID-FOUND.md`
- `docs/RASTREAMENTO-CONVERSOES-SITE.md`
- `docs/criar-paginas-wix.md`
- `docs/integrations-map.md`

#### Destino sugerido
- `docs/`
- ou `areas/marketing/contexto/`
- ou `cerebro/empresa/contexto/` quando forem documentos mais institucionais

---

## Fase 2 — Migração de automações da empresa

### Origem atual
Principalmente:
- `scripts/mogo-*`
- `scripts/organizar_drive_mogo.py`
- `scripts/instagram-*`
- `scripts/linkedin-*`
- `scripts/relatorio-*`
- `scripts/export_tldv_*`
- `scripts/sprinthub-*`
- `scripts/rede_*`

### Destino sugerido
- `automacoes/scripts/`
- `automacoes/integrations/`
- `automacoes/cron/`

### Regra desta fase
Antes de mover qualquer script, revisar:
- cron jobs que apontam para `/root/.openclaw/workspace/scripts/...`
- caminhos absolutos para `/root/.openclaw/workspace/relatorios/...`
- imports locais e dependências de arquivos adjacentes

---

## Fase 3 — Limpeza final do workspace do BigDog

Quando o Cake Brain já estiver recebendo contexto e automações:

### Deve sair do workspace do BigDog
- relatórios empresariais
- materiais de marca
- documentação institucional da Cake
- scripts operacionais da empresa
- memória institucional duplicada

### Deve permanecer no workspace do BigDog
- `AGENTS.md`
- `SOUL.md`
- `IDENTITY.md`
- `USER.md`
- `BOOT.md`
- `HEARTBEAT.md`
- `MEMORY.md` do assistente
- `memory/` do assistente
- `vendor/`
- handoff, runtime, segurança, fallback, governança
- scripts de infraestrutura do agente

---

## Primeira leva recomendada

### Pode migrar primeiro, com baixo risco
- `cerebro/empresa/`
- `cerebro/areas/`
- `marketing/`
- `relatorios/operacoes/`
- `relatorios/marketing/`
- `docs` de marketing/integrações/negócio
- PDFs e assets de marca

### Não migrar ainda sem revisão
- scripts usados em cron
- relatórios vivos apontados por automações atuais
- qualquer arquivo com caminho absoluto no runtime

---

## Checklist operacional

- [ ] Confirmar estrutura final do Cake Brain
- [ ] Copiar contexto institucional primeiro
- [ ] Copiar docs de negócio
- [ ] Copiar ativos e relatórios históricos
- [ ] Inventariar scripts empresariais
- [ ] Mapear crons que usam caminhos absolutos
- [ ] Mover scripts empresariais por lote
- [ ] Atualizar crons para os novos caminhos
- [ ] Limpar o workspace do BigDog por último

---

## Próximo passo prático recomendado

Criar agora, dentro deste repo, os destinos abaixo para receber a primeira leva:

```text
brand/
relatorios/
automacoes/scripts/
automacoes/cron/
automacoes/integrations/
```

Depois disso, fazer o primeiro lote de cópia controlada.
