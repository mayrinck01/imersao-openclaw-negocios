#!/usr/bin/env python3
"""
Stack Ad Creator — Pixel Educação
Gera Post (1080×1350) e Story (1080×1920) para o formato "stack" de produto.

Uso:
  python3 generate.py config.json
  python3 generate.py config.json --formats post        # só post
  python3 generate.py config.json --formats post story  # ambos (padrão)
  python3 generate.py config.json --copies a b c        # copies específicas
"""
import json
import sys
import os
import argparse
from playwright.sync_api import sync_playwright

MASCOT_SVG = """<svg class="mascot" viewBox="0 0 120 120" fill="none" xmlns="http://www.w3.org/2000/svg">
  <defs><linearGradient id="lg" x1="0%" y1="0%" x2="100%" y2="100%">
    <stop offset="0%" stop-color="#ff4d4d"/><stop offset="100%" stop-color="#991b1b"/>
  </linearGradient></defs>
  <path d="M60 10 C30 10 15 35 15 55 C15 75 30 95 45 100 L45 110 L55 110 L55 100 C55 100 60 102 65 100 L65 110 L75 110 L75 100 C90 95 105 75 105 55 C105 35 90 10 60 10Z" fill="url(#lg)"/>
  <path d="M20 45 C5 40 0 50 5 60 C10 70 20 65 25 55 C28 48 25 45 20 45Z" fill="url(#lg)"/>
  <path d="M100 45 C115 40 120 50 115 60 C110 70 100 65 95 55 C92 48 95 45 100 45Z" fill="url(#lg)"/>
  <path d="M45 15 Q35 5 30 8" stroke="#ff4d4d" stroke-width="3" stroke-linecap="round"/>
  <path d="M75 15 Q85 5 90 8" stroke="#ff4d4d" stroke-width="3" stroke-linecap="round"/>
  <circle cx="45" cy="35" r="6" fill="#050810"/><circle cx="75" cy="35" r="6" fill="#050810"/>
  <circle cx="46" cy="34" r="2.5" fill="#00e5cc"/><circle cx="76" cy="34" r="2.5" fill="#00e5cc"/>
</svg>"""

FONT_LINK = '<link href="https://fonts.googleapis.com/css2?family=DM+Sans:ital,wght@0,700;0,800;0,900;1,800;1,900&family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">'


def build_cards_html(cards, card_style="numbered"):
    html = ""
    for i, card in enumerate(cards, 1):
        title = card[0]
        desc = card[1] if len(card) > 1 and card[1] else ""
        if card_style == "checkbox":
            icon = '<div class="card-check">✓</div>'
        else:
            icon = f'<div class="card-num">0{i}</div>'
        desc_html = f'<div class="card-desc">{desc}</div>' if desc else ""
        html += f"""
      <div class="card">
        {icon}
        <div class="card-body">
          <div class="card-title">{title}</div>
          {desc_html}
        </div>
      </div>"""
    return html


