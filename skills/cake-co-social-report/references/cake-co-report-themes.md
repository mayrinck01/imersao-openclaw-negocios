---
name: cake-co-report-themes
description: Catálogo de temas visuais para relatórios HTML interativos do Cake & Co (boards, dashboards, comparativos). Define paleta default, alternativas, fontes e snippets prontos para aplicação direta.
version: 1.0
default_theme: modern-minimalist
created: 2026-05-05
maintainer: João Mayrinck — CEO Cake & Co
related_skills:
  - theme-factory (origem das paletas)
  - frontend-design (estrutura HTML/CSS)
---

# Cake & Co · Catálogo de Temas para Relatórios Visuais

Este documento é um catálogo acionável. Define a identidade visual padrão dos relatórios do Cake & Co e oferece variações pré-aprovadas para contextos específicos.

## Uso pelo agente

Quando o usuário solicitar geração de relatório, board, dashboard ou report visual em HTML:

1. **Default**: aplicar tema `modern-minimalist` salvo se outro for explicitamente solicitado.
2. **Estrutura base**: usar o template HTML do board Q1 2026 como ponto de partida (KPIs em grid 4 colunas, filtros sticky por canal e mês, 5 capítulos com Chart.js, tabelas detalhadas, footer com nota técnica).
3. **Aplicação do tema**: substituir três blocos do template — Google Fonts URL, CSS custom properties (`:root`) e objeto de cores JavaScript (`const C = { ... }` para Chart.js).
4. **Não improvisar paletas novas** sem confirmação do usuário. Se nenhum tema servir, apresentar a lista e perguntar.

## Triggers

- "relatório visual", "board", "dashboard", "report" → tema default
- "aplica tema [nome]" → trocar para o tema solicitado
- "executivo / sóbrio / dados" → modern-minimalist
- "premium / acolhedor / artesanal" → golden-hour
- "fashion / sofisticado / requinte" → desert-rose
- "luxury / dramático / impacto" → midnight-galaxy ou coral-dark

## Default · Modern Minimalist

Tema oficial para relatórios executivos do Cake & Co. Justificativa: máxima legibilidade de dados financeiros, atemporal, comunica seriedade sem ser frio, funciona tanto em projeção quanto em PDF impresso.

### Quando usar
- Boards executivos de rotina (mensal, quadrimestral, anual)
- Relatórios para sócios, contabilidade, auditoria
- Apresentações para banco, investidor ou parceiro institucional
- Qualquer relatório onde a hierarquia da informação importa mais que a identidade visual

### Paleta (origem: theme-factory · Modern Minimalist)
- **Charcoal** `#36454F` — primário, texto e elementos âncora
- **Slate Gray** `#708090` — secundário, acentos
- **Light Gray** `#D3D3D3` — backgrounds e dividers
- **White** `#FFFFFF` — texto contrastado e fundo limpo

### Tipografia
- **Display**: `Space Grotesk` (300–700) — geométrica moderna, headers e KPIs grandes
- **Body**: `DM Sans` (300–700) — humanista geométrica, texto corrido e UI
- **Mono**: `JetBrains Mono` (400–600) — números tabulares, labels técnicos, eixos de gráfico

### Snippet · Google Fonts import
```html
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300..700&family=DM+Sans:opsz,wght@9..40,300..700&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
```

### Snippet · CSS custom properties
```css
:root {
  --mustard:         #36454F;
  --mustard-deep:    #1F2A33;
  --mustard-soft:    rgba(54,69,79,.10);
  --terracotta:      #708090;
  --terracotta-deep: #4A5560;
  --terracotta-soft: rgba(112,128,144,.12);
  --beige:           #D3D3D3;
  --chocolate:       #36454F;
  --bg:              #FAFAFA;
  --bg-2:            #F0F0F0;
  --bg-card:         #FFFFFF;
  --bg-card-2:       #F7F7F7;
  --line:            #E5E5E5;
  --line-2:          #CCCCCC;
  --ink:             #36454F;
  --ink-soft:        #5A6770;
  --muted:           #8A9099;
  --muted-2:         #B0B5BC;
  --green:           #3E7D5C;
  --red:             #9C3D3D;
}
```

### Snippet · font-family declarations
```css
body { font-family: 'DM Sans', sans-serif; }
h1, h2, .card-title, .kpi .v { font-family: 'Space Grotesk', sans-serif; }
.mono, code, .pill, table.dt thead th { font-family: 'JetBrains Mono', monospace; }
```

### Snippet · JS color object para Chart.js
```javascript
const C = {
  bg:'#FAFAFA', bgCard:'#FFFFFF', bgCard2:'#F7F7F7',
  line:'#E5E5E5', line2:'#CCCCCC',
  ink:'#36454F', inkSoft:'#5A6770', muted:'#8A9099',
  mustard:'#36454F', mustardDeep:'#1F2A33',
  terracotta:'#708090', terracottaDeep:'#4A5560',
  beige:'#D3D3D3', beigeDeep:'#A8A8A8',
  green:'#3E7D5C', red:'#9C3D3D',
  chocolate:'#36454F'
};
```

