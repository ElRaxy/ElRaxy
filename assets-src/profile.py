"""Generate the original terminal wordmark. Run with Python's standard library."""
from html import escape
from pathlib import Path

WORDMARK = [
    ' █████╗ ██╗     ███████╗██╗  ██╗   ███╗   ███╗██╗ ██████╗ ██████╗ ',
    '██╔══██╗██║     ██╔════╝╚██╗██╔╝   ████╗ ████║██║██╔════╝██╔═══██╗',
    '███████║██║     █████╗   ╚███╔╝    ██╔████╔██║██║██║     ██║   ██║',
    '██╔══██║██║     ██╔══╝   ██╔██╗    ██║╚██╔╝██║██║██║     ██║   ██║',
    '██║  ██║███████╗███████╗██╔╝ ██╗   ██║ ╚═╝ ██║██║╚██████╗╚██████╔╝',
    '╚═╝  ╚═╝╚══════╝╚══════╝╚═╝  ╚═╝   ╚═╝     ╚═╝╚═╝ ╚═════╝ ╚═════╝ ',
]
OUTPUT = Path(__file__).resolve().parents[1] / "assets" / "profile"


def header(color):
    lines = "\n".join(
        f'<tspan x="38" y="{38 + index * 19}">{escape(line)}</tspan>'
        for index, line in enumerate(WORDMARK)
    )
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 846 154" role="img" aria-labelledby="title">
<title id="title">Alex Micó</title>
<text fill="{color}" font-family="Menlo, Consolas, monospace" font-size="19" xml:space="preserve">{lines}</text>
</svg>
'''


if __name__ == "__main__":
    OUTPUT.mkdir(parents=True, exist_ok=True)
    for theme, color in (("light", "#2448ff"), ("dark", "#879aff")):
        (OUTPUT / f"terminal-{theme}.svg").write_text(header(color), encoding="utf-8")
