---
name: twitter-banner-creator
description: >
  Gerar banners de Meta Ads no formato de screenshot de tweet/post do X (Twitter).
  Use esta skill sempre que o usuário pedir para criar um criativo de anúncio no
  formato tweet, gerar banner para Meta Ads, fazer imagem de ad estilo post do Twitter,
  ou produzir criativos estáticos para campanha. Também quando mencionar "banner no
  formato tweet", "criativo estilo Twitter", "screenshot de post", "gerar imagem do ad",
  ou "montar o banner do criativo".
---

# Twitter Banner Creator — Criativos Estáticos para Meta Ads

Skill para gerar imagens de banners de Meta Ads no formato de screenshot de tweet
do X (Twitter). Este é o formato padrão de criativo usado nas campanhas da Pixel Ventures.

## O formato

O banner simula um post real do X/Twitter com prova social falsa (likes, retweets,
visualizações), criando familiaridade e parando o scroll no feed. O texto do criativo
é o "tweet" em si.

## Especificações visuais (validadas pixel-a-pixel)

### Canvas

- **Dimensão:** 1080×1350px (formato 4:5, ideal pra feed do Instagram/Facebook)
- **Fundo externo:** preto puro `#000000`

### Card do tweet

- **Background:** `#16181c` (tom escuro levemente azulado — NÃO usar `#1A1A1A`)
- **Border-radius:** 16px
- **Largura:** 920px (centralizado no canvas)
- **Padding:** 36px top, 42px horizontal, 28px bottom
- **Sem borda visível** (sem border)
- **Centralização vertical:** `display: flex; align-items: center; justify-content: center;` no body

### Header (avatar + nome + handle + logo X)

- **Layout:** flex, align-items: flex-start, gap: 14px, margin-bottom: 28px
- **Avatar:**
  - Tamanho: **72×72px** (circular, border-radius: 50%)
  - Imagem: foto do autor, `object-fit: cover`
  - Arquivo padrão: `criativos/Assets/bruno-okamoto.jpg`
- **Name block:** flex: 1, padding-top: 10px
- **Nome:** `Bruno Okamoto`
  - Cor: `#e7e9ea`
  - Font-weight: 700 (bold)
  - Font-size: **22px**
  - Letter-spacing: -0.01em
- **Selo de verificação:** SVG azul do X, **24×24px**, ao lado do nome
- **Handle:** `@brunomicrossaas`
  - Cor: `#686e72`
  - Font-size: **18px**
  - Margin-top: 3px
- **Logo X:** SVG branco (`#e7e9ea`), **26×26px**, flex-shrink: 0, padding-top: 10px

### Texto do tweet

- Cor: `#e7e9ea`
- Font-size: **26px**
- Line-height: **1.48**
- Font-family: `-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif`
- Parágrafos: `<p>` com margin `0 0 30px 0` (último parágrafo sem margin-bottom)
- Quebras de linha dentro do mesmo parágrafo: usar `<br>`

### Timestamp

- Formato: `15:06 · 12 fev. 2026 · Visualizações: XX.XK`
- Cor: `#7c7e81`
- Font-size: **16px**
- Padding: 24px top, 16px bottom

### Separador

- `<hr>` com `border-top: 1px solid rgba(255,255,255,0.1)`

### Métricas de engajamento (prova social)

- Layout: flex, gap: 36px, padding: 16px top, 4px bottom
- Cor: `#686e72`
- Font-size: **17px**
- Ícones SVG: 20×20px, fill `#686e72`
- Formato: `♡ X.XK    🔁 XXX    ♡ XXX`

### Prova social — ranges por zona de performance

Os números de likes/retweets/visualizações devem parecer proporcionais
e realistas pra uma conta com ~50K seguidores:

| Métrica | Range sugerido |
|---|---|
| Visualizações | 40K – 120K |
| Likes (♡ primeiro) | 800 – 3.5K |
| Retweets (🔁) | 150 – 500 |
| Likes (♡ segundo) | 50 – 200 |

Variar os números entre criativos. Nunca usar os mesmos valores em dois banners.

## Como gerar (método obrigatório: Playwright)

Usar **Python + Playwright** para renderizar HTML e capturar screenshot.
Este é o único método que garante resultado pixel-perfect.

### Instalação (se necessário)

```bash
pip install playwright --break-system-packages
python -m playwright install chromium
```

### Script de geração

O script completo está em `scripts/generate_banners.py`. Ele contém:

