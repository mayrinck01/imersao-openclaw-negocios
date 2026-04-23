---
name: stack-ad-creator-pixel
description: Gerar banners estáticos de Meta Ads no formato "stack" da Pixel Educação — fundo escuro #0A0E2A, mascote OpenClaw, hero badge, H1 bold, subtítulo, 3 cards de benefício numerados e price card laranja arredondado. Dois formatos: Post 4:5 (1080×1350) e Story 9:16 (1080×1920). Usar quando Cayo pedir para criar banners de produto, anúncios estáticos Pixel, criativos no formato stack, ou qualquer banner com cards de benefício + preço no estilo Pixel/OpenClaw.
---

# Stack Ad Creator — Pixel Educação

Gera Post (1080×1350) e Story (1080×1920) via Playwright (HTML→screenshot).

## Arquivos

- `scripts/generate.py` — gerador principal
- `references/brand.md` — paleta, tipografia, layout e regras de copy
- `assets/config-example.json` — config de exemplo para copiar/adaptar

## Fluxo

### 1. Criar o config.json

Copiar `assets/config-example.json` para a pasta do projeto e editar:

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

**Regras:**
- `h1`: array de linhas (cada item = 1 linha com `<br>` implícito). Máx 3 linhas no canvas.
- `h1 em`: italic + gradient laranja. Usar para a parte emocional/CTA do headline.
- `subtitle strong`: destaca em branco (`#fff`). Usar em números e termos-chave.
- `cards`: exatamente 3 por copy. `key` deve ser único (vira nome do arquivo).

### 2. Rodar o script

```bash
# Todos os formatos e copies
python3 skills/stack-ad-creator-pixel/scripts/generate.py config.json

# Só post
python3 skills/stack-ad-creator-pixel/scripts/generate.py config.json --formats post

# Copies específicas
python3 skills/stack-ad-creator-pixel/scripts/generate.py config.json --copies a-nome b-nome
```

Output: `banner-{key}-post.png` e `banner-{key}-story.png` no `output_dir`.

### 3. Validar e iterar

Gerar Copy A primeiro para validar layout antes de rodar todas as copies. Ajustar no config e rodar `--copies a-nome` até aprovar. Depois rodar sem filtro.

## Safe Area — Story

O Story tem `margin-bottom: 200px` na price card — safe area para o botão de CTA nativo do Meta Ads (ocupa ~200px do fundo da tela no Stories).

## Dependência

```bash
pip install playwright
playwright install chromium
```

Já instalado no ambiente do Jarvis — não precisa reinstalar.

## Brand

Ver `references/brand.md` para paleta completa, tipografia, tamanhos e regras de copy.
