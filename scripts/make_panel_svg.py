#!/usr/bin/env python3
"""Genera panel-dark.svg y panel-light.svg: el diagrama que abre el perfil.

Dibuja como trabajo, no cuanto trabajo. Un contador (commits, skills, ADRs) mide
volumen y el volumen no dice si sabes hacer algo; el recorrido de una feature si.

Las etapas y los gates salen de data/facts.json, que es donde vive el metodo. Los
agregados quedan en el pie, en letra pequena, con la fecha del recuento: son
contexto, no el argumento.

    python scripts/make_panel_svg.py
"""
from __future__ import annotations

import json
from pathlib import Path
from xml.etree import ElementTree as ET
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
FACTS = ROOT / "data" / "facts.json"

W, H = 860, 300
FONT = "'JetBrains Mono','SFMono-Regular',ui-monospace,Menlo,Consolas,monospace"

THEMES = {
    "dark":  dict(bg="#0D1117", box="#161B22", edge="#30363D", dim="#7D8590",
                  ink="#E6EDF3", accent="#58A6FF", ok="#3FB950", alt="#8957E5"),
    "light": dict(bg="#FFFFFF", box="#F6F8FA", edge="#D1D9E0", dim="#59636E",
                  ink="#1F2328", accent="#0969DA", ok="#1A7F37", alt="#8250DF"),
}

# (titulo, linea de detalle, es_gate)
# el detalle se corta a mano: a 10px monospace caben ~15 caracteres por linea
STAGES = [
    ("SPEC",   "acceptance\ncriteria, EARS", False),
    ("PLAN",   "blast radius\ndeclared first", False),
    ("BUILD",  "subagents write\nto files", False),
    ("REVIEW", "3 tries, then\nit escalates", True),
    ("VERIFY", "tests, then a\nreal browser", True),
]
SHIP_W = 78


def stage(i: int, x: int, w: int, title: str, detail: str, gate: bool, c: dict) -> str:
    """Una etapa del recorrido. Las que son gate llevan marca y no se pintan igual."""
    y, h = 96, 96
    delay = 0.35 + i * 0.22
    edge = c["ok"] if gate else c["edge"]
    lines = "".join(
        f'<text x="{x + 16}" y="{y + 52 + n * 15}" fill="{c["dim"]}" font-size="10.5">{escape(l)}</text>'
        for n, l in enumerate(detail.split("\n"))
    )
    # el gate se marca con un punto, no con una palabra: en 130px no cabe un rotulo
    mark = f'<circle cx="{x + w - 14}" cy="{y + 22}" r="4" fill="{c["ok"]}"/>' if gate else ""
    return (
        f'<g opacity="0"><animate attributeName="opacity" from="0" to="1" begin="{delay:.2f}s" dur="0.45s" fill="freeze"/>'
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{c["box"]}" stroke="{edge}" stroke-width="1.2"/>'
        f'<text x="{x + 14}" y="{y + 28}" fill="{c["ink"]}" font-size="14" font-weight="700" letter-spacing="1.4">{escape(title)}</text>'
        f'{mark}{lines}</g>'
    )


