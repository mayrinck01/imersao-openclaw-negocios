---
name: tria-checklist-notion
description: "Use quando o usuário pedir para processar relatórios Tria, Checklist Fácil, visitas técnicas, PDFs/fotos de visita, inconformidades ou KPIs de segurança alimentar no Notion da Cake & Co."
metadata:
  version: "1.0"
  created: "2026-05-28"
  maintainer: "João Mayrinck — CEO Cake & Co"
  related_scripts:
    - /root/workspaces/cake-brain/automacoes/scripts/tria_notion_sync.py
---

# Tria / Checklist Fácil → Notion

Use esta skill para sincronizar relatórios de visita técnica Tria/Checklist Fácil com o Notion da Cake & Co.

## Princípio

Dados estruturados são fonte primária. PDFs e fotos são evidência. Não reconstruir relatório inferindo tudo pelo PDF quando houver export estruturado.

## Fontes canônicas

- Script: `/root/workspaces/cake-brain/automacoes/scripts/tria_notion_sync.py`
- Testes: `/root/workspaces/cake-brain/automacoes/tests/test_tria_notion_sync.py`
- Inventário de emails/PDFs: `relatorios/Tria/tria-email-pdf-inventory.json`
- PDFs baixados: `relatorios/Tria/Relatorios PDF/`
- Export estruturado Tria: pasta com `Dados Estruturados/` e `Fotos Visitas/`
- Mapa Drive: `relatorios/Tria/tria-drive-photo-folders.json`
- Base Notion: `Relatórios de Visita`
- Base relacionada: `Ações e Inconformidades`
- Página mãe dos KPIs: `Painel de KPIs — Segurança Alimentar`

## Fluxo

1. Conferir o pacote recebido: PDFs, dados estruturados e fotos.
2. Usar o export estruturado quando existir: `visitas.json`, `nao_conformidades.json`, `reconhecimentos.json`, `plano_acao.json`.
3. Rodar primeiro em `--dry-run` e ler o JSON de saída.
4. Para execução real em lote, confirmar que o Zão pediu a atualização.
5. Sincronizar nesta ordem:
   - extrair fotos dos PDFs antigos quando necessário;
   - criar/reusar pastas do Drive;
   - subir fotos;
   - criar/atualizar Relatórios de Visita;
   - anexar PDF na propriedade `PDF original`;
   - garantir bloco visível para baixar o PDF no corpo da página;
   - criar/arquivar ações e inconformidades;
   - criar/atualizar KPIs mensais.
6. Validar Notion e testes locais antes de dizer que acabou.

## Comando base

Executar dentro de `/root/workspaces/cake-brain`.

```bash
python3 automacoes/scripts/tria_notion_sync.py \
  --structured-export-dir relatorios/Tria/exportacao-estruturada-2026 \
  --extract-pdf-photos \
  --sync-drive-photos \
  --upload-drive-photos \
  --enrich-from-pdf \
  --replace-body \
  --ensure-body-pdf-block \
  --create-actions \
  --archive-extra-actions \
  --sync-monthly-kpis
```

Adicionar `--dry-run` antes da execução real.

## Credenciais

- Usar `NOTION_TOKEN` ou `NOTION_API_KEY` apenas via ambiente/1Password.
- Não imprimir token, API key, cookie, link secreto ou qualquer credencial.
- Para Drive, usar o `gog` com conta `cakebigdog@gmail.com` e cliente `cakebigdog`, sem expor credenciais.

## Validação mínima

Rodar:

```bash
python3 -m unittest automacoes.tests.test_tria_notion_sync -v
python3 -m py_compile automacoes/scripts/tria_notion_sync.py
git diff --check -- automacoes/scripts/tria_notion_sync.py automacoes/tests/test_tria_notion_sync.py skills/tria-checklist-notion/SKILL.md
```

Para fechamento de Notion/Drive, checar no resumo ou via API:

- `errors=[]`
- `missing_pdf=0`
- `missing_visible_file_block=0`
- `no_drive=0`
- `missing_icons=0`
- todos os relatórios processados têm corpo preenchido
- KPIs mensais existem para todos os meses/anos com visita

## Padrão visual esperado

Manter a lógica visual usada nos relatórios jan-mar/2026:

- `📆` calendário/período
- `🥇🥈🥉` rankings
- `🔴` criticidade
- `🏷️` categoria
- `📄` relatório/documentação
- `🧽` higiene
- `📦` estoque/validade
- `🔧` manutenção
- `🌡️` temperatura
- `🏗️` edificação
- `🐞` pragas
- `🚨` alerta
- `⚠️` atenção
- `✅` estado zerado/conforme

## Cuidados

- Não apagar páginas antigas sem opção explícita de arquivamento do script.
- Não substituir formatação manual sem `--replace-body` e autorização clara.
- Não duplicar ações: usar `--archive-extra-actions` só quando a fonte estruturada atual for a referência correta.
- Se a consulta Notion ou Drive falhar, parar e diagnosticar; não repetir POST/PUT em massa no escuro.
- Depois de execução relevante, registrar memória/handoff e versionar apenas código/skill/docs, não exports brutos nem credenciais.
