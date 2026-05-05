---
name: cake-co-social-report
description: Use quando o usuário pedir relatório, dashboard, board ou análise de redes sociais/performance digital do Cake & Co. Cobre Instagram, Facebook, TikTok e LinkedIn orgânicos, Meta Ads, Google Ads e GA4; define modalidade, fontes, KPIs, fórmulas, estrutura HTML standalone e visualização Chart.js.
version: 1.0
default_theme: modern-minimalist
default_frequency: monthly
platforms:
  - instagram
  - facebook
  - tiktok
  - linkedin
data_sources:
  primary:
    - meta_business_suite (Instagram + Facebook orgânico)
    - meta_ads_manager (Meta Ads pago)
    - google_ads
    - google_analytics
  secondary:
    - tiktok_analytics (export manual)
    - linkedin_analytics (export manual)
created: 2026-05-05
maintainer: João Mayrinck — CEO Cake & Co
related_skills:
  - cake-co-report-themes (visual e tipografia; referência embutida em references/cake-co-report-themes.md)
  - frontend-design (estrutura HTML/CSS)
---

# Cake & Co · Skill para Relatórios de Gestão de Rede Social

Catálogo acionável para geração de relatórios sociais. Define o que medir, como estruturar, qual frequência usar e como visualizar.

## Uso pelo agente

Quando o usuário solicitar relatório de rede social, social media, mídia social, performance digital, redes sociais ou termos correlatos:

1. **Identificar a modalidade** (mensal, quinzenal, semanal ou de campanha) — se não estiver claro, perguntar antes de gerar.
2. **Confirmar o período** com datas exatas (início e fim).
3. **Pedir as fontes de dados** se ainda não fornecidas — listar exatamente o que precisa (ver seção *Origem dos dados*).
4. **Aplicar tema visual** lendo `references/cake-co-report-themes.md` (default `modern-minimalist`).
5. **Estruturar o output em HTML standalone** com filtros interativos por plataforma, mesmo padrão do template canônico.
6. **Não inventar dados**. Se faltar métrica, marcar como `n/d` no relatório e listar as métricas ausentes ao usuário no final.
7. **Não usar dados de mais de uma fonte sem reconciliação** — se Google Analytics e Meta Business Suite divergirem (sempre divergem), informar a divergência ao usuário.

## Triggers

- "relatório de rede social", "social media report", "performance das redes"
- "como foi o Instagram em [período]"
- "fechamento do mês das redes"
- "relatório semanal de social"
- "relatório da campanha [nome]"
- "como foram os anúncios"

## Modalidades de relatório

### A · Mensal — Consolidação estratégica
Frequência padrão. Foco: visão completa, recomendações estratégicas para o mês seguinte.

**Capítulos obrigatórios:**
1. Visão geral consolidada (KPIs do orgânico + pago + site)
2. Performance por plataforma (1 seção para cada das 4 redes)
3. Funil de marketing (alcance → engajamento → tráfego → conversão)
4. Top conteúdos do mês (5 melhores por engagement rate)
5. Tráfego pago (Google Ads + Meta Ads)
6. Site (Google Analytics)
7. Recomendações para o próximo mês

**Comparativo**: mês anterior (M-1) e mesmo mês ano anterior (Y-1) quando disponível.

### B · Quinzenal — Acompanhamento ativo
Foco: tendências em curso, ajustes táticos, antecipar problemas.

**Capítulos obrigatórios:**
1. Resumo da quinzena (5–7 KPIs principais)
2. O que está subindo / o que está caindo (deltas vs quinzena anterior)
3. Top 3 conteúdos
4. Recomendações táticas para a próxima quinzena

**Comparativo**: quinzena anterior + média histórica (últimas 4 quinzenas).

### C · Semanal — Operação
Foco: rotina, alertas, próximas ações. Curto.

**Capítulos obrigatórios:**
1. KPIs da semana (5 números: alcance total, engajamento total, novos seguidores, cliques no link, conversões)
2. Alertas (qualquer métrica caiu mais de 20%? subiu mais de 50%?)
3. Top 1 conteúdo da semana
4. Próximos posts agendados (se a equipe usar planejamento editorial)

**Comparativo**: semana anterior.

### D · Por campanha — Eventual
Foco: investimento × resultado de uma campanha específica.

**Capítulos obrigatórios:**
1. Briefing rápido (objetivo, período, investimento, plataformas)
2. Antes × durante × depois (linha de tendência das KPIs)
3. Performance pago (CPA, CTR, ROAS)
4. Performance orgânico (alcance, engajamento, top posts da campanha)
5. Conversões atribuídas
6. Aprendizados consolidados