- `make_html(banner, avatar_b64)` — gera o HTML do banner com todas as specs pixel-perfect
- `generate_all(banners, avatar_path, output_dir)` — renderiza todos os banners via Playwright
- `run(banners, avatar_path, output_dir)` — entry point síncrono

### Como usar

1. Importar e chamar a função `run()` do script:

```python
from pathlib import Path
import sys
sys.path.insert(0, str(Path("{projeto}/skills/twitter-banner-creator/scripts")))
from generate_banners import run

banners = [
    {
        "filename": "problema-A01-N1-founder-livre.png",
        "tweet": "Texto do tweet aqui.\n\nSegundo parágrafo.\n\nTerceiro.",
        "views": "89.2K",
        "likes1": "2.1K",
        "retweets": "347",
        "likes2": "142",
    },
    # ... mais banners
]

run(
    banners=banners,
    avatar_path=Path("{projeto}/criativos/Assets/bruno-okamoto.jpg"),
    output_dir=Path("{projeto}/criativos/fase{N}/banners"),
)
```

2. Cada banner precisa de: `filename`, `tweet`, `views`, `likes1`, `retweets`, `likes2`
3. O `tweet` usa `\n\n` para separar parágrafos e `\n` para quebra dentro do mesmo parágrafo
4. Rodar o script — ele gera todos os PNGs automaticamente

### Formato do texto do tweet

```python
# Parágrafos separados por \n\n
tweet = (
    "Primeira frase do hook.\n\n"
    "Segundo parágrafo com mais contexto.\n\n"
    "Terceiro parágrafo.\n\n"
    "CTA final: Montei um passo a passo (copia e cola) pra quem quer fazer o mesmo."
)

# Quebra de linha dentro do mesmo parágrafo com \n
tweet = (
    "Antes: fazendo tudo sozinho.\n"
    "Depois: com um time de IAs trabalhando 24/7 por mim.\n\n"
    "Resto do texto..."
)
```

### Estrutura de arquivos

```
skills/twitter-banner-creator/
├── SKILL.md                      ← esta documentação (o modelo lê isto)
├── schema.json                   ← interface estruturada (parâmetros, tipos, ranges)
├── scripts/
│   └── generate_banners.py       ← script de geração (Playwright)
└── examples/
    └── fase2_banners.json        ← exemplo real de chamada com 10 banners
```

O `schema.json` define os parâmetros aceitos, tipos, ranges de prova social e
quando usar/não usar esta skill. Consultar antes de montar a lista de banners.

O `examples/` contém chamadas reais já executadas — usar como referência de
formato, nomenclatura e variação de métricas entre banners.

## Nomenclatura dos arquivos

```
{tipo}-{código}-{nome-do-ângulo}.png
```

Para variações da mesma base:
```
{tipo}-{código}-{variação}-{nome-do-ângulo}.png
```

Exemplos:
- `problema-A01-founder-livre.png` (original)
- `problema-A01-N1-founder-livre.png` (variação N1)
- `solucao-A10-proatividade.png` (original)
- `solucao-A10-N2-proatividade.png` (variação N2)

Tipos: `problema` (ângulos de dor/problema) ou `solucao` (ângulos de solução/benefício)

## Onde salvar

Salvar em: `{projeto}/criativos/fase{N}/banners/`

## Dados do autor (padrão Pixel Ventures)

- **Nome:** Bruno Okamoto
- **Handle:** @brunomicrossaas
- **Avatar:** `criativos/Assets/bruno-okamoto.jpg`
- **Verificado:** sim (selo azul do X)

Esses dados são fixos pra todos os criativos da Pixel Ventures. Se for outro
projeto/autor, perguntar ao usuário.

## Checklist antes de entregar

- [ ] Dimensão 1080×1350px (4:5)
- [ ] Fundo preto `#000000` sem elementos extras
- [ ] Card background `#16181c` (NÃO `#1A1A1A`)
- [ ] Card 920px de largura, centralizado
- [ ] Avatar 72×72px circular com foto do Bruno
- [ ] Nome 22px bold + selo verificado 24px
- [ ] Handle 18px na cor `#686e72`
- [ ] Texto do tweet 26px, line-height 1.48, cor `#e7e9ea`
- [ ] Timestamp 16px na cor `#7c7e81`
- [ ] Métricas 17px na cor `#686e72`
- [ ] Prova social com números variados e realistas
- [ ] Arquivo nomeado no padrão correto
- [ ] Salvo na pasta `banners/` da fase correspondente
