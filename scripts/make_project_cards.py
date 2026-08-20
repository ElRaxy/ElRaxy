#!/usr/bin/env python3
"""Genera las tarjetas de proyecto (assets/card-*.svg).

Mismo lenguaje visual que el resto del perfil: panel oscuro, franja de acento,
prompt de terminal abajo. Las tarjetas son estaticas a proposito — el movimiento
del README ya lo llevan el heatmap y el retrato; una cuadricula de cuatro cosas
animandose a la vez no se lee.

    python scripts/make_project_cards.py
"""
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets"

W, H = 460, 210
FONT = "'JetBrains Mono','SFMono-Regular',ui-monospace,Menlo,Consolas,monospace"

CARDS = [
    dict(file="card-strev.svg", path="~/projects/strev", name="Strev",
         badge=("live", "#3FB950", "#0E2A14"), grad=("#1F6FEB", "#3FB950"),
         lines=["Training SaaS — progressive overload, athlete", "tracking and trainer dashboards."],
         tags=["React 19", "Express 5", "MongoDB", "Zod", "Stripe"],
         cmd=("open", "strev.app")),
    dict(file="card-vanguardia.svg", path="~/projects/vanguardia", name="VanguardIA",
         badge=("private", "#8957E5", "#1C1230"), grad=("#8957E5", "#58A6FF"),
         lines=["My software factory: specs first, subagents that", "write to files, nothing done until verified."],
         tags=["Claude Code", "Python", "Node", "MCP"],
         cmd=("run", "harness --spec")),
    dict(file="card-fleet.svg", path="~/projects/anuubis", name="Fleet Ops",
         badge=("internal", "#58A6FF", "#0C1D33"), grad=("#1F6FEB", "#58A6FF"),
         lines=["8 servers, ~880 WordPress sites: deploys, audits,", "migrations and incident response, scripted."],
         tags=["Python", "WP-CLI", "Plesk", "Playwright"],
         cmd=("deploy", "--fleet --verify")),
    dict(file="card-chorus.svg", path="~/projects/chorus", name="chorus",
         badge=("open source", "#D2A8FF", "#1C1230"), grad=("#8957E5", "#D2A8FF"),
         lines=["Multi-LLM peer review for code decisions.", "Bring your own CLI; 2-4 models review the work."],
         tags=["TypeScript", "CLI"],
         cmd=("gh repo view", "ElRaxy/chorus")),
]


def tag_row(tags: list[str], y: int) -> str:
    out, x = [], 24
    for t in tags:
        w = 10 + len(t) * 7
        out.append(
            f'<rect x="{x}" y="{y}" width="{w}" height="22" rx="6" fill="#161B22" stroke="#30363D"/>'
            f'<text x="{x + w / 2:.0f}" y="{y + 15}" fill="#79C0FF" font-size="11" text-anchor="middle">{escape(t)}</text>'
        )
        x += w + 8
    return "".join(out)


def build(card: dict) -> str:
    label, ink, bg = card["badge"]
    bw = 16 + len(label) * 7
    g0, g1 = card["grad"]
    body = "".join(
        f'<text x="24" y="{92 + i * 21}" fill="#8B949E" font-size="12.5">{escape(l)}</text>'
        for i, l in enumerate(card["lines"])
    )
    verb, arg = card["cmd"]
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}"
     role="img" font-family="{FONT}">
  <title>{escape(card["name"])}</title>
  <defs><linearGradient id="g" x1="0" y1="0" x2="{W}" y2="0" gradientUnits="userSpaceOnUse">
    <stop offset="0" stop-color="{g0}"/><stop offset="1" stop-color="{g1}"/></linearGradient></defs>
  <rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="12" fill="#0D1117" stroke="#30363D" stroke-width="1.5"/>
  <rect x="1" y="1" width="{W - 2}" height="4" rx="2" fill="url(#g)"/>
  <text x="24" y="32" fill="#6E7681" font-size="11.5">{escape(card["path"])}</text>
  <text x="24" y="62" fill="#E6EDF3" font-size="21" font-weight="700">{escape(card["name"])}</text>
  <rect x="{W - 24 - bw}" y="44" width="{bw}" height="22" rx="11" fill="{bg}" stroke="{ink}"/>
  <text x="{W - 24 - bw / 2:.0f}" y="59" fill="{ink}" font-size="11" text-anchor="middle">{escape(label)}</text>
  {body}
  {tag_row(card["tags"], 142)}
  <text x="24" y="188" font-size="12.5"><tspan fill="#58A6FF">$</tspan><tspan fill="#C9D1D9" dx="8">{escape(verb)}</tspan><tspan fill="#D2A8FF" dx="8">{escape(arg)}</tspan></text>
</svg>
"""


def main() -> None:
    for card in CARDS:
        (OUT / card["file"]).write_text(build(card), encoding="utf-8")
        print(f"assets/{card['file']}")


if __name__ == "__main__":
    main()