def build(theme: str, facts: dict) -> str:
    c = THEMES[theme]
    w = facts["workshop"]
    n = len(STAGES)
    pad, gap = 30, 14
    bw = (W - pad * 2 - SHIP_W - gap * n) // n

    boxes, arrows = "", ""
    for i, (title, detail, gate) in enumerate(STAGES):
        x = pad + i * (bw + gap)
        boxes += stage(i, x, bw, title, detail, gate, c)
        if i:  # flecha en el hueco entre cajas, no encima de la anterior
            a0, a1 = x - gap + 1, x - 2
            arrows += (
                f'<path d="M{a0},144 L{a1},144 M{a1 - 4},140.5 L{a1},144 L{a1 - 4},147.5" '
                f'stroke="{c["dim"]}" stroke-width="1.2" fill="none" opacity="0">'
                f'<animate attributeName="opacity" from="0" to="1" begin="{0.3 + i * 0.22:.2f}s" dur="0.3s" fill="freeze"/></path>'
            )

    # el recorrido termina en algo, no en el borde
    sx = pad + n * (bw + gap)
    boxes += (
        f'<g opacity="0"><animate attributeName="opacity" from="0" to="1" begin="{0.35 + n * 0.22:.2f}s" dur="0.5s" fill="freeze"/>'
        f'<rect x="{sx}" y="96" width="{SHIP_W}" height="96" rx="8" fill="none" stroke="{c["accent"]}" stroke-width="1.2" stroke-dasharray="4 3"/>'
        f'<text x="{sx + SHIP_W // 2}" y="{140}" fill="{c["accent"]}" font-size="13" font-weight="700" text-anchor="middle">SHIP</text>'
        f'<text x="{sx + SHIP_W // 2}" y="{158}" fill="{c["dim"]}" font-size="9.5" text-anchor="middle">or back</text></g>'
    )
    a0, a1 = sx - gap + 1, sx - 2
    arrows += (
        f'<path d="M{a0},144 L{a1},144 M{a1 - 4},140.5 L{a1},144 L{a1 - 4},147.5" '
        f'stroke="{c["dim"]}" stroke-width="1.2" fill="none" opacity="0">'
        f'<animate attributeName="opacity" from="0" to="1" begin="{0.3 + n * 0.22:.2f}s" dur="0.3s" fill="freeze"/></path>'
    )

    rail_y = 232
    rail = (
        f'<line x1="{pad}" y1="{rail_y}" x2="{W - pad}" y2="{rail_y}" stroke="{c["edge"]}" stroke-width="1" '
        f'stroke-dasharray="{W}" stroke-dashoffset="{W}">'
        f'<animate attributeName="stroke-dashoffset" from="{W}" to="0" begin="0.2s" dur="1.4s" fill="freeze"/></line>'
    )

    head = (
        f'<g opacity="0"><animate attributeName="opacity" from="0" to="1" begin="0.05s" dur="0.45s" fill="freeze"/>'
        f'<text x="{pad}" y="46" fill="{c["ink"]}" font-size="17" font-weight="700">How a change gets shipped here</text>'
        f'<text x="{pad}" y="68" fill="{c["dim"]}" font-size="11.5">Nothing moves right without passing the gate on its left.</text>'
        f'<circle cx="{W - pad - 202}" cy="42" r="4" fill="{c["ok"]}"/>'
        f'<text x="{W - pad}" y="46" fill="{c["dim"]}" font-size="11" text-anchor="end">= a gate that can send it back</text></g>'
    )

    tally = (f'{w["skills"]} skills · {w["agents"]} agents · {w["commands"]} commands · '
             f'{w["rules"]} rules · {w["adrs"]} ADRs · {w["runbooks"]} runbooks')
    foot = (
        f'<g opacity="0"><animate attributeName="opacity" from="0" to="1" begin="1.7s" dur="0.6s" fill="freeze"/>'
        f'<text x="{pad}" y="{rail_y + 24}" fill="{c["dim"]}" font-size="10.5">{escape(tally)}</text>'
        f'<text x="{W - pad}" y="{rail_y + 24}" fill="{c["dim"]}" font-size="10.5" text-anchor="end">counted {w["counted_at"]}</text></g>'
    )

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}"
     role="img" font-family="{FONT}">
  <title>How a change gets shipped: spec, plan, build, review, verify</title>
  <desc>{escape(tally)}, counted {w["counted_at"]}.</desc>
  <rect width="{W}" height="{H}" rx="10" fill="{c["bg"]}"/>
  {head}{arrows}{boxes}{rail}{foot}
</svg>
"""


def main() -> None:
    facts = json.loads(FACTS.read_text(encoding="utf-8"))
    if "workshop" not in facts:
        raise SystemExit("faltan los datos del taller: corre scripts/collect_workshop_facts.py")
    for theme in THEMES:
        svg = build(theme, facts)
        ET.fromstring(svg)          # si no parsea, GitHub pinta un icono roto y no avisa
        out = ROOT / f"panel-{theme}.svg"
        out.write_text(svg, encoding="utf-8")
        print(f"{out.name} · {len(svg.encode()):,} bytes · XML ok")


if __name__ == "__main__":
    main()
