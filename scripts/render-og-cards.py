#!/usr/bin/env python3
"""Render social cards from the manifest Hugo writes to public/og-cards.json.

The manifest lists local content paths, so this script deletes it after the
cards are written. Run it after `hugo`, before the site is uploaded.
"""

import html
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FONT = Path(__file__).resolve().parent / "og" / "InterVariable.ttf"

CSS = """
@font-face {
  font-family: "Inter";
  src: url("FONT_URL") format("truetype");
  font-weight: 100 900;
  font-style: normal;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
html, body {
  width: 1200px;
  height: 630px;
  overflow: hidden;
  background: #fff;
}
.card {
  width: 1200px;
  height: 630px;
  display: flex;
  align-items: center;
  gap: 28px;
  padding: 44px 40px 44px 64px;
  background: #fff;
  font-family: Inter, sans-serif;
  -webkit-font-smoothing: antialiased;
  text-rendering: geometricPrecision;
}
.copy {
  flex: 0 0 488px;
  width: 488px;
}
.title {
  color: #141414;
  font-weight: 650;
  font-size: 50px;
  line-height: 1.08;
  letter-spacing: -0.032em;
  font-variation-settings: "opsz" 32, "wght" 650;
  text-wrap: balance;
  hyphens: none;
  overflow-wrap: normal;
}
.meta {
  margin-top: 18px;
  color: #6b7280;
  font-weight: 450;
  font-size: 24px;
  line-height: 1;
  letter-spacing: -0.012em;
  font-variation-settings: "opsz" 16, "wght" 450;
}
.meta .sep {
  display: inline-block;
  margin: 0 0.45em;
  color: #b0b5bd;
}
.figure {
  flex: 1 1 auto;
  min-width: 0;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: flex-start;
}
.figure img {
  display: block;
  max-width: 100%;
  max-height: 100%;
  width: auto;
  height: auto;
}
.card.solo { padding-left: 80px; }
.card.solo .copy { flex: none; width: 980px; }
.card.solo .title { font-size: 60px; }
"""


def chrome_bin():
    for name in ("chromium", "chromium-browser", "google-chrome", "google-chrome-stable"):
        path = shutil.which(name)
        if path:
            return path
    sys.exit("render-og-cards: install chromium or google-chrome")


def card_html(title, minutes, image_uri):
    safe_title = html.escape(title.replace("-", "\u2011"))
    meta = f'ewoodbury.com<span class="sep">·</span>{minutes} min read'
    if image_uri:
        figure = f'<div class="figure"><img src="{html.escape(image_uri, quote=True)}" alt=""></div>'
        kind = ""
    else:
        figure = ""
        kind = " solo"
    css = CSS.replace("FONT_URL", FONT.as_uri())
    return f"""<!doctype html>
<html>
<head><meta charset="utf-8"><style>{css}</style></head>
<body>
  <div class="card{kind}">
    <div class="copy">
      <div class="title">{safe_title}</div>
      <div class="meta">{meta}</div>
    </div>
    {figure}
  </div>
</body>
</html>
"""


def magick_bin():
    for name in ("magick", "convert"):
        path = shutil.which(name)
        if path:
            return path
    sys.exit("render-og-cards: install ImageMagick")


def trim_header(magick, src, dest):
    subprocess.run(
        [magick, str(src), "-fuzz", "2%", "-trim", "+repage", str(dest)],
        check=True,
        stdout=subprocess.DEVNULL,
    )
    if dest.stat().st_size == 0:
        shutil.copyfile(src, dest)


def render(chrome, magick, html_path, dest):
    shot = html_path.with_name("shot.png")
    proc = subprocess.run(
        [
            chrome,
            "--headless",
            "--disable-gpu",
            "--no-sandbox",
            "--hide-scrollbars",
            "--force-device-scale-factor=2",
            "--window-size=1200,630",
            "--default-background-color=FFFFFF",
            f"--screenshot={shot}",
            html_path.as_uri(),
        ],
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0 or not shot.exists():
        sys.stderr.write(proc.stderr)
        sys.exit(f"render-og-cards: chromium failed for {dest.name}")
    dest.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [magick, str(shot), "-filter", "Lanczos", "-resize", "1200x630", str(dest)],
        check=True,
        stdout=subprocess.DEVNULL,
    )


def main():
    public = Path(sys.argv[1] if len(sys.argv) > 1 else ROOT / "public").resolve()
    manifest_path = public / "og-cards.json"
    cards = json.loads(manifest_path.read_text())
    chrome = chrome_bin()
    magick = magick_bin()

    with tempfile.TemporaryDirectory(prefix="og-cards-") as tmp:
        work = Path(tmp)
        for card in cards:
            header = card.get("header") or ""
            image_uri = ""
            if header:
                src = ROOT / header
                if not src.is_file():
                    sys.exit(f"render-og-cards: missing header {src}")
                trimmed = work / "header.png"
                trim_header(magick, src, trimmed)
                image_uri = trimmed.as_uri()
            html_path = work / "card.html"
            html_path.write_text(card_html(card["title"], card["minutes"], image_uri), encoding="utf-8")
            dest = public / card["out"]
            render(chrome, magick, html_path, dest)
            print(dest.relative_to(public))

    manifest_path.unlink()


if __name__ == "__main__":
    main()