**Comparativo**: média do período fora da campanha + benchmark contra outras campanhas anteriores.

## Catálogo de KPIs por plataforma

### Instagram (via Meta Business Suite)

**Métricas de alcance e exposição**
- Alcance (`reach`) — pessoas únicas que viram o conteúdo
- Impressões (`impressions`) — total de visualizações
- Visitas ao perfil (`profile_views`)

**Métricas de engajamento**
- Curtidas, comentários, salvamentos, compartilhamentos
- Engagement rate por alcance: `((curtidas + comentários + salvamentos + compartilhamentos) / alcance) × 100`
- Engagement rate por seguidores: `((curtidas + comentários + salvamentos + compartilhamentos) / seguidores) × 100`

**Métricas de crescimento**
- Total de seguidores
- Crescimento líquido: `seguidores_fim - seguidores_início`
- Taxa de crescimento: `(crescimento líquido / seguidores_início) × 100`

**Stories**
- Visualizações
- Respostas
- Toques (avançar / voltar / saída)
- Taxa de conclusão: `((views_último_card / views_primeiro_card)) × 100`

**Reels**
- Plays
- Reproduções
- Curtidas, comentários, compartilhamentos, salvamentos
- Tempo médio de visualização
- Taxa de retenção

**Cliques no link** (bio ou link sticker)

### Facebook (via Meta Business Suite)

- Alcance da página
- Impressões
- Curtidas da página (total + crescimento líquido)
- Engajamentos totais (reações + comentários + compartilhamentos + cliques)
- Reações por tipo (curtir, amei, haha, uau, triste, grr)
- Cliques em links
- Engagement rate: `(engajamentos / alcance) × 100`

### TikTok (via TikTok Analytics — export manual)

- Visualizações totais
- Tempo médio de visualização
- Taxa de retenção (% de vídeo assistido em média)
- Curtidas, comentários, compartilhamentos, salvamentos
- Total de seguidores + crescimento líquido
- Visualizações do perfil
- Visitas ao link na bio (se houver)
- Engagement rate: `((curtidas + comentários + compartilhamentos + saves) / visualizações) × 100`

### LinkedIn (via LinkedIn Analytics — export manual)

- Impressões
- Engajamentos (curtidas + comentários + compartilhamentos + cliques)
- Engagement rate: `(engajamentos / impressões) × 100`
- Total de seguidores + crescimento líquido
- Visualizações da página da empresa
- Cliques únicos no site

### Google Ads (via Google Ads dashboard ou export)

- Investimento total (R$)
- Impressões
- Cliques
- CTR (click-through rate): `(cliques / impressões) × 100`
- CPC médio (cost per click): `investimento / cliques`
- Conversões (definidas previamente: cliques no WhatsApp, formulário, ligação, redirecionamento iFood)
- CPA (cost per acquisition): `investimento / conversões`
- Taxa de conversão: `(conversões / cliques) × 100`
- ROAS (return on ad spend): `receita atribuída / investimento`

### Google Analytics (GA4 — site)

- Sessões totais
- Usuários únicos
- Novos usuários
- Taxa de rejeição (bounce rate)
- Tempo médio de sessão
- Páginas por sessão
- Páginas mais visitadas (top 10)
- Origem do tráfego (orgânico / direto / social / pago / referral)
- Conversões configuradas (eventos: clique no WhatsApp, clique no iFood, formulário, etc.)
- Funil de conversão se configurado

### Meta Ads (via Meta Business Suite — separar do orgânico)

- Investimento total
- Impressões pagas
- Alcance pago
- CPM (custo por mil impressões)
- CPC, CTR, conversões, CPA, ROAS (mesmas fórmulas do Google Ads)
- Frequência média (impressões / alcance)

## Estrutura padrão do dashboard HTML

Reaproveitar o template base do board Q1 2026 (definido em `cake-co-report-themes.md`). Adaptações específicas para social:

### Hero
- Eyebrow: `Cake & Co · Social Report · [modalidade] · [período]`
- Título: definir conforme modalidade
- Meta-row: 4 itens (Período · Plataformas analisadas · Fonte dos dados · Última atualização)

### Filtros sticky
- **Plataforma**: Todas / Instagram / Facebook / TikTok / LinkedIn / Site
- **Tipo de mídia**: Tudo / Orgânico / Pago
- **Mês ou Semana**: conforme modalidade

