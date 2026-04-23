# Brand — Pixel Educação / OpenClaw

## Paleta

| Token           | Hex       | Uso                                   |
|-----------------|-----------|---------------------------------------|
| `bg`            | `#0A0E2A` | Background principal                  |
| `card-bg`       | `#111940` | Fundo dos cards do stack              |
| `accent`        | `#FE5000` | Laranja primário (gradientes, bordas) |
| `accent-dark`   | `#CC4100` | Laranja escuro (gradiente price card) |
| `accent-light`  | `#FFA38D` | Laranja claro (badge text)            |
| `text-primary`  | `#FFFFFF` | Títulos, valores                      |
| `text-secondary`| `#C8C8E0` | Subtítulos, body copy                 |
| `text-muted`    | `rgba(255,255,255,0.52)` | Preço riscado         |
| `green-dot`     | `#10B981` | Indicador de ao vivo / ativo          |
| `teal-eye`      | `#00e5cc` | Detalhe dos olhos do mascote          |

Gradiente accent: `linear-gradient(90deg, #CC4100 0%, #FE5000 50%, #E84500 100%)`  
Gradiente H1 em: `linear-gradient(135deg, #FE5000, #FFA38D, #FE5000)`  
Glow de fundo: `radial-gradient(ellipse at 50% 20%, rgba(254,80,0,0.11) 0%, transparent 65%)`

---

## Tipografia

| Fonte     | Pesos usados        | Uso                            |
|-----------|---------------------|--------------------------------|
| DM Sans   | 700, 800, 900       | H1, card-title, price-value    |
| Inter     | 400, 500, 700, 800  | Badge, subtitle, card-desc, price-* |

Google Fonts URL:
```
https://fonts.googleapis.com/css2?family=DM+Sans:ital,wght@0,700;0,800;0,900;1,800;1,900&family=Inter:wght@400;500;600;700;800&display=swap
```

---

## Tamanhos de Canvas

| Formato | Dimensões    | Uso                          |
|---------|-------------|------------------------------|
| Post    | 1080 × 1350 | Feed Instagram/Facebook (4:5)|
| Story   | 1080 × 1920 | Stories Instagram/Facebook   |

---

## Layout Stack

O formato "stack" tem sempre esta estrutura vertical:

```
[ Mascote ]
[ Hero Badge ]        ← produto + green dot
[ H1 ]                ← até 3 linhas; <em> = italic + gradient
[ Subtitle ]          ← <strong> = destaque branco
[ Card 01 ]  ─┐
[ Card 02 ]   ├─ Stack de 3 cards com numeração 01/02/03
[ Card 03 ]  ─┘
[ Price Card ]        ← card arredondado, gradiente accent
```

**Post:** body com `padding: 0 80px`, conteúdo centralizado, price card dentro do padding.  
**Story:** body sem padding lateral; price card com `margin: 0 60px 200px` — os 200px do fundo são a safe area para o botão de CTA nativo do Meta Ads.

---

## Price Card

- Border-radius: `24px`
- Story margins: `0 60px 200px` (safe area embaixo)
- Post margins: `0 0 48px`
- Padding interno: `52px 80px` (story) / `40px 80px 48px` (post)
- Estrutura: `price-left` (was + condition) ↔ `price-right` (label + value)

---

## Mascote

SVG embutido no script. Corpo vermelho com gradiente `#ff4d4d → #991b1b`, olhos teal `#00e5cc`. Não substituir por imagem externa — usar o SVG do script.

---

## Regras de Copy

- **H1:** sempre a mesma linha em todas as copies de uma campanha. Máx 3 linhas no canvas. Parte emocional em `<em>` (italic + gradient).
- **Subtitle:** usa `<strong>` nos números e termos-chave. Fundo: `#C8C8E0`; strong: `#fff`.
- **Cards:** 3 fixos por copy. `card-title` = nome do benefício; `card-desc` = 1 frase de contexto.
- **Copies diferentes** = subtitle diferente + cards podem variar. H1 e preço são fixos por campanha.
