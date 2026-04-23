# SKILL — Criação de Criativos

## O Que Faz
Dado um ângulo e formato aprovado, gera o criativo completo: copy, roteiro de vídeo ou especificação de imagem, pronto para produção pelo designer ou editor.

---

## Input
- **Ângulo:** nome e descrição do ângulo aprovado (ex: "dor financeira — processos manuais")
- **Formato:** vídeo 15s / vídeo 30s / imagem feed / carrossel / stories estático
- **Público-alvo:** cold / warm / remarketing
- **CTA:** qual ação queremos que o lead tome

## Processo

### 1. Buscar Specs do Formato
| Formato | Dimensões | Duração | Texto |
|---------|-----------|---------|-------|
| Reels/Stories vídeo | 1080x1920 | 15s ou 30s | Mínimo — hook falado |
| Feed vídeo | 1080x1080 | 15-60s | Overlay opcional |
| Imagem feed | 1080x1080 | — | Headline + CTA |
| Carrossel | 1080x1080 | — | 4-6 cards |
| Stories estático | 1080x1920 | — | Pouco texto |

### 2. Aplicar Learnings ao Formato
- Vídeo: começa com hook nos primeiros 1,5s (sem logo)
- Inclui overlay numérico se cold traffic
- CTA verbal nos últimos 3s
- Imagem: face em destaque + headline com número

### 3. Gerar Copy e Roteiro

**Para vídeo:** estrutura cena a cena
```
[0-3s] HOOK — frase de abertura + overlay
[3-10s] PROBLEMA — agravamento da dor
[10-13s] SOLUÇÃO — apresentação da empresa/serviço
[13-15s] CTA — "Fale com especialista, link na bio"
```

**Para imagem:** copy completo
```
Headline: [texto principal com número]
Subheadline: [complemento]
CTA: [botão ou texto de ação]
Instruções visuais: [cor, posição de rosto, estilo]
```

### 4. Briefing de Produção
- Referências visuais (se houver)
- Tom: direto/urgente/empático
- Elementos obrigatórios (logo, cores, fontes da marca)
- Prazo de entrega

## Output

### Para criativos estáticos (formato obrigatório: Stack Ad Creator Pixel)

**Regra:** Todo criativo estático sugerido DEVE usar o formato Stack Ad Creator Pixel.

**Fluxo obrigatório ao sugerir um estático:**
1. Apresentar o brief com hook, subtítulo e 3 cards de benefício (só texto — sem sugestão de foto de fundador, avatar ou imagem de pessoa)
2. Perguntar ao usuário: *"Quer que eu já gere no formato Stack Ad Creator Pixel?"*
3. Se confirmado, montar o `config.json` e rodar o script:

```bash
python3 cerebro/empresa/skills/stack-ad-creator-pixel/scripts/generate.py config.json
```

**Estrutura do config.json para estático:**
```json
{
  "product_badge": "Nome do Produto",
  "h1": ["Linha 1 do headline", "<em>Linha 2 em italic+gradient.</em>"],
  "pricing": {
    "was": "R$297",
    "value": "R$97",
    "label": "Acesso vitalício",
    "condition": "Condição de lançamento"
  },
  "output_dir": "./banners",
  "formats": ["post", "story"],
  "copies": [
    {
      "key": "a-nome",
      "label": "Copy A — Ângulo",
      "subtitle": "Texto do subtítulo com <strong>destaques em branco.</strong>",
      "cards": [
        ["Título do benefício 1", "Descrição em 1 frase."],
        ["Título do benefício 2", "Descrição em 1 frase."],
        ["Título do benefício 3", "Descrição em 1 frase."]
      ]
    }
  ]
}
```

**Regras de copy para o Stack:**
- `h1`: máx 3 linhas. Parte emocional/CTA em `<em>` (fica em italic + gradient laranja)
- `subtitle`: números e termos-chave em `<strong>` (ficam em branco)
- `cards`: exatamente 3 por copy — benefício direto, sem enrolação
- **Sem menção a imagem de fundador, avatar ou foto de pessoa** — o formato é 100% tipográfico

### Para vídeo: copy e roteiro

Documento cena a cena:

```
# Criativo: [NOME-DO-CRIATIVO]

**Formato:** Vídeo 15s Reels
**Ângulo:** [ângulo]
**Público:** Cold / Warm / Remarketing

## Roteiro

[00-03s] HOOK — frase de abertura + overlay
[03-10s] PROBLEMA — agravamento da dor
[10-13s] SOLUÇÃO — apresentação do produto
[13-15s] CTA — ação clara

## Instruções para Editor
- Corte rápido, sem transição lenta
- Música: lo-fi corporativo, baixo volume
- Legendas em branco, fonte bold
- Overlay numérico em amarelo
```

---

## Referências
- Stack Ad Creator Pixel: `empresa/skills/stack-ad-creator-pixel/`
- Brand guide do Stack: `empresa/skills/stack-ad-creator-pixel/references/brand.md`
- Formatos disponíveis: `areas/marketing/sub-areas/trafego-pago/formatos/`
- Ângulos aprovados: `areas/marketing/sub-areas/trafego-pago/angulos/`
- Learnings: `areas/marketing/sub-areas/trafego-pago/learnings/resumo.md`
