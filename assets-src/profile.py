"""Generate original profile lettering with Python's standard library.

Run: python3 assets-src/profile.py
SVGs are standalone, with visible static defaults and optional finite motion.
"""

from pathlib import Path

GLYPHS = {
    "A": ["01110", "11011", "11011", "11111", "11011", "11011", "11011"],
    "L": ["11000", "11000", "11000", "11000", "11000", "11000", "11111"],
    "E": ["11111", "11000", "11000", "11110", "11000", "11000", "11111"],
    "X": ["11011", "11011", "01110", "00100", "01110", "11011", "11011"],
    "M": ["10001", "11011", "11111", "10101", "10001", "10001", "10001"],
    "I": ["11111", "00100", "00100", "00100", "00100", "00100", "11111"],
    "C": ["01111", "11000", "11000", "11000", "11000", "11000", "01111"],
    "O": ["01110", "11011", "11011", "11011", "11011", "11011", "01110"],
}
THEMES = {
    "light": {"paper": "#f1f0e8", "ink": "#141613", "blue": "#2448ff", "line": "#c5c7bd"},
    "dark": {"paper": "#141613", "ink": "#f1f0e8", "blue": "#879aff", "line": "#444840"},
}
BADGES = {
    "react": "React", "javascript": "JavaScript", "typescript": "TypeScript",
    "node": "Node.js", "express": "Express", "mongodb": "MongoDB",
    "python": "Python", "bash": "Bash", "vitest": "Vitest",
    "github-actions": "GitHub Actions", "gemini": "Gemini", "vertex-ai": "Vertex AI",
}


def badge(label):
    width = len(label) * 8 + 30
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} 30" role="img" aria-label="{label}">
  <rect x=".5" y=".5" width="{width - 1}" height="29" rx="5" fill="#f1f0e8" stroke="#c5c7bd"/>
  <path d="M8 11v8" stroke="#2448ff" stroke-width="2"/>
  <text x="18" y="20" fill="#141613" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" font-size="13">{label}</text>
</svg>
'''


def word(value, x, y, cell, color, start):
    letters = []
    for index, letter in enumerate(value):
        parts = []
        for row, bits in enumerate(GLYPHS[letter]):
            for col, bit in enumerate(bits):
                if bit == "1":
                    parts.append(f"M{col * cell} {row * cell}h{cell}v{cell}h-{cell}z")
        if letter == "O":
            parts.append(f"M{2 * cell} {-cell / 2}l{cell} {-cell}h{cell}l-{cell} {cell}z")
        path = "".join(parts)
        delay = (start + index) * 65
        letters.append(
            f'<g transform="translate({x + index * 6 * cell} {y})">'
            f'<path class="letter" style="animation-delay:{delay}ms" fill="{color}" d="{path}"/>'
            "</g>"
        )
    return "\n".join(letters)


def banner(theme, mobile):
    color = THEMES[theme]
    width, height = (640, 510) if mobile else (1200, 382)
    edge = 40 if mobile else 48
    if mobile:
        name = word("ALEX", 40, 104, 23, color["ink"], 0)
        name += word("MICO", 40, 305, 21, color["blue"], 4)
        name += f'<rect class="cursor" x="548" y="431" width="42" height="21" fill="{color["blue"]}"/>'
        metadata = (
            '<text x="40" y="51" font-size="23">ELRAXY</text>'
            '<text x="600" y="51" text-anchor="end" font-size="21">FULL STACK</text>'
            '<text x="40" y="489" font-size="20">PRODUCTS &amp; TOOLS</text>'
            '<text x="600" y="489" text-anchor="end" font-size="20">ALICANTE, ES</text>'
        )
        line_y = 470
    else:
        name = word("ALEX", 48, 132, 21, color["ink"], 0)
        name += word("MICO", 624, 132, 21, color["blue"], 4)
        name += f'<rect class="cursor" x="1128" y="258" width="24" height="21" fill="{color["blue"]}"/>'
        metadata = (
            '<text x="48" y="57" font-size="23">ELRAXY</text>'
            '<text x="1152" y="57" text-anchor="end" font-size="23">FULL STACK / PRODUCTS &amp; TOOLS</text>'
            '<text x="48" y="354" font-size="21">INTERFACES, APIS &amp; SMALL USEFUL TOOLS</text>'
            '<text x="1152" y="354" text-anchor="end" font-size="21">ALICANTE, ES</text>'
        )
        line_y = 320
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title description">
  <title id="title">Alex Micó</title>
  <desc id="description">ElRaxy. Full stack developer. Products and tools. Alicante, Spain.</desc>
  <style>
    @media (prefers-reduced-motion: no-preference) {{
      .letter {{ animation: settle 620ms cubic-bezier(.22,1,.36,1) both; }}
      .cursor {{ animation: cursor 1600ms ease-out; }}
    }}
    @keyframes settle {{ from {{ transform: translateY(7px); }} to {{ transform: translateY(0); }} }}
    @keyframes cursor {{ 0%,35% {{ opacity: 1; }} 48%,58% {{ opacity: .3; }} 72%,100% {{ opacity: 1; }} }}
  </style>
  <rect width="{width}" height="{height}" rx="8" fill="{color['paper']}"/>
  <path d="M{edge} 77H{width - edge}M{edge} {line_y}H{width - edge}" fill="none" stroke="{color['line']}"/>
  <g font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" fill="{color['ink']}">
    {metadata}
  </g>
  {name}
</svg>
'''


if __name__ == "__main__":
    output = Path(__file__).resolve().parents[1] / "assets" / "profile"
    output.mkdir(parents=True, exist_ok=True)
    for theme in THEMES:
        for mobile in (False, True):
            suffix = "-mobile" if mobile else ""
            (output / f"name-{theme}{suffix}.svg").write_text(banner(theme, mobile), encoding="utf-8")
    for slug, label in BADGES.items():
        (output / f"tool-{slug}.svg").write_text(badge(label), encoding="utf-8")
