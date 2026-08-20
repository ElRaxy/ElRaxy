#!/usr/bin/env python3
"""Genera instrument-dark.svg e instrument-light.svg: el panel que abre el perfil.

Mide el taller, no la empresa. Cada numero se puede rastrear: los agregados salen
de data/facts.json con la fecha en que se contaron (los pone
scripts/collect_workshop_facts.py), y los commits del ano salen del propio grafo
de contribuciones. Lo que no se puede medir ni citar, no se pinta: un instrumento
con telemetria inventada es un adorno con pretensiones.

    python scripts/make_instrument_svg.py
"""
from __future__ import annotations

import datetime
import json
import math
from pathlib import Path
from xml.etree import ElementTree as ET
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
FACTS = ROOT / "data" / "facts.json"

W, H = 860, 340
CX, CY, R = 430, 176, 92
READ_W = 168
FONT = "'JetBrains Mono','SFMono-Regular',ui-monospace,Menlo,Consolas,monospace"

THEMES = {
    "dark":  dict(bg="#0D1117", grid="#21262D", edge="#30363D", dim="#6E7681",
                  ink="#D1D7E0", accent="#58A6FF", ok="#3FB950", alt="#8957E5"),
    "light": dict(bg="#FFFFFF", grid="#E4E8EC", edge="#D1D9E0", dim="#8C959F",
                  ink="#1F2328", accent="#0969DA", ok="#1A7F37", alt="#8250DF"),
}


def reading(x0: int, y: int, label: str, value: str, c: dict, delay: float) -> str:
    """Etiqueta a la izquierda, valor a la derecha, regla debajo.

    Los dos extremos anclados a un ancho fijo: anclarlos al mismo punto con un
    offset hace que un valor largo se coma la etiqueta.
    """
    x1 = x0 + READ_W
    return (
        f'<g opacity="0"><animate attributeName="opacity" from="0" to="1" begin="{delay}s" dur="0.5s" fill="freeze"/>'
        f'<text x="{x0}" y="{y}" fill="{c["dim"]}" font-size="9.5" letter-spacing="1.8">{escape(label)}</text>'
        f'<text x="{x1}" y="{y}" fill="{c["ink"]}" font-size="15" font-weight="700" text-anchor="end">{escape(value)}</text>'
        f'<line x1="{x0}" y1="{y + 8}" x2="{x1}" y2="{y + 8}" stroke="{c["edge"]}" stroke-width="1"/></g>'
    )