---

## Alternativas pré-aprovadas

### Golden Hour · contexto premium / artesanal acolhedor

Origem: theme-factory. Use quando o relatório for de marketing, customer experience, lançamento de produto ou tiver tom mais celebrativo. Conecta com o produto-fim (confeitaria) sem ser piegas.

**Paleta**
- Mustard `#F4A900` (primário) · Terracotta `#C1666B` (secundário) · Warm Beige `#D4B896` · Chocolate `#4A403A`

**Tipografia**: `Bricolage Grotesque` (display) + `DM Sans` (body) + `JetBrains Mono` (mono)

```html
<link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,300..800&family=DM+Sans:opsz,wght@9..40,300..700&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
```

```javascript
const C = {
  bg:'#FAF4EA', bgCard:'#FFFBF3', bgCard2:'#FAF1DD',
  line:'#E8DCC2', line2:'#D4C4A4',
  ink:'#4A403A', inkSoft:'#6B5E55', muted:'#9C8E80',
  mustard:'#F4A900', mustardDeep:'#D89400',
  terracotta:'#C1666B', terracottaDeep:'#A14F54',
  beige:'#D4B896', beigeDeep:'#B89A78',
  green:'#6B8E4F', red:'#A14F54',
  chocolate:'#4A403A'
};
```

---

### Desert Rose · contexto fashion / requinte sofisticado

Origem: theme-factory. Use para relatórios de marca, comunicação, posicionamento, beleza visual ou apresentações para parceiros de design/branding. Paleta empoeirada que comunica refinamento.

**Paleta**
- Dusty Rose `#D4A5A5` (primário) · Clay `#B87D6D` (secundário) · Sand `#E8D5C4` · Deep Burgundy `#5D2E46`

**Tipografia**: `Playfair Display` (display, serif fashion-editorial) + `Albert Sans` (body humanista) + `JetBrains Mono`

```html
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400..900;1,400..900&family=Albert+Sans:wght@300..700&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
```

```javascript
const C = {
  bg:'#FAF2EC', bgCard:'#FFFBF7', bgCard2:'#F8E8DC',
  line:'#E5D2BF', line2:'#D4B7A0',
  ink:'#5D2E46', inkSoft:'#7D556A', muted:'#A88B8B',
  mustard:'#D4A5A5', mustardDeep:'#B87D6D',
  terracotta:'#B87D6D', terracottaDeep:'#5D2E46',
  beige:'#E8D5C4', beigeDeep:'#C2A290',
  green:'#6B8E4F', red:'#A14F54',
  chocolate:'#5D2E46'
};
```

---

### Midnight Galaxy · contexto luxury / dramático / impacto

Origem: theme-factory. Use quando o relatório precisar gerar impacto visual, em apresentações de gala, eventos especiais ou comunicação de marca premium-noturna. Dark theme cósmico.

**Paleta**
- Deep Purple `#2B1E3E` (base) · Cosmic Blue `#4A4E8F` · Lavender `#A490C2` (accent) · Silver `#E6E6FA` (texto)

**Tipografia**: `Cormorant Garamond` (display, serif dramática) + `Outfit` (body geométrica fina) + `JetBrains Mono`

```html
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300..700;1,300..700&family=Outfit:wght@200..700&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
```

```javascript
const C = {
  bg:'#1A1230', bgCard:'#2B1E3E', bgCard2:'#352849',
  line:'#3D2F54', line2:'#4F4070',
  ink:'#E6E6FA', inkSoft:'#C9C2E0', muted:'#9088B0',
  mustard:'#A490C2', mustardDeep:'#7E6BA0',
  terracotta:'#4A4E8F', terracottaDeep:'#2F3470',
  beige:'#6B5E8C', beigeDeep:'#4F4070',
  green:'#7BC89D', red:'#D88B9A',
  chocolate:'#E6E6FA'
};
```

**Cuidado**: por ser dark, exige mais contraste em pequenos textos. Validar legibilidade em projeção antes de usar para board crítico.

---

### Coral Dark · contexto tech-moderno / SaaS / produto

Origem: design custom (não vem da theme-factory). Inspirado em Linear/Vercel/Stripe Press. Use para relatórios internos da operação, dashboards de produto, ou quando comunicar "Cake & Co como empresa data-driven moderna". Acento coral conecta com produto-top da marca (morango).

**Paleta**
- Off-black quente `#0B0908` (base) · Coral-morango `#FF5B5B` (acento principal) · Champagne `#E8C896` (acento secundário) · Off-white quente `#F2EBE0` (texto)

**Tipografia**: `Instrument Serif` (display itálica moderna) + `Geist` (body Vercel) + `JetBrains Mono`

```html
<link href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Geist:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
```

