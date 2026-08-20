#!/usr/bin/env python3
"""Convierte assets/source-photo.png en ascii-portrait.svg: un retrato ASCII
monocromo que se imprime fila a fila.

El movimiento vive entero dentro del SVG (SMIL), porque GitHub renderiza los SVG
del README via <img>: no ejecuta JS y bloquea el CSS externo.

La foto ya viene sin fondo, asi que no hace falta rembg. Lo que si hace falta es
CLAHE: una cara con luz plana y ecualizacion global se convierte en un borron sin
rasgos — medido en este mismo retrato antes de meter OpenCV.

Solo se ejecuta a mano, cuando cambia la foto. El cron diario no lo llama, asi que
cv2 y numpy no son dependencias del workflow.

    python scripts/make_ascii_svg.py
"""
from pathlib import Path
from xml.sax.saxutils import escape

import cv2
import numpy as np
from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "assets" / "source-photo.png"
OUTPUT = ROOT / "ascii-portrait.svg"

COLS = 100
CROP_KEEP = 0.66          # recorte vertical: cabeza y hombros (el torso satura a negro)
CLAHE_CLIP, CLAHE_TILE = 4.0, 12
RAMP = " .`:-=+*csS#%@"   # claro (disperso) -> oscuro (denso)
WHITE_CUT = 232           # por encima de esto, espacio: limpia el fondo

CHAR_W, LINE_H, FONT_SIZE = 8, 15, 13
PAD_X, PAD_TOP = 26, 58
ROW_DUR, ROW_STAGGER = 0.34, 0.075

INK = "#C9D1D9"
CURSOR = "#58A6FF"
FONT = "'JetBrains Mono','SFMono-Regular',ui-monospace,Menlo,Consolas,monospace"


def to_rows(path: Path) -> list[str]:
    """Foto -> lista de filas de caracteres."""
    im = Image.open(path).convert("RGBA")
    box = im.split()[-1].getbbox()
    im = im.crop((box[0], box[1], box[2], box[1] + int((box[3] - box[1]) * CROP_KEEP)))

    inner = im.split()[-1].getbbox()          # el sujeto ya sin torso: reencuadra
    im = im.crop(inner)
    alpha = im.split()[-1]
    mask = alpha.point(lambda v: 255 if v > 140 else 0)

    flat = Image.new("RGB", im.size, (255, 255, 255))
    flat.paste(im, mask=alpha)

    clahe = cv2.createCLAHE(clipLimit=CLAHE_CLIP, tileGridSize=(CLAHE_TILE, CLAHE_TILE))
    grey = Image.fromarray(clahe.apply(np.array(flat.convert("L"))))
    grey = grey.filter(ImageFilter.UnsharpMask(radius=3, percent=140, threshold=2))

    canvas = Image.new("L", grey.size, 255)
    canvas.paste(grey, mask=mask)

    rows = max(1, round(canvas.height / canvas.width * COLS * 0.5))
    small = canvas.resize((COLS, rows), Image.LANCZOS)
    px, top = small.load(), len(RAMP) - 1

    out = []
    for y in range(rows):
        line = "".join(
            " " if px[x, y] >= WHITE_CUT else RAMP[top - round(px[x, y] / 255 * top)]
            for x in range(COLS)
        )
        out.append(line.rstrip())
    while out and not out[0].strip():
        out.pop(0)
    while out and not out[-1].strip():
        out.pop()
    left = min((len(r) - len(r.lstrip()) for r in out if r.strip()), default=0)
    return [r[left:].rstrip() for r in out]


def build_svg(rows: list[str]) -> str:
    grid = max((len(r) for r in rows), default=COLS)
    text_w = grid * CHAR_W
    width = text_w + PAD_X * 2
    height = PAD_TOP + len(rows) * LINE_H + 26

    clips, glyphs, cursors = [], [], []
    for i, row in enumerate(rows):
        y = PAD_TOP + i * LINE_H
        begin = round(i * ROW_STAGGER, 3)
        span = max(1, len(row)) * CHAR_W

        clips.append(
            f'<clipPath id="r{i}"><rect x="{PAD_X}" y="{y - FONT_SIZE}" width="0" height="{LINE_H}">'
            f'<animate attributeName="width" from="0" to="{span}" begin="{begin}s" '
            f'dur="{ROW_DUR}s" fill="freeze"/></rect></clipPath>'
        )
        glyphs.append(
            f'<text x="{PAD_X}" y="{y}" clip-path="url(#r{i})" xml:space="preserve" '
            f'textLength="{len(row) * CHAR_W}" lengthAdjust="spacing">{escape(row)}</text>'
        )
        # bloque que cabalga el borde del barrido y se apaga al terminar la fila
        cursors.append(
            f'<rect x="{PAD_X}" y="{y - FONT_SIZE + 2}" width="{CHAR_W}" height="{FONT_SIZE}" '
            f'fill="{CURSOR}" opacity="0">'
            f'<set attributeName="opacity" to="0.85" begin="{begin}s"/>'
            f'<animate attributeName="x" from="{PAD_X}" to="{PAD_X + span}" begin="{begin}s" '
            f'dur="{ROW_DUR}s" fill="freeze"/>'
            f'<set attributeName="opacity" to="0" begin="{round(begin + ROW_DUR, 3)}s"/></rect>'
        )

    nl = "\n    "
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}"
     viewBox="0 0 {width} {height}" role="img" font-family="{FONT}">
  <title>Alex Mico Robles</title>
  <desc>ASCII portrait printed row by row.</desc>
  <defs>
    <linearGradient id="edge" x1="0" y1="0" x2="{width}" y2="0" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="#1F6FEB"/><stop offset="0.55" stop-color="#58A6FF"/><stop offset="1" stop-color="#8957E5"/>
    </linearGradient>
    {nl.join(clips)}
  </defs>

  <rect x="1" y="1" width="{width - 2}" height="{height - 2}" rx="12" fill="#0D1117" stroke="#30363D" stroke-width="1.5"/>
  <rect x="1" y="1" width="{width - 2}" height="4" rx="2" fill="url(#edge)"/>
  <circle cx="30" cy="32" r="5" fill="#FF5F56"/><circle cx="48" cy="32" r="5" fill="#FFBD2E"/><circle cx="66" cy="32" r="5" fill="#27C93F"/>
  <text x="{width - 26}" y="36" fill="#6E7681" font-size="11.5" text-anchor="end">portrait.sh</text>
  <line x1="20" y1="46" x2="{width - 20}" y2="46" stroke="#21262D" stroke-width="1"/>

  <g fill="{INK}" font-size="{FONT_SIZE}">
    {nl.join(glyphs)}
  </g>
  <g>
    {nl.join(cursors)}
  </g>
</svg>
"""


def main() -> None:
    rows = to_rows(SOURCE)
    svg = build_svg(rows)
    OUTPUT.write_text(svg, encoding="utf-8")
    print(f"{OUTPUT.relative_to(ROOT)} · {len(rows)} filas x {COLS} cols · {len(svg.encode()):,} bytes")


if __name__ == "__main__":
    main()