def build_html(cfg, copy, fmt):
    is_story = fmt == "story"
    w, h = (1080, 1920) if is_story else (1080, 1350)
    pricing = cfg["pricing"]

    # ── Tipografia e tamanhos
    mascot_sz     = "120px"  if is_story else "72px"
    mascot_mb     = "26px"   if is_story else "20px"
    badge_fs      = "29px"   if is_story else "24px"
    badge_py      = "14px"   if is_story else "12px"
    badge_px      = "34px"   if is_story else "28px"
    badge_mb      = "40px"   if is_story else "32px"
    h1_fs         = "80px"   if is_story else "70px"
    h1_mb         = "18px"   if is_story else "14px"
    sub_fs        = "41px"   if is_story else "35px"
    sub_lh        = "1.5"
    sub_mb        = "56px"   if is_story else "48px"
    card_pad_v    = "42px"   if is_story else "30px"
    card_pad_h    = "42px"   if is_story else "36px"
    card_title_fs = "34px"   if is_story else "28px"
    card_desc_fs  = "29px"   if is_story else "23px"
    card_num_fs   = "48px"   if is_story else "38px"
    card_check_sz = "41px"   if is_story else "34px"
    stack_gap     = "18px"   if is_story else "14px"
    card_style    = cfg.get("card_style", "numbered")

    # ── Price card
    pb_py_top     = "52px"   if is_story else "40px"
    pb_py_bot     = "52px"   if is_story else "48px"
    pb_px         = "80px"
    pb_radius     = "24px"
    pb_margin     = "0 60px 200px" if is_story else "0 0 48px"   # story: 200px safe area p/ botão CTA Meta
    pricebar_w    = "calc(100% - 120px)" if is_story else "100%"
    price_was_fs  = "36px"   if is_story else "32px"
    price_cond_fs = "24px"   if is_story else "20px"
    price_lbl_fs  = "26px"   if is_story else "24px"
    price_val_fs  = "112px"  if is_story else "88px"

    # ── Layout
    if is_story:
        body_padding  = "0"
        body_justify  = "space-between"
        content_style = "flex: 1; padding: 100px 80px 60px; justify-content: center;"
    else:
        body_padding  = "0 80px"
        body_justify  = "center"
        content_style = "padding: 80px 0 40px;"

    # ── H1: copy-level override tem prioridade sobre o global
    h1_raw = copy.get("h1", cfg.get("h1", ""))
    if isinstance(h1_raw, list):
        h1_html = "<br>".join(h1_raw)
    else:
        h1_html = h1_raw

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<link rel="preconnect" href="https://fonts.googleapis.com">
{FONT_LINK}
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}

  body {{
    width: {w}px; height: {h}px;
    font-family: 'Inter', -apple-system, sans-serif;
    background: #0A0E2A;
    display: flex; flex-direction: column; align-items: center;
    justify-content: {body_justify};
    padding: {body_padding};
    overflow: hidden; position: relative;
  }}
  body::before {{
    content: ''; position: absolute; top: 0; left: 50%;
    transform: translateX(-50%);
    width: 900px; height: 600px;
    background: radial-gradient(ellipse at 50% 20%, rgba(254,80,0,0.11) 0%, transparent 65%);
    pointer-events: none; z-index: 0;
  }}

  .content {{
    {content_style}
    width: 100%; display: flex; flex-direction: column; align-items: center;
    position: relative; z-index: 1;
  }}
  .mascot {{
    width: {mascot_sz}; height: {mascot_sz}; margin-bottom: {mascot_mb};
    filter: drop-shadow(0 8px 24px rgba(254,80,0,0.40)); flex-shrink: 0;
  }}
  .hero-badge {{
    display: inline-flex; align-items: center; gap: 10px;
    padding: {badge_py} {badge_px}; border-radius: 100px;
    background: rgba(254,80,0,0.10); border: 1px solid rgba(254,80,0,0.30);
    font-family: 'Inter', sans-serif; font-size: {badge_fs}; font-weight: 500;
    color: #FFA38D; margin-bottom: {badge_mb}; flex-shrink: 0;
  }}
  .hero-badge .dot {{
    width: 9px; height: 9px; border-radius: 50%; background: #10B981; flex-shrink: 0;
  }}
  h1 {{
    font-family: 'DM Sans', sans-serif; font-size: {h1_fs}; font-weight: 900;
    color: #fff; line-height: 1.03; text-align: center;
    letter-spacing: -2px; margin-bottom: {h1_mb}; flex-shrink: 0;
  }}
  h1 em {{
    font-style: italic;
    background: linear-gradient(135deg, #FE5000, #FFA38D, #FE5000);
    background-size: 300% 100%;
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
  }}
  .subtitle {{
    font-size: {sub_fs}; color: #C8C8E0; text-align: center;
    line-height: {sub_lh}; font-weight: 400; flex-shrink: 0;
    margin-bottom: {sub_mb};
  }}
  .subtitle strong {{ color: #fff; font-weight: 800; }}

  .stack {{
    width: 100%;
    display: flex; flex-direction: column; gap: {stack_gap};
    flex-shrink: 0;
  }}
  .card {{
    background: #111940; border: 1px solid rgba(254,80,0,0.15);
    border-radius: 20px; padding: {card_pad_v} {card_pad_h};
    display: flex; align-items: flex-start; gap: 28px;
    position: relative; overflow: hidden;
  }}
  {'/* no left bar for checkbox variant */' if card_style == "checkbox" else '''
  .card::before {
    content: ""; position: absolute; left: 0; top: 0; bottom: 0; width: 5px;
    background: linear-gradient(180deg, #FE5000, #CC4100); border-radius: 20px 0 0 20px;
  }'''}
  .card-num {{
    font-family: 'DM Sans', sans-serif; font-size: {card_num_fs}; font-weight: 900;
    color: #FE5000; letter-spacing: -1px;
    min-width: 56px; flex-shrink: 0; line-height: 1;
  }}
  .card-check {{
    font-family: 'Inter', sans-serif; font-size: {card_check_sz}; font-weight: 900;
    color: #FE5000; flex-shrink: 0; line-height: 1; margin-top: 4px;
  }}
  .card-body {{ display: flex; flex-direction: column; }}
  .card-title {{
    font-family: 'DM Sans', sans-serif; font-size: {card_title_fs}; font-weight: 800;
    color: #F1F5F9; line-height: 1.2;
  }}
  .card-desc {{
    font-size: {card_desc_fs}; color: #fff; font-weight: 400; line-height: 1.4; margin-top: 5px;
  }}

  /* ── PRICE CARD ── */
  .price-bar {{
    width: {pricebar_w};
    margin: {pb_margin};
    border-radius: {pb_radius};
    background: linear-gradient(90deg, #CC4100 0%, #FE5000 50%, #E84500 100%);
    padding: {pb_py_top} {pb_px} {pb_py_bot};
    display: flex; align-items: center; justify-content: space-between;
    flex-shrink: 0; position: relative; z-index: 1;
  }}
  .price-left {{ display: flex; flex-direction: column; gap: 6px; }}
  .price-was {{
    font-family: 'Inter', sans-serif; font-size: {price_was_fs}; font-weight: 700;
    color: rgba(255,255,255,0.52); text-decoration: line-through; text-decoration-thickness: 2px;
  }}
  .price-condition {{
    font-family: 'Inter', sans-serif; font-size: {price_cond_fs}; font-weight: 700; color: #fff;
    max-width: 420px; line-height: 1.4; word-break: break-word;
  }}
  .price-right {{ display: flex; flex-direction: column; align-items: flex-end; gap: 4px; }}
  .price-label {{
    font-family: 'Inter', sans-serif; font-size: {price_lbl_fs}; font-weight: 700;
    letter-spacing: 2px; text-transform: uppercase; color: rgba(255,255,255,0.85);
    text-align: right; line-height: 1.5;
  }}
  .price-value {{
    font-family: 'DM Sans', sans-serif; font-size: {price_val_fs}; font-weight: 900;
    color: #fff; line-height: 1; letter-spacing: -3px;
  }}
</style>
</head>
<body>
  <div class="content">
    {MASCOT_SVG}
    <div class="hero-badge"><span class="dot"></span> {cfg["product_badge"]}</div>
    <h1>{h1_html}</h1>
    <p class="subtitle">{copy["subtitle"]}</p>
    <div class="stack">{build_cards_html(copy["cards"], card_style)}</div>
  </div>
  <div class="price-bar">
    <div class="price-left">
      <div class="price-was">{pricing["was"]}</div>
      <div class="price-condition">{pricing["condition"]}</div>
    </div>
    <div class="price-right">
      <div class="price-label">{pricing["label"]}</div>
      <div class="price-value">{pricing["value"]}</div>
    </div>
  </div>
</body>
</html>"""


def render(cfg, formats=None, copy_keys=None):
    formats = formats or cfg.get("formats", ["post", "story"])
    out_dir = cfg.get("output_dir", ".")
    os.makedirs(out_dir, exist_ok=True)

    copies = cfg["copies"]
    if copy_keys:
        copies = [c for c in copies if c["key"] in copy_keys]

    sizes = {"post": (1080, 1350), "story": (1080, 1920)}
    generated = []

    with sync_playwright() as p:
        browser = p.chromium.launch()
        for copy in copies:
            for fmt in formats:
                w, h = sizes[fmt]
                html = build_html(cfg, copy, fmt)
                tmp = f"/tmp/stack-ad-{copy['key']}-{fmt}.html"
                with open(tmp, "w") as f:
                    f.write(html)
                page = browser.new_page(viewport={"width": w, "height": h})
                page.goto(f"file://{tmp}")
                page.wait_for_timeout(2500)
                out = os.path.join(out_dir, f"banner-{copy['key']}-{fmt}.png")
                page.screenshot(path=out, full_page=False)
                page.close()
                generated.append(out)
                print(f"✓ {out}")
        browser.close()

    print(f"\n✅ {len(generated)} imagem(ns) gerada(s) em '{out_dir}'")
    return generated


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Stack Ad Creator — Pixel Educação")
    parser.add_argument("config", help="Caminho para o config.json")
    parser.add_argument("--formats", nargs="+", choices=["post", "story"],
                        help="Formatos a gerar (padrão: post story)")
    parser.add_argument("--copies", nargs="+", metavar="KEY",
                        help="Chaves das copies a gerar (padrão: todas)")
    args = parser.parse_args()

    with open(args.config) as f:
        cfg = json.load(f)

    render(cfg, formats=args.formats, copy_keys=args.copies)
