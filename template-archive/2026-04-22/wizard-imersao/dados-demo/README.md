# Dados — Como Conectar

> Os dados da empresa podem vir de CSV local OU de Google Sheets. Escolha o que faz sentido pro seu caso.

---

## Opção 1: Google Sheets (recomendado)

A maioria dos negócios já tem seus dados em planilhas do Google. O agente pode ler direto.

### Planilha pública (só leitura — mais fácil)

1. Abrir a planilha no Google Sheets
2. Compartilhar → "Qualquer pessoa com o link pode visualizar"
3. Pegar o ID da planilha (o código longo na URL)
4. O agente lê via export:

```
https://docs.google.com/spreadsheets/d/{ID}/export?format=csv&gid={ABA_ID}
```

Exemplo:
```
https://docs.google.com/spreadsheets/d/1FgaylWNye_UJa6lOrMFtNt4rcBeScJjwpfaHR02oqHc/export?format=csv&gid=0
```

**Vantagem:** zero configuração, funciona em 30 segundos.
**Desvantagem:** só leitura, planilha precisa ser pública (link).

### Planilha privada (leitura + escrita)

Para o agente ler E escrever na planilha (ex: atualizar status de leads):

1. Configurar OAuth com Google (uma vez)
2. Usar GOG CLI (`gog sheets read`, `gog sheets write`) ou API direta
3. O agente consegue ler qualquer aba e escrever em células específicas

**Vantagem:** acesso total, planilha pode ser privada.
**Desvantagem:** setup de OAuth (10 min uma vez).

---

## Opção 2: CSV local

Exportar a planilha como CSV e colocar na pasta `dados/`.

```
Google Sheets → Arquivo → Download → CSV
Salvar em: dados/vendas.csv (ou qualquer nome)
```

**Vantagem:** funciona offline, sem dependência de API.
**Desvantagem:** dados ficam desatualizados (precisa re-exportar).

---

## Qual escolher?

| Cenário | Recomendação |
|---------|-------------|
| Dados mudam todo dia (vendas, leads) | Google Sheets (sempre atualizado) |
| Dados estáticos (lista de produtos, equipe) | CSV ou Markdown |
| Agente precisa escrever (atualizar status) | Google Sheets com OAuth |
| Quer começar rápido (imersão) | Google Sheets público |

---

## Configuração no agente

No `TOOLS.md` do agente, documentar:

```markdown
### Google Sheets
- **Planilha de vendas:** [link da planilha]
  - ID: {id}
  - Aba "Vendas": gid=0
  - Aba "Leads": gid=123456
- **Acesso:** Público (read) / OAuth (read+write)
```

No `AGENTS.md`, na seção de dados:

```markdown
## Dados
- Vendas → Google Sheets (planilha "Vendas da Empresa", aba "2026")
- Leads → Google Sheets (mesma planilha, aba "Pipeline")
- Leitura via export CSV: https://docs.google.com/spreadsheets/d/{ID}/export?format=csv&gid={ABA}
```

---

## Arquivos de exemplo (CSV)

Os CSVs neste repo servem como **referência de estrutura**. Na prática, seus dados provavelmente já estão numa planilha.

- `vendas.csv` — Exemplo de estrutura de dados de vendas
- `leads.csv` — Exemplo de estrutura de pipeline de leads

Use esses CSVs como modelo pra organizar sua própria planilha no Google Sheets.

---

*Atualizado: março 2026*