def build(theme: str, facts: dict) -> str:
    c = THEMES[theme]
    w = facts["workshop"]
    ident = facts["identity"]
    today = datetime.date.today()
    stamp = f"{today.year}.{today.timetuple().tm_yday:03d}"

    m, arm = 26, 22
    brackets = "".join(
        f'<path d="{d}" stroke="{c["edge"]}" stroke-width="1.2" fill="none"/>'
        for d in (
            f"M{m},{m + arm} L{m},{m} L{m + arm},{m}",
            f"M{W - m - arm},{m} L{W - m},{m} L{W - m},{m + arm}",
            f"M{m},{H - m - arm} L{m},{H - m} L{m + arm},{H - m}",
            f"M{W - m - arm},{H - m} L{W - m},{H - m} L{W - m},{H - m - arm}",
        )
    )
    ticks = "".join(
        f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{c["grid"]}" stroke-width="1"/>'
        for x1, y1, x2, y2 in (
            (W // 2 - 6, m, W // 2 + 6, m), (W // 2 - 6, H - m, W // 2 + 6, H - m),
            (m, CY, m + 12, CY), (W - m - 12, CY, W - m, CY),
        )
    )

    circ = 2 * math.pi * R
    ring = (
        f'<circle cx="{CX}" cy="{CY}" r="{R}" fill="none" stroke="{c["accent"]}" stroke-width="1.1" opacity="0.55" '
        f'stroke-dasharray="{circ:.1f}" stroke-dashoffset="{circ:.1f}" transform="rotate(-90 {CX} {CY})">'
        f'<animate attributeName="stroke-dashoffset" from="{circ:.1f}" to="0" begin="0.15s" dur="1.15s" fill="freeze"/></circle>'
        + "".join(
            f'<ellipse cx="{CX}" cy="{CY}" rx="{rx}" ry="{ry}" fill="none" stroke="{c["grid"]}" stroke-width="1" '
            f'transform="rotate(-18 {CX} {CY})" opacity="0">'
            f'<animate attributeName="opacity" from="0" to="1" begin="{b}s" dur="0.7s" fill="freeze"/></ellipse>'
            for rx, ry, b in ((R + 34, R - 34, 0.9), (R - 34, R + 34, 1.0))
        )
    )

    # un nodo por agente del harness
    nodes = ""
    n = max(1, w["agents"])
    for i in range(n):
        a = -math.pi / 2 + i * 2 * math.pi / n
        nx, ny = CX + R * math.cos(a), CY + R * math.sin(a)
        col = (c["ok"], c["accent"], c["alt"])[i % 3]
        t = 1.2 + i * 0.05
        nodes += (
            f'<circle cx="{nx:.1f}" cy="{ny:.1f}" r="0" fill="{col}">'
            f'<animate attributeName="r" from="0" to="4.5" begin="{t:.2f}s" dur="0.3s" fill="freeze"/></circle>'
            f'<circle cx="{nx:.1f}" cy="{ny:.1f}" r="9" fill="none" stroke="{col}" stroke-width="0.8" opacity="0">'
            f'<animate attributeName="opacity" from="0" to="0.26" begin="{t:.2f}s" dur="0.4s" fill="freeze"/></circle>'
        )

    core = (
        f'<g opacity="0"><animate attributeName="opacity" from="0" to="1" begin="1.9s" dur="0.6s" fill="freeze"/>'
        f'<text x="{CX}" y="{CY - 34}" fill="{c["dim"]}" font-size="9.5" letter-spacing="2.4" text-anchor="middle">{w["agents"]} AGENTS</text>'
        f'<text x="{CX}" y="{CY + 2}" fill="{c["ink"]}" font-size="34" font-weight="700" text-anchor="middle">{w["commits"]:,}</text>'
        f'<text x="{CX}" y="{CY + 22}" fill="{c["dim"]}" font-size="9.5" letter-spacing="2.4" text-anchor="middle">COMMITS</text></g>'
    )

    lx, rx = m + 26, W - m - 26 - READ_W
    left = (reading(lx, 138, "COMMANDS", f'{w["commands"]}', c, 2.0)
            + reading(lx, 202, "RULES", f'{w["rules"]}', c, 2.1))
    right = (reading(rx, 138, "ADRS", f'{w["adrs"]}', c, 2.2)
             + reading(rx, 202, "RUNBOOKS", f'{w["runbooks"]}', c, 2.3))

    head = (
        f'<g opacity="0"><animate attributeName="opacity" from="0" to="1" begin="0.05s" dur="0.5s" fill="freeze"/>'
        f'<text x="{lx}" y="{m + 34}" fill="{c["ink"]}" font-size="13" letter-spacing="3.2" font-weight="700">{escape(ident["code"])}</text>'
        f'<text x="{lx}" y="{m + 50}" fill="{c["dim"]}" font-size="9" letter-spacing="2.6">{escape(ident["system"])}</text>'
        f'<text x="{W - m - 26}" y="{m + 34}" fill="{c["dim"]}" font-size="11" letter-spacing="1.8" text-anchor="end">{stamp}</text>'
        f'<text x="{W - m - 26}" y="{m + 50}" fill="{c["dim"]}" font-size="9" letter-spacing="2.2" text-anchor="end">{w["dailies"]} SESSIONS LOGGED</text></g>'
    )
    foot = (
        f'<g opacity="0"><animate attributeName="opacity" from="0" to="1" begin="2.45s" dur="0.6s" fill="freeze"/>'
        f'<text x="{lx}" y="{H - m - 26}" fill="{c["dim"]}" font-size="9" letter-spacing="1.8">SINCE {w["since"]}</text>'
        f'<text x="{lx}" y="{H - m - 12}" fill="{c["dim"]}" font-size="9" letter-spacing="1.8">{escape(ident["name"])}</text>'
        f'<text x="{W - m - 26}" y="{H - m - 26}" fill="{c["dim"]}" font-size="9" letter-spacing="1.8" text-anchor="end">GH/ELRAXY</text>'
        f'<text x="{W - m - 26}" y="{H - m - 12}" fill="{c["dim"]}" font-size="9" letter-spacing="1.8" text-anchor="end">COUNTED {w["counted_at"]}</text></g>'
    )

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}"
     role="img" font-family="{FONT}">
  <title>{escape(ident["name"])} — {escape(ident["system"])}</title>
  <desc>{w["skills"]} skills, {w["agents"]} agents, {w["commands"]} commands, {w["adrs"]} ADRs, {w["runbooks"]} runbooks.</desc>
  <rect width="{W}" height="{H}" rx="10" fill="{c["bg"]}"/>
  {brackets}{ticks}
  {ring}{nodes}{core}
  {left}{right}
  {head}{foot}
</svg>
"""


def main() -> None:
    facts = json.loads(FACTS.read_text(encoding="utf-8"))
    if "workshop" not in facts:
        raise SystemExit("faltan los datos del taller: corre scripts/collect_workshop_facts.py")
    for theme in THEMES:
        svg = build(theme, facts)
        ET.fromstring(svg)          # si no parsea, GitHub pinta un icono roto y no avisa
        out = ROOT / f"instrument-{theme}.svg"
        out.write_text(svg, encoding="utf-8")
        print(f"{out.name} · {len(svg.encode()):,} bytes · XML ok")


if __name__ == "__main__":
    main()