```javascript
const C = {
  bg:'#0B0908', bg2:'#14110F', bg3:'#1C1815',
  line:'#2A2421', line2:'#3A332E',
  ink:'#F2EBE0', inkSoft:'#C9C0B3', muted:'#8B8278',
  coral:'#FF5B5B', coralDeep:'#E04545',
  champ:'#E8C896', champDeep:'#C9A574',
  green:'#6BCB77', red:'#FF7A7A'
};
```

**Diferença estrutural**: este tema usa nomes de variáveis JS diferentes (`coral`, `champ` em vez de `mustard`, `terracotta`). Se trocar deste para outro, ajustar referências no Chart.js.

---

### Wine Editorial · contexto editorial / publicação / arquivo

Origem: design custom (não vem da theme-factory). Estilo revista de gastronomia / relatório anual de marca premium. Use para relatórios anuais consolidados, livros de marca, materiais para imprensa.

**Paleta**
- Bordô profundo `#7A1F2B` · Dourado fosco `#C9A96E` · Creme quente `#FAF6F0` · Tinta `#1A1614`

**Tipografia**: `Fraunces` (display serif editorial) + `Manrope` (body) + (sem mono dedicada — usa Manrope)

```html
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght,SOFT@9..144,300..900,0..100&family=Manrope:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
```

---

## Critérios de decisão · qual tema escolher

| Cenário | Tema |
|---|---|
| Board mensal/trimestral de rotina | **modern-minimalist** (default) |
| Apresentação para banco/investidor | modern-minimalist |
| Relatório anual consolidado para sócios | wine-editorial ou modern-minimalist |
| Material de marketing / lançamento | golden-hour |
| Apresentação de marca / parceiro de branding | desert-rose |
| Evento especial / gala / aniversário Cake & Co | midnight-galaxy |
| Dashboard interno operacional / time | coral-dark |
| Relatório técnico de produção / processos | modern-minimalist |
| Comunicação para clientes finais | golden-hour |
| Auditoria, contabilidade, fiscal | modern-minimalist |

Em caso de dúvida ou sobreposição de critérios: aplicar default e oferecer ao usuário a possibilidade de trocar.

## Estrutura técnica do template base

O HTML standalone que serve como esqueleto contém:

- **Hero section** com eyebrow animado, título display grande, lead paragraph e meta-row de 4 itens
- **Filterbar sticky** com 2 grupos de filtros (canal: Todos/Loja/Delivery · mês: Todos/Jan/Fev/Mar/Abr) e botão Reset
- **KPI grid** com 4 cards (Faturamento atual, Faturamento anterior, Crescimento, Principal motor) que recalculam dinamicamente conforme filtros
- **5 capítulos** numerados em mono (`/01`, `/02` etc.):
  - 01 Mensal — bar chart agrupado + 3 insights
  - 02 Canal — bar horizontal Δ R$ + donut mix + tabela
  - 03 Combo — bar + line chart com 2 eixos Y (faturamento × ticket médio)
  - 04 Produtos — 3 tabs (Geral / Loja / Delivery) com bar horizontal Top 10
  - 05 Detalhe — tabela mensal completa
- **Note section** com regra de classificação e nota técnica
- **Footer** com brand mark e theme credit

Dependências externas:
- `Chart.js 4.4.1` via cdnjs
- `Google Fonts` conforme tema

Toda a interatividade (filtros, tabs, recálculo de KPIs, redraw de charts) está em JavaScript inline. Sem build step.

## Como aplicar um tema diferente do default

Quando o usuário disser "aplica o tema X" ou "quero o relatório em [tema]":

1. Pegar o template base (último relatório gerado ou template canônico)
2. Substituir o `<link>` do Google Fonts pelo do tema solicitado
3. Substituir o bloco `:root { ... }` com as CSS variables do tema
4. Substituir o objeto `const C = { ... }` no JavaScript
5. Trocar os `font-family` em `body`, headers e elementos mono se as fontes mudarem
6. Atualizar o título da aba (`<title>`) e o crédito do footer (`Theme · [nome]`)
7. Validar que as cores não vazaram do tema antigo (busca por hex codes do tema anterior)

## Notas de manutenção

- **Default não muda sem registro explícito** neste arquivo. Trocar default = atualizar campo `default_theme` no frontmatter.
- **Adicionar tema novo**: criar nova seção seguindo o padrão (paleta, tipografia, snippets, contexto de uso, critério). Atualizar tabela de decisão.
- **Atualização de paleta de tema existente**: bumpar `version` no frontmatter, registrar mudança em changelog (ainda não criado, criar quando primeira atualização ocorrer).
- **Conflito entre tema e brand guidelines do Cake & Co**: brand guidelines vencem. Este catálogo aplica-se apenas a relatórios e dashboards, não a material de marca primária.

## Histórico

- **v1.0 · 2026-05-05**: catálogo inicial com 4 temas da theme-factory (modern-minimalist default, golden-hour, desert-rose, midnight-galaxy) e 2 temas custom (coral-dark, wine-editorial). Geração derivada do board Q1 2026 (Mogo, Venda Analítica).
