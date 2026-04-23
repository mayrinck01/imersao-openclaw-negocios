# Estudo: Problema de Atribuição Google Ads — Cake & Co
**Data:** 20/03/2026 | **Elaborado por:** BigDog

---

## 1. DIAGNÓSTICO — O QUE ESTÁ ACONTECENDO

### O Problema Central
Os anúncios do Google Ads estão mandando tráfego para a **página institucional** (`www.cakeco.com.br`) ao invés da **página de vendas** (`pedido.cakeco.com.br/cakeco`). O GA4 **não está instalado** no `www.cakeco.com.br`, o que causa invisibilidade total das conversões.

### O Fluxo Atual (com problema)
```
Usuário clica no anúncio
       ↓
www.cakeco.com.br  ← GA4 NÃO está aqui
  (1 sessão GA4 google/cpc registrada — mas sem conversão possível)
       ↓
Usuário clica em "Fazer Pedido"
       ↓
pedido.cakeco.com.br/cakeco  ← GA4 ESTÁ aqui
  (nova sessão começa como "Direct" — atribuição original PERDIDA)
       ↓
Compra realizada → atribuída ao Direct ❌
```

### Evidências nos Dados

| Dado | Número | Significado |
|------|--------|-------------|
| Cliques reportados pelo Google Ads | **5.605** | Cliques reais pagos |
| Sessões `google/cpc` no GA4 | **12** | Apenas quem chegou direto no pedido |
| Sessões perdidas | **5.593 (99,8%)** | Foram para www.cakeco.com.br sem GA4 |
| `www.cakeco.com.br` no GA4 | **0 sessões** | Confirmado: sem GA4 instalado |
| Compras atribuídas ao "Direct" | **111 compras / R$26.556** | Grande parte são anúncios pagos disfarçados |

---

## 2. CAMPANHAS ATIVAS E SEU PROBLEMA

### Campanhas rodando agora (março 2026):

| Campanha | Tipo | Gasto/mês | URL de destino | Status |
|----------|------|-----------|---------------|--------|
| CAMP 1 - PESQUISA | Search | R$ 1.799 | `www.cakeco.com.br` ❌ | Ativo |
| [PERF MAX][14/11/25] | Performance Max | R$ 1.531 | Automático (Google escolhe) ⚠️ | Ativo |
| **Total investido** | | **R$ 3.330** | | |

### Campanhas pausadas (para referência):

| Campanha | Tipo | URL que usava |
|----------|------|--------------|
| [REDE DE DISPLAY][03/02] | Display | `pedido.cakeco.com.br/cakeco` ✅ |
| Conversão Site | Search | `www.cakeco.com.br` ❌ |
| Rede pesquisa | Search | `www.cakeco.com.br` ❌ |

**Observação importante:** A única campanha que usava a URL correta (`pedido.cakeco.com.br`) está **pausada**. Todas as ativas apontam para o lugar errado.

---

## 3. IMPACTO FINANCEIRO ESTIMADO

### Receita "invisível" no Google Ads
- Compras Direct no GA4: **111 compras — R$ 26.556**
- Estimativa de quanto é do Google Ads: se a proporção de cliques for representativa, uma parte significativa dessas compras veio de anúncios pagos que perderam atribuição

### ROAS Real vs ROAS Aparente
| | Aparente (hoje) | Estimado (real) |
|---|---|---|
| Gasto Google Ads | R$ 3.330 | R$ 3.330 |
| Receita atribuída | R$ 232 | Desconhecido — possivelmente R$ 5k–15k |
| ROAS | 0,07x ❌ | Possivelmente 2x–5x |

---

## 4. AS DUAS FUNÇÕES — ONDE A GESTORA TEM RAZÃO

Existe uma lógica legítima em ter campanhas apontando para `www.cakeco.com.br`:

### Função 1 — Branding / Awareness / SEO Pago
- Objetivo: aparecer nas buscas do nome da marca, ganhar presença
- Destino correto: `www.cakeco.com.br` (página institucional)
- Métrica de sucesso: impressões, cliques, reconhecimento de marca
- **Problema atual:** sem GA4 instalado no www, não há como medir nada

### Função 2 — Conversão / Venda Direta
- Objetivo: gerar compras no site
- Destino correto: `pedido.cakeco.com.br/cakeco` (loja)
- Métrica de sucesso: compras, ROAS, receita
- **Problema atual:** as campanhas de conversão (CAMP 1 - PESQUISA) apontam para o lugar errado

---

## 5. O QUE PRECISA SER FEITO — TRÊS CAMINHOS

### Caminho A — Mínimo (rápido, baixo risco)
**Mudar URL da CAMP 1 - PESQUISA para `pedido.cakeco.com.br/cakeco`**
- Campanha de maior gasto e foco em conversão
- Performance Max continua com URL automática (Google escolhe)
- Resultado esperado: atribuição correta, ROAS visível em ~7 dias
- Risco: baixo

### Caminho B — Completo (recomendado)
1. **Instalar GA4 no `www.cakeco.com.br`** — passa a medir tudo no site institucional
2. **Configurar cross-domain tracking** entre `www.cakeco.com.br` e `pedido.cakeco.com.br` — a sessão do usuário não quebra mais quando ele vai de uma para outra
3. **Separar campanhas por objetivo:**
   - Branding → `www.cakeco.com.br` (com GA4 instalado)
   - Conversão → `pedido.cakeco.com.br/cakeco`
4. **Resultado:** visibilidade total da jornada do cliente, atribuição correta

### Caminho C — Simples e direto
**Apontar tudo para `pedido.cakeco.com.br/cakeco`**
- Mais simples, menos configuração
- Perde a jornada pelo site institucional
- Risco: usuários que queriam ver o site antes de comprar podem converter menos

---

## 6. RECOMENDAÇÃO DO BIGDOG

**Curto prazo (fazer agora):**
> Mudar a CAMP 1 - PESQUISA para `pedido.cakeco.com.br/cakeco`. Resultado imediato em atribuição.

**Médio prazo (próximas 2 semanas):**
> Instalar GA4 + cross-domain tracking entre os dois domínios. Com isso temos a jornada completa visível.

**Não fazer:**
> Mudar o Performance Max sem entender o que o Google está escolhendo como URL. Esse tipo de campanha tem lógica própria de otimização — mexer sem dados pode piorar.

---

## 7. PERGUNTAS PARA DISCUTIR COM A GESTORA

1. **A CAMP 1 - PESQUISA foi criada com objetivo de conversão ou branding?** Se conversão, a URL está errada.

2. **O Performance Max está rodando com asset group apontando para onde?** O Google pode estar escolhendo tanto `www` quanto `pedido` — precisa verificar.

3. **Por que a campanha de Display que usava `pedido.cakeco.com.br` foi pausada?** Era a única com URL correta.

4. **Tem acesso ao GTM (Google Tag Manager) do `www.cakeco.com.br`?** Se sim, instalar o GA4 no www é rápido (menos de 1 hora).

5. **As 153 conversões que o Google Ads reporta — quais eventos são?** Com a correção que fizemos hoje (valor real), os próximos relatórios vão mostrar o breakdown correto.

---

## 8. CONTEXTO — O QUE MUDAMOS HOJE

- ✅ Conversão "COMPRA" agora usa **valor real da transação** (antes: R$100 fixo por compra)
- ✅ O algoritmo do Google vai passar a otimizar para receita real
- ⏳ Efeito nos relatórios: ~7 dias para os dados aparecerem corretamente

---

*Estudo preparado por BigDog para discussão com gestora de tráfego pago.*
*Dados: GA4 Property 432160737 + Google Ads Customer 585-316-3512 | Período: 01/03–19/03/2026*