### KPIs (grid de 4 cards) — modalidade mensal
1. Alcance total consolidado · com delta vs M-1
2. Engajamento total · com delta vs M-1
3. Crescimento líquido de seguidores (soma das 4 redes)
4. Conversões atribuídas (Analytics + Ads)

### KPIs (grid de 4 cards) — modalidade semanal
1. Alcance da semana
2. Engajamento da semana
3. Novos seguidores
4. Cliques no link consolidados

### Capítulos (modalidade mensal completa)

**01 · Visão geral**
- Bar chart agrupado: alcance por plataforma (atual vs M-1)
- Donut: mix de engajamento por plataforma

**02 · Por plataforma** (4 cards expansíveis ou 4 seções)
- Para cada: KPIs da plataforma + line chart de evolução diária + top 3 posts

**03 · Funil de marketing**
- Funnel chart: Impressões → Alcance → Engajamento → Cliques no link → Sessões no site → Conversões
- Taxa de conversão de cada etapa

**04 · Top conteúdos do mês**
- Tabela ordenada por engagement rate
- Colunas: thumb, plataforma, data, formato (post/reel/story/vídeo), alcance, engajamento, ER%, link

**05 · Tráfego pago**
- Bar chart investimento por plataforma
- Tabela com KPIs de campanha (CTR, CPC, CPA, ROAS)
- Linha do tempo investimento × conversões

**06 · Site (Google Analytics)**
- KPIs principais (sessões, usuários, conversões)
- Donut: origem do tráfego
- Tabela: top 10 páginas

**07 · Recomendações**
- Bullet points consolidados (gerar a partir da análise)
- 3 ações sugeridas para o próximo mês

## Origem dos dados — checklist para o agente

Antes de gerar relatório, confirmar com usuário se ele tem:

- [ ] Export do Meta Business Suite do período (CSV/XLSX) — Instagram + Facebook
- [ ] Export do TikTok Analytics (manual via Studio)
- [ ] Export do LinkedIn Analytics (manual via página da empresa)
- [ ] Export do Meta Ads Manager/Business Suite pago (campanhas, investimento e conversões)
- [ ] Export do Meta Ads Manager/Business Suite pago (campanhas, investimento e conversões)
- [ ] Export do Google Ads (relatório customizado por campanha ou geral)
- [ ] Export do Google Analytics 4 (relatório de aquisição + comportamento + conversões)

Se faltar alguma fonte, prosseguir com o que tem e marcar as ausentes na seção de notas técnicas do relatório final. Nunca preencher com estimativa.

**Formato esperado dos exports** (configurar com a equipe se ainda não estiver padronizado):
- Período: corresponder exatamente ao período do relatório
- Granularidade: diária quando possível
- Encoding: UTF-8
- Formato preferencial: XLSX

## Framework de análise — leitura dos resultados

Quando interpretar os números, aplicar este checklist:

1. **Tendência** — está subindo, descendo ou estável? (vs período anterior + média histórica)
2. **Sazonalidade** — período coincide com data sazonal (Páscoa, Natal, Dia das Mães etc.)? Comparar contra mesmo período ano anterior.
3. **Outliers** — algum post explodiu? algum despencou? buscar a causa antes de incluir na análise.
4. **Conversão** — engajamento subiu mas conversão não → problema no funil. Conversão subiu sem engajamento subir → tráfego pago carregando o resultado.
5. **Plataforma dominante** — qual está puxando crescimento? qual está estagnada?
6. **Custo/eficiência** — CPA está dentro do meta? Comparar com média histórica (definir meta com usuário se não existir ainda).
7. **Efeito cross-channel** — campanha em uma plataforma puxou tráfego em outras? GA mostra origem.

## Snippets · Chart.js para gráficos típicos

### Funnel chart (tipo bar horizontal decrescente)
```javascript
new Chart(ctx, {
  type: 'bar',
  data: {
    labels: ['Impressões', 'Alcance', 'Engajamento', 'Cliques link', 'Sessões site', 'Conversões'],
    datasets: [{
      data: [valor1, valor2, valor3, valor4, valor5, valor6],
      backgroundColor: [C.mustard, C.mustardDeep, C.terracotta, C.terracottaDeep, C.beige, C.beigeDeep],
      borderRadius: 6
    }]
  },
  options: {
    indexAxis: 'y',
    plugins: { legend: { display: false } },
    scales: { x: { ticks: { callback: v => v.toLocaleString('pt-BR') } } }
  }
});
```

