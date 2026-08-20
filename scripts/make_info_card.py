#!/usr/bin/env python3
"""Genera info-card.svg: un panel estilo `neofetch` que se imprime linea a linea
al lado del retrato ASCII.

El contenido vive en ROWS. Es la parte que las estadisticas de GitHub no cuentan,
asi que aqui no se repiten metricas: van en el heatmap.

    python scripts/make_info_card.py
"""
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "info-card.svg"

KEY, VAL, DIM, ACCENT, WARM = "#58A6FF", "#C9D1D9", "#8B949E", "#D2A8FF", "#3FB950"

# (etiqueta, [(texto, color), ...]) — etiqueta vacia = linea de continuacion
ROWS: list[tuple[str, list[tuple[str, str]]]] = [
    ("Role",   [("AI & Automation", VAL), (" @ ", DIM), ("Anuubis Solutions", ACCENT)]),
    ("Focus",  [("Production software, shipped end to end — with agents in the loop.", VAL)]),
    ("", []),
    ("Now",    [("Strev", ACCENT), (" — training SaaS, live at ", VAL), ("strev.app", KEY)]),
    ("",       [("VanguardIA", ACCENT), (" — my AI software factory: harness, specs, subagents", VAL)]),
    ("",       [("Anuubis", ACCENT), (" — WordPress fleet: 8 servers, ~880 sites, deploy automated", VAL)]),
    ("", []),
    ("Method", [("Spec first (EARS)", VAL), (" · ", DIM), ("multi-agent harness", VAL),
                (" · ", DIM), ("nothing ships unverified", WARM)]),
    ("Stack",  [("TypeScript · React 19 · Express 5 · Node · MongoDB · Python · Docker", VAL)]),
    ("Agents", [("Claude Code · LLM APIs · MCP · orchestration & evals", VAL)]),
    ("Ops",    [("Plesk · CI/CD · Sentry · WP-CLI at fleet scale · incident runbooks", VAL)]),
    ("", []),
    ("Open",   [("chorus", ACCENT), (" — multi-LLM peer review for code decisions", VAL)]),
    ("Lang",   [("Spanish · English", VAL)]),
    ("", []),
    ("Reach",  [("anubis.es", KEY), (" · ", DIM), ("alexmico2006@gmail.com", KEY)]),
]

WIDTH = 660
PAD_X, PAD_TOP, LINE_H = 26, 74, 23
FONT_SIZE, LABEL_W = 13, 62
STAGGER = 0.11
FONT = "'JetBrains Mono','SFMono-Regular',ui-monospace,Menlo,Consolas,monospace"


def build_svg() -> str:
    body_h = len(ROWS) * LINE_H
    height = PAD_TOP + body_h + 62
    lines, delay = [], 0.25

    for label, parts in ROWS:
        if not label and not parts:            # separador: ocupa alto, no anima
            lines.append("")
            continue
        y = PAD_TOP + len(lines) * LINE_H
        spans = "".join(f'<tspan fill="{c}">{escape(t)}</tspan>' for t, c in parts)
        head = (f'<text x="{PAD_X}" y="{y}" fill="{KEY}" font-weight="700">{escape(label)}</text>'
                if label else "")
        lines.append(
            f'<g opacity="0">'
            f'<animate attributeName="opacity" from="0" to="1" begin="{round(delay, 2)}s" dur="0.32s" fill="freeze"/>'
            f'<animateTransform attributeName="transform" type="translate" from="-10 0" to="0 0" '
            f'begin="{round(delay, 2)}s" dur="0.32s" fill="freeze"/>'
            f'{head}<text x="{PAD_X + LABEL_W}" y="{y}" xml:space="preserve">{spans}</text></g>'
        )
        delay += STAGGER

    body = "\n    ".join(l for l in lines if l)
    end = round(delay + 0.2, 2)
    swatch_y = PAD_TOP + body_h + 6
    swatches = "".join(
        f'<rect x="{PAD_X + i * 20}" y="{swatch_y}" width="14" height="14" rx="3" fill="{c}"/>'
        for i, c in enumerate(["#FF5F56", "#FFBD2E", "#3FB950", "#58A6FF", "#8957E5", "#D2A8FF", "#8B949E"])
    )

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{height}"
     viewBox="0 0 {WIDTH} {height}" role="img" font-family="{FONT}" font-size="{FONT_SIZE}">
  <title>alex@anuubis — profile card</title>
  <desc>Neofetch-style card: role, current work, method and stack.</desc>
  <defs>
    <linearGradient id="edge" x1="0" y1="0" x2="{WIDTH}" y2="0" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="#1F6FEB"/><stop offset="0.55" stop-color="#58A6FF"/><stop offset="1" stop-color="#8957E5"/>
    </linearGradient>
  </defs>

  <rect x="1" y="1" width="{WIDTH - 2}" height="{height - 2}" rx="12" fill="#0D1117" stroke="#30363D" stroke-width="1.5"/>
  <rect x="1" y="1" width="{WIDTH - 2}" height="4" rx="2" fill="url(#edge)"/>
  <circle cx="30" cy="32" r="5" fill="#FF5F56"/><circle cx="48" cy="32" r="5" fill="#FFBD2E"/><circle cx="66" cy="32" r="5" fill="#27C93F"/>
  <text x="{WIDTH - 26}" y="36" fill="#6E7681" font-size="11.5" text-anchor="end">neofetch</text>

  <g opacity="0">
    <animate attributeName="opacity" from="0" to="1" begin="0.05s" dur="0.3s" fill="freeze"/>
    <text x="{PAD_X}" y="{PAD_TOP - 26}" font-size="15" font-weight="700">
      <tspan fill="{ACCENT}">alex</tspan><tspan fill="{DIM}">@</tspan><tspan fill="{KEY}">anuubis</tspan>
    </text>
    <line x1="{PAD_X}" y1="{PAD_TOP - 17}" x2="{WIDTH - PAD_X}" y2="{PAD_TOP - 17}" stroke="#21262D" stroke-width="1"/>
  </g>

  <g>
    {body}
  </g>

  <g opacity="0">
    <animate attributeName="opacity" from="0" to="1" begin="{end}s" dur="0.4s" fill="freeze"/>
    {swatches}
    <rect x="{PAD_X + 7 * 20 + 8}" y="{swatch_y}" width="9" height="14" fill="{KEY}">
      <animate attributeName="opacity" values="1;1;0;0" dur="1.1s" begin="{end}s" repeatCount="indefinite"/>
    </rect>
  </g>
</svg>
"""


def main() -> None:
    svg = build_svg()
    OUTPUT.write_text(svg, encoding="utf-8")
    print(f"{OUTPUT.relative_to(ROOT)} · {len(ROWS)} filas · {len(svg.encode()):,} bytes")


if __name__ == "__main__":
    main()
