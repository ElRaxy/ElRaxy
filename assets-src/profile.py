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


THEMES = {
    "light": dict(bg="#f6f8fa", ink="#17202c", accent="#2448ff", line="#d5dce6", muted="#536273"),
    "dark": dict(bg="#10161f", ink="#edf2fa", accent="#879aff", line="#2b3647", muted="#9eacbe"),
}


def text(x, y, value, size, fill, weight="400", family="Arial, sans-serif"):
    return f'<text x="{x}" y="{y}" fill="{fill}" font-family="{family}" font-size="{size}" font-weight="{weight}">{escape(value)}</text>'


def document(width, height, title, body):
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title"><title id="title">{escape(title)}</title>{body}</svg>\n'


def header(theme, mobile=False):
    c = THEMES[theme]
    w, h = (360, 292) if mobile else (720, 222)
    body = f'<rect x=".5" y=".5" width="{w-1}" height="{h-1}" rx="12" fill="{c["bg"]}" stroke="{c["line"]}"/>'
    body += f'<path d="M24 48H{w-24}" stroke="{c["line"]}"/><path d="M24 48H68" stroke="{c["accent"]}" stroke-width="3"/>'
    body += text(24, 31, "README / ALEX", 14 if mobile else 13, c["ink"], "700", "Menlo, Consolas, monospace")
    body += f'<text x="{w-24}" y="31" text-anchor="end" fill="{c["muted"]}" font-family="Arial, sans-serif" font-size="{14 if mobile else 12}">PERSONAL WORK</text>'
    groups = [(WORDMARK, 16.5, 83, 18)] if not mobile else [([line[:32] for line in WORDMARK], 14.5, 78, 15), ([line[35:] for line in WORDMARK], 14.5, 181, 15)]
    for rows, size, top, step in groups:
        spans = "".join(f'<tspan x="24" y="{top+i*step}">{escape(row)}</tspan>' for i, row in enumerate(rows))
        body += f'<text fill="{c["accent"]}" font-family="Menlo, Consolas, monospace" font-size="{size}" xml:space="preserve">{spans}</text>'
    y = h-18
    body += text(24, y, "FULL STACK / PRODUCTS / TOOLS", 14 if mobile else 13, c["muted"], family="Menlo, Consolas, monospace")
    body += f'<rect x="{w-36}" y="{y-10}" width="12" height="12" rx="1" fill="{c["accent"]}"/>'
    return document(w, h, "Alex Micó — full stack, products and developer tools", body)


def motif(project, c):
    # Editorial illustrations, not project logos or product screenshots.
    a, line, ink = c["accent"], c["line"], c["ink"]
    if project == "strev":
        return f'<g fill="none" stroke="{line}" stroke-width="2"><path d="M8 75H188M8 47H188M8 19H188"/><path d="M14 79C43 79 31 27 62 27S83 79 109 79S129 27 158 27S180 62 192 62" stroke="{a}" stroke-width="4"/></g><circle cx="158" cy="27" r="7" fill="{c["bg"]}" stroke="{a}" stroke-width="3"/>'
    if project == "sereno":
        return f'<g fill="none" stroke-width="2"><path d="M8 18H192M8 48H192M8 78H192" stroke="{line}"/><path d="M12 9L23 18L12 27M12 39L23 48L12 57M12 69L23 78L12 87" stroke="{a}"/><path d="M42 18H128M42 48H94M42 78H148" stroke="{ink}"/><path d="M144 18H181M110 48H169M164 78H184" stroke="{a}" stroke-width="6"/></g>'
    return f'<g fill="none" stroke-width="2"><path d="M9 48H62M139 48H192M100 10V27M100 69V89" stroke="{line}"/><rect x="62" y="10" width="77" height="77" rx="5" stroke="{a}"/><path d="M47 32L31 48L47 64M155 32L171 48L155 64" stroke="{ink}"/><path d="M83 49L96 62L120 36" stroke="{a}" stroke-width="4"/></g>'


def project_banner(project, name, number, label, theme, mobile=False):
    c = THEMES[theme]
    w, h = (360, 126) if mobile else (720, 126)
    body = f'<rect x=".5" y=".5" width="{w-1}" height="{h-1}" rx="10" fill="{c["bg"]}" stroke="{c["line"]}"/>'
    body += text(22, 28, number + " / " + label, 14 if mobile else 12, c["muted"], family="Menlo, Consolas, monospace")
    body += text(22, 77, name, 27 if mobile else 34, c["ink"], "700")
    body += f'<path d="M22 100H58" stroke="{c["accent"]}" stroke-width="3"/>'
    if mobile:
        body += f'<g transform="translate(266 38) scale(.38)">{motif(project,c)}</g>'
    else:
        body += f'<g transform="translate(486 17)">{motif(project,c)}</g>'
    return document(w, h, name + " — " + label.lower(), body)


if __name__ == "__main__":
    OUTPUT.mkdir(parents=True, exist_ok=True)
    projects = [("strev", "Strev", "01", "WEB PRODUCT"), ("sereno", "Sereno", "02", "DEVELOPER TOOL"), ("roguepatch", "RoguePatch Lab", "03", "SECURITY LAB")]
    for theme in THEMES:
        for mobile in (False, True):
            suffix = "-mobile" if mobile else ""
            (OUTPUT / f"terminal-{theme}{suffix}.svg").write_text(header(theme, mobile), encoding="utf-8")
            for slug, name, number, label in projects:
                (OUTPUT / f"project-{slug}-{theme}{suffix}.svg").write_text(project_banner(slug, name, number, label, theme, mobile), encoding="utf-8")
