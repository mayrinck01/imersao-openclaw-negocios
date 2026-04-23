"""
Twitter Banner Creator — Gerador de banners Meta Ads no formato tweet screenshot.

Uso:
    Defina a lista `banners` com os criativos desejados e configure os paths.
    Rode: python generate_banners.py

Dependências:
    pip install playwright --break-system-packages
    python -m playwright install chromium
"""

import asyncio
import base64
import sys
from pathlib import Path
from playwright.async_api import async_playwright


# ── Configuração ──────────────────────────────────────────────────────────────

# Caminho do avatar (relativo ao projeto ou absoluto)
AVATAR_PATH = None  # Definir antes de rodar, ex: Path("criativos/Assets/bruno-okamoto.jpg")

# Pasta de saída
OUTPUT_DIR = None  # Definir antes de rodar, ex: Path("criativos/fase2/banners")

# Lista de banners a gerar
# Cada dict precisa de: filename, tweet, views, likes1, retweets, likes2
BANNERS = []


# ── Template HTML ─────────────────────────────────────────────────────────────

def make_html(banner: dict, avatar_b64: str) -> str:
    """Gera o HTML do banner no estilo tweet screenshot.

    Especificações visuais (validadas pixel-a-pixel contra referência):
    - Canvas: 1080×1350px, fundo #000000
    - Card: 920px, background #16181c, border-radius 16px
    - Avatar: 72×72px circular
    - Nome: 22px bold, cor #e7e9ea
    - Handle: 18px, cor #686e72
    - Texto tweet: 26px, line-height 1.48, cor #e7e9ea
    - Timestamp: 16px, cor #7c7e81
    - Métricas: 17px, cor #686e72
    """
    # Converte texto do tweet em HTML (parágrafos e quebras de linha)
    paragraphs = banner["tweet"].split("\n\n")
    tweet_html = ""
    for p in paragraphs:
        lines = p.split("\n")
        content = "<br>".join(lines)
        tweet_html += f'<p style="margin: 0 0 30px 0;">{content}</p>'

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{
    width: 1080px;
    height: 1350px;
    background: #000000;
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    -webkit-font-smoothing: antialiased;
  }}
  .card {{
    background: #16181c;
    border-radius: 16px;
    padding: 36px 42px 28px 42px;
    width: 920px;
  }}
  .header {{
    display: flex;
    align-items: flex-start;
    margin-bottom: 28px;
    gap: 14px;
  }}
  .avatar {{
    width: 72px;
    height: 72px;
    border-radius: 50%;
    object-fit: cover;
    flex-shrink: 0;
  }}
  .name-block {{
    flex: 1;
    padding-top: 10px;
  }}
  .name-row {{
    display: flex;
    align-items: center;
    gap: 5px;
  }}
  .display-name {{
    color: #e7e9ea;
    font-weight: 700;
    font-size: 22px;
    letter-spacing: -0.01em;
  }}
  .verified svg {{
    width: 24px;
    height: 24px;
    vertical-align: middle;
  }}
  .handle {{
    color: #686e72;
    font-size: 18px;
    margin-top: 3px;
  }}
  .x-logo {{
    flex-shrink: 0;
    padding-top: 10px;
  }}
  .x-logo svg {{
    width: 26px;
    height: 26px;
  }}
  .tweet-text {{
    color: #e7e9ea;
    font-size: 26px;
    line-height: 1.48;
    padding: 0;
  }}
  .tweet-text p:last-child {{
    margin-bottom: 0 !important;
  }}
  .timestamp {{
    color: #7c7e81;
    font-size: 16px;
    padding: 24px 0 16px 0;
  }}
  .separator {{
    border: none;
    border-top: 1px solid rgba(255,255,255,0.1);
    margin: 0;
  }}
  .metrics {{
    display: flex;
    align-items: center;
    gap: 36px;
    padding: 16px 0 4px 0;
    color: #686e72;
    font-size: 17px;
  }}
  .metric {{
    display: flex;
    align-items: center;
    gap: 7px;
  }}
  .metric svg {{
    width: 20px;
    height: 20px;
    fill: #686e72;
  }}
