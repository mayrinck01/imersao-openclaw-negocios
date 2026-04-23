# Relatório — Tráfego Pago Cake & Co
## Preparado para Julia / Zão
## Data: 31/03/2026

---

## 1. Resposta direta

**Hoje, com os dados internos que já conseguimos recuperar da Cake, não dá para afirmar com segurança que Meta ou Google é a plataforma que mais traz receita total para a Cake sem reabrir a consulta das APIs em tempo real.**

Mas já dá para afirmar 3 coisas importantes:

1. **Existe dado real da Cake mostrando forte distorção de atribuição no Google Ads**
2. **O Google provavelmente está subatribuído nas vendas reportadas**
3. **Qualquer comparação crua entre Meta x Google, sem corrigir atribuição, pode levar a conclusão errada**

---

## 2. O que encontramos de dado real da Cake

Fonte interna recuperada: `memory/projects/estudo-google-ads-atribuicao.md`

### Período analisado
- **01/03 a 19/03/2026**

### Google Ads / GA4 — números reais encontrados
- **Cliques reportados pelo Google Ads:** 5.605
- **Sessões `google/cpc` no GA4:** 12
- **Sessões perdidas:** 5.593 (**99,8%**)
- **Sessões do domínio institucional `www.cakeco.com.br` no GA4:** 0
- **Compras atribuídas a Direct no GA4:** 111 compras
- **Receita atribuída a Direct no GA4:** **R$ 26.556**
- **Receita atribuída aparente ao Google Ads:** **R$ 232**
- **Investimento Google Ads nas campanhas ativas analisadas:** **R$ 3.330**

### Campanhas Google ativas encontradas
- **CAMP 1 - PESQUISA** — Search — **R$ 1.799/mês** — destino `www.cakeco.com.br`
- **[PERF MAX][14/11/25]** — Performance Max — **R$ 1.531/mês** — URL automática
- **Total investido:** **R$ 3.330/mês**

---

## 3. O que esses números significam

### Diagnóstico central
Os anúncios do Google Ads estavam levando tráfego para o domínio institucional (`www.cakeco.com.br`), enquanto a compra acontece em `pedido.cakeco.com.br/cakeco`.

Como o GA4 não estava corretamente instalado / integrado nesse fluxo:
- o clique pago acontecia
- o usuário chegava no site institucional
- depois ia para o site de pedido
- a conversão acabava aparecendo como **Direct**

### Consequência prática
O painel do Google Ads pode estar mostrando uma receita artificialmente baixa.

Ou seja:
- **Google aparenta vender pouco no painel**
- mas **parte relevante da receita pode ter sido desviada para Direct por quebra de atribuição**

---

## 4. Conclusão executiva

### O que NÃO dá para dizer hoje
- que **Meta traz mais receita** que Google
- que **Google traz mais receita** que Meta
- que o valor reportado em cada plataforma reflete a verdade total da operação

### O que já dá para dizer com segurança
- **o Google está com forte indício de subatribuição**
- portanto, **qualquer leitura atual de receita por canal está contaminada**
- antes de responder categoricamente “qual plataforma traz mais receita”, é preciso consolidar:
  - Meta Ads (receita reportada)
  - Google Ads (receita reportada)
  - GA4 / e-commerce (receita observada)
  - atribuição corrigida entre os domínios

---

## 5. Melhor resposta de negócio para Julia

### Versão objetiva
**Julia, olhando os dados internos da Cake que já recuperamos, hoje eu não consigo te dizer com segurança qual plataforma mais traz receita porque a atribuição do Google está claramente quebrada.**

**Os números mostram 5.605 cliques no Google Ads entre 01 e 19/03, mas só 12 sessões `google/cpc` apareceram no GA4, enquanto 111 compras e R$ 26.556 ficaram atribuídos a Direct.**

**Isso indica que o Google provavelmente está subatribuído e que comparar Meta x Google do jeito que está hoje pode distorcer a conclusão.**

**Então, a resposta correta é:**
- hoje **não dá para afirmar com segurança** qual traz mais receita real
- primeiro precisamos corrigir / consolidar a atribuição
- depois comparar **receita, investimento, ROAS e número de pedidos** por canal

---

## 6. Resposta curta para WhatsApp

**Julia, com base nos dados internos que já recuperei da Cake, hoje eu ainda não cravaria qual plataforma traz mais receita real.**

**Motivo:** a atribuição do Google está quebrada. Entre 01 e 19/03 o Google Ads reportou **5.605 cliques**, mas o GA4 registrou só **12 sessões `google/cpc`**, enquanto **111 compras / R$ 26.556** ficaram como **Direct**.

**Ou seja:** o Google provavelmente está subatribuído, então comparar Meta x Google do jeito que está hoje pode levar a uma conclusão errada.

**Minha leitura:** antes de responder “quem vende mais”, precisamos consolidar a receita real por canal com atribuição corrigida.

---

## 7. Posição do BigDog

Se eu tivesse que orientar a decisão do Zão agora:

- **não responderia com chute**
- **não usaria benchmark de mercado como se fosse dado da Cake**
- **não concluiria Meta > Google nem Google > Meta enquanto a atribuição estiver quebrada**

A resposta madura é:
> **Hoje os dados da Cake indicam que o Google está mal medido. Então a pergunta certa não é só “qual plataforma vende mais?”, mas “qual plataforma está sendo corretamente medida?”.**

---

## 8. Próximo passo recomendado

1. Reabrir consulta das APIs / painéis com autenticação operacional
2. Extrair para o mesmo período:
   - investimento Meta
   - receita Meta
   - investimento Google
   - receita Google
   - pedidos por canal
   - ticket médio por canal
3. Validar GA4 / cross-domain
4. Refazer a resposta final com base consolidada

---

## Fonte interna usada
- `memory/projects/estudo-google-ads-atribuicao.md`
- `memory/sessions/2026-03-30.md`