### Growth chart (line, 1 linha por plataforma)
```javascript
new Chart(ctx, {
  type: 'line',
  data: {
    labels: ['Sem 1', 'Sem 2', 'Sem 3', 'Sem 4'],
    datasets: [
      { label: 'Instagram', data: [...], borderColor: C.mustard, tension: 0.4 },
      { label: 'Facebook', data: [...], borderColor: C.terracotta, tension: 0.4 },
      { label: 'TikTok', data: [...], borderColor: C.beige, tension: 0.4 },
      { label: 'LinkedIn', data: [...], borderColor: C.green, tension: 0.4 }
    ]
  }
});
```

### Top posts ranking (bar horizontal)
```javascript
new Chart(ctx, {
  type: 'bar',
  data: {
    labels: ['Post 1', 'Post 2', 'Post 3', 'Post 4', 'Post 5'],
    datasets: [{ data: [er1, er2, er3, er4, er5], backgroundColor: C.mustard, borderRadius: 6 }]
  },
  options: { indexAxis: 'y', plugins: { legend: { display: false } } }
});
```

### Donut · mix por plataforma
```javascript
new Chart(ctx, {
  type: 'doughnut',
  data: {
    labels: ['Instagram', 'Facebook', 'TikTok', 'LinkedIn'],
    datasets: [{
      data: [eng_ig, eng_fb, eng_tt, eng_li],
      backgroundColor: [C.mustard, C.terracotta, C.beige, C.green],
      borderColor: C.bgCard, borderWidth: 3
    }]
  },
  options: { cutout: '66%' }
});
```

### Investimento × resultado (combo bar+line)
```javascript
new Chart(ctx, {
  type: 'bar',
  data: {
    labels: ['Sem 1', 'Sem 2', 'Sem 3', 'Sem 4'],
    datasets: [
      { type: 'bar', label: 'Investimento', data: [...], backgroundColor: C.beige, yAxisID: 'y' },
      { type: 'line', label: 'Conversões', data: [...], borderColor: C.mustard, yAxisID: 'y1', tension: 0.4 }
    ]
  },
  options: {
    scales: {
      y: { position: 'left', title: { display: true, text: 'R$' } },
      y1: { position: 'right', grid: { display: false }, title: { display: true, text: 'Conversões' } }
    }
  }
});
```

## Critérios de decisão · qual modalidade aplicar

| Solicitação do usuário | Modalidade |
|---|---|
| "Fechamento do mês" | mensal |
| "Como foi o mês" | mensal |
| "Quinzenal" / "últimas duas semanas" | quinzenal |
| "Como tá indo" / "performance dessa semana" | semanal |
| "Resultado da campanha [X]" | por campanha |
| Pedido sem especificação clara | perguntar antes de gerar |

## Como combinar com a skill de temas

Esta skill cuida do **conteúdo** do relatório. A referência `references/cake-co-report-themes.md` cuida da **forma**. Ordem de aplicação:

1. Decidir a modalidade (esta skill)
2. Decidir tema visual (referência de temas — default `modern-minimalist`)
3. Aplicar template HTML base (definido na skill de temas)
4. Substituir o conteúdo padrão pelos capítulos e KPIs definidos aqui
5. Validar que dados foram tratados conforme as fórmulas deste catálogo
6. Entregar HTML standalone

## Notas de manutenção

- **Mudança nas plataformas usadas pelo Cake & Co**: atualizar lista de `platforms` no frontmatter e adicionar/remover seções correspondentes do catálogo de KPIs.
- **Mudança em fonte de dados** (ex: passar a usar SprintHub ao invés de export manual): atualizar `data_sources` e a seção *Origem dos dados*.
- **Definição de metas/benchmarks**: quando definidos, incluir tabela `metas_anuais` no frontmatter para o agente comparar resultados contra a meta.
- **Conversões**: a definição do que conta como conversão para Cake & Co precisa ficar registrada explicitamente. Sugestão para registro futuro: clique no WhatsApp, clique no botão iFood, preenchimento de formulário do site, ligação. Confirmar com o usuário antes de assumir.
- **Bumpar `version`** sempre que houver mudança no escopo, não em ajustes editoriais.

## Histórico

- **v1.0 · 2026-05-05**: catálogo inicial. 4 plataformas (Instagram, Facebook, TikTok, LinkedIn). 4 modalidades (mensal, quinzenal, semanal, por campanha). Fontes: Meta Business Suite, Google Ads, Google Analytics. Tema visual default herdado de `cake-co-report-themes.md` (modern-minimalist).