</style>
</head>
<body>
  <div class="card">
    <div class="header">
      <img class="avatar" src="data:image/jpeg;base64,{avatar_b64}" />
      <div class="name-block">
        <div class="name-row">
          <span class="display-name">Bruno Okamoto</span>
          <span class="verified">
            <svg viewBox="0 0 22 22" fill="none">
              <path d="M20.396 11c-.018-.646-.215-1.275-.57-1.816-.354-.54-.852-.972-1.438-1.246.223-.607.27-1.264.14-1.897-.131-.634-.437-1.218-.882-1.687-.47-.445-1.053-.75-1.687-.882-.633-.13-1.29-.083-1.897.14-.273-.587-.704-1.086-1.245-1.44S11.647 1.62 11 1.604c-.646.017-1.273.213-1.813.568s-.969.853-1.24 1.44c-.608-.223-1.267-.272-1.902-.14-.635.13-1.22.436-1.69.882-.445.47-.749 1.055-.878 1.69-.13.635-.08 1.293.144 1.896-.587.274-1.087.705-1.443 1.245-.356.54-.555 1.17-.574 1.817.02.647.218 1.276.574 1.817.356.54.856.972 1.443 1.245-.224.604-.274 1.26-.144 1.896.13.636.433 1.221.878 1.69.47.446 1.055.752 1.69.883.635.13 1.294.083 1.902-.141.27.587.7 1.086 1.24 1.44s1.167.551 1.813.568c.647-.016 1.276-.213 1.817-.567s.972-.854 1.245-1.44c.604.224 1.262.272 1.896.141.636-.13 1.22-.436 1.69-.883.445-.468.75-1.053.881-1.689.13-.635.083-1.292-.14-1.896.587-.274 1.084-.705 1.439-1.246.355-.54.551-1.17.569-1.816z" fill="#1D9BF0"/>
              <path d="M9.585 14.929l-3.28-3.28 1.168-1.168 2.112 2.112 5.36-5.36 1.168 1.168-6.528 6.528z" fill="white"/>
            </svg>
          </span>
        </div>
        <div class="handle">@brunomicrossaas</div>
      </div>
      <div class="x-logo">
        <svg viewBox="0 0 24 24" fill="#e7e9ea">
          <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/>
        </svg>
      </div>
    </div>
    <div class="tweet-text">
      {tweet_html}
    </div>
    <div class="timestamp">15:06 · 12 fev. 2026 · Visualizações: {banner["views"]}</div>
    <hr class="separator">
    <div class="metrics">
      <div class="metric">
        <svg viewBox="0 0 24 24"><path d="M16.697 5.5c-1.222-.06-2.679.51-3.89 2.16l-.805 1.09-.806-1.09C9.984 6.01 8.526 5.44 7.304 5.5c-1.243.07-2.349.78-2.91 1.91-.552 1.12-.633 2.78.479 4.82 1.074 1.97 3.257 4.27 7.129 6.61 3.87-2.34 6.052-4.64 7.126-6.61 1.111-2.04 1.03-3.7.477-4.82-.56-1.13-1.666-1.84-2.908-1.91zm4.187 7.69c-1.351 2.48-4.001 5.12-8.379 7.67l-.503.3-.504-.3c-4.379-2.55-7.029-5.19-8.382-7.67-1.36-2.5-1.41-4.86-.514-6.67.887-1.79 2.647-2.91 4.601-3.01 1.651-.09 3.368.56 4.798 2.01 1.429-1.45 3.146-2.1 4.796-2.01 1.954.1 3.714 1.22 4.601 3.01.896 1.81.846 4.17-.514 6.67z"/></svg>
        <span>{banner["likes1"]}</span>
      </div>
      <div class="metric">
        <svg viewBox="0 0 24 24"><path d="M4.5 3.88l4.432 4.14-1.364 1.46L5.5 7.55V16c0 1.1.896 2 2 2H13v2H7.5c-2.209 0-4-1.79-4-4V7.55L1.432 9.48.068 8.02 4.5 3.88zM16.5 6H11V4h5.5c2.209 0 4 1.79 4 4v8.45l2.068-1.93 1.364 1.46-4.432 4.14-4.432-4.14 1.364-1.46 2.068 1.93V8c0-1.1-.896-2-2-2z"/></svg>
        <span>{banner["retweets"]}</span>
      </div>
      <div class="metric">
        <svg viewBox="0 0 24 24"><path d="M16.697 5.5c-1.222-.06-2.679.51-3.89 2.16l-.805 1.09-.806-1.09C9.984 6.01 8.526 5.44 7.304 5.5c-1.243.07-2.349.78-2.91 1.91-.552 1.12-.633 2.78.479 4.82 1.074 1.97 3.257 4.27 7.129 6.61 3.87-2.34 6.052-4.64 7.126-6.61 1.111-2.04 1.03-3.7.477-4.82-.56-1.13-1.666-1.84-2.908-1.91zm4.187 7.69c-1.351 2.48-4.001 5.12-8.379 7.67l-.503.3-.504-.3c-4.379-2.55-7.029-5.19-8.382-7.67-1.36-2.5-1.41-4.86-.514-6.67.887-1.79 2.647-2.91 4.601-3.01 1.651-.09 3.368.56 4.798 2.01 1.429-1.45 3.146-2.1 4.796-2.01 1.954.1 3.714 1.22 4.601 3.01.896 1.81.846 4.17-.514 6.67z"/></svg>
        <span>{banner["likes2"]}</span>
      </div>
    </div>
  </div>
</body>
</html>"""


# ── Geração ───────────────────────────────────────────────────────────────────

async def generate_all(banners: list, avatar_path: Path, output_dir: Path):
    """Gera todos os banners da lista usando Playwright."""
    if not avatar_path.exists():
        print(f"ERRO: Avatar não encontrado: {avatar_path}")
        sys.exit(1)

    output_dir.mkdir(parents=True, exist_ok=True)
    avatar_b64 = base64.b64encode(avatar_path.read_bytes()).decode()

    async with async_playwright() as p:
        browser = await p.chromium.launch()

        for i, banner in enumerate(banners):
            print(f"[{i+1}/{len(banners)}] {banner['filename']}...")
            html = make_html(banner, avatar_b64)

            page = await browser.new_page(viewport={"width": 1080, "height": 1350})
            await page.set_content(html, wait_until="networkidle")

            output_path = output_dir / banner["filename"]
            await page.screenshot(path=str(output_path), type="png")
            await page.close()
            print(f"  ✓ {output_path}")

        await browser.close()
        print(f"\nPronto! {len(banners)} banners gerados em {output_dir}")


def run(banners: list, avatar_path: Path, output_dir: Path):
    """Entry point — wrapper síncrono para generate_all."""
    asyncio.run(generate_all(banners, avatar_path, output_dir))


# ── Execução direta ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    if not BANNERS:
        print("Nenhum banner definido. Configure a lista BANNERS no script.")
        sys.exit(1)
    if not AVATAR_PATH:
        print("AVATAR_PATH não configurado.")
        sys.exit(1)
    if not OUTPUT_DIR:
        print("OUTPUT_DIR não configurado.")
        sys.exit(1)

    run(BANNERS, AVATAR_PATH, OUTPUT_DIR)
