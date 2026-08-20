#!/usr/bin/env python3
"""Renderiza un calendario de contribuciones animado y autocontenido."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from xml.etree import ElementTree as ET


REPO_ROOT = Path(__file__).resolve().parents[1]
INPUT_PATH = REPO_ROOT / "data" / "contributions.json"
OUTPUT_PATH = REPO_ROOT / "contrib-heatmap.svg"

SVG_NAMESPACE = "http://www.w3.org/2000/svg"
WIDTH = 860
HEIGHT = 190
CELL_SIZE = 11
GAP = 3
STEP = CELL_SIZE + GAP
WEEKS = 53
WEEKDAYS = 7
GRID_WIDTH = WEEKS * CELL_SIZE + (WEEKS - 1) * GAP
GRID_X = (WIDTH - GRID_WIDTH) / 2
GRID_Y = 47
COLORS = ["#161B22", "#0E4429", "#006D32", "#26A641", "#39D353"]
MONTHS = (
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
)


def svg_element(tag: str, attributes: dict[str, str] | None = None) -> ET.Element:
    """Crea un elemento dentro del espacio de nombres SVG."""
    return ET.Element(f"{{{SVG_NAMESPACE}}}{tag}", attributes or {})


def add_text(
    parent: ET.Element,
    content: str,
    x: float,
    y: float,
    **attributes: str,
) -> ET.Element:
    """Añade un nodo de texto con coordenadas consistentes."""
    text = ET.SubElement(
        parent,
        f"{{{SVG_NAMESPACE}}}text",
        {"x": f"{x:g}", "y": f"{y:g}", **attributes},
    )
    text.text = content
    return text


def load_data() -> dict:
    """Carga el JSON generado por el scraper."""
    return json.loads(INPUT_PATH.read_text(encoding="utf-8"))


def validate_days(days: list[dict]) -> None:
    """Evita producir posiciones o colores fuera del calendario esperado."""
    for day in days:
        week = day.get("week")
        weekday = day.get("weekday")
        level = day.get("level")
        if not isinstance(week, int) or not 0 <= week < WEEKS:
            raise ValueError(f"Semana fuera de rango: {week!r}")
        if not isinstance(weekday, int) or not 0 <= weekday < WEEKDAYS:
            raise ValueError(f"Día de semana fuera de rango: {weekday!r}")
        if not isinstance(level, int) or not 0 <= level < len(COLORS):
            raise ValueError(f"Nivel fuera de rango: {level!r}")
        date.fromisoformat(str(day.get("date")))


def build_styles(diagonal_values: list[int], fade_delay: float) -> str:
    """Agrupa los retardos por diagonal para mantener compacto el CSS."""
    delay_rules = "\n".join(
        f".d{index} {{ animation-delay: {value * 0.012:.3f}s; }}"
        for index, value in enumerate(diagonal_values)
    )
    return f"""
text {{
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
}}
.day {{
  opacity: 0;
  transform: translateY(-6px);
  transform-box: fill-box;
  transform-origin: center;
  animation-name: reveal;
  animation-duration: 0.45s;
  animation-timing-function: ease-out;
  animation-fill-mode: forwards;
}}
{delay_rules}
.finishing {{
  opacity: 0;
  animation-name: fade-in;
  animation-duration: 0.50s;
  animation-timing-function: ease-out;
  animation-delay: {fade_delay:.3f}s;
  animation-fill-mode: forwards;
}}
@keyframes reveal {{
  from {{ opacity: 0; transform: translateY(-6px); }}
  to {{ opacity: 1; transform: translateY(0); }}
}}
@keyframes fade-in {{
  from {{ opacity: 0; }}
  to {{ opacity: 1; }}
}}
""".strip()


def month_positions(days: list[dict]) -> list[tuple[int, str]]:
    """Sitúa cada mes en su primera semana visible."""
    first_weeks: dict[tuple[int, int], int] = {}
    for day in sorted(days, key=lambda item: str(item["date"])):
        parsed_date = date.fromisoformat(str(day["date"]))
        key = (parsed_date.year, parsed_date.month)
        first_weeks.setdefault(key, int(day["week"]))
    return [
        (week, MONTHS[month - 1])
        for (_, month), week in first_weeks.items()
    ]


def build_svg(payload: dict) -> ET.ElementTree:
    """Construye el documento SVG completo en memoria."""
    days = payload["days"]
    stats = payload["stats"]
    validate_days(days)

    diagonal_values = sorted(
        {int(day["week"]) + int(day["weekday"]) for day in days}
    )
    diagonal_classes = {
        value: f"d{index}" for index, value in enumerate(diagonal_values)
    }
    last_reveal = (max(diagonal_values) * 0.012 + 0.45) if diagonal_values else 0

    ET.register_namespace("", SVG_NAMESPACE)
    root = svg_element(
        "svg",
        {
            "width": str(WIDTH),
            "height": str(HEIGHT),
            "viewBox": f"0 0 {WIDTH} {HEIGHT}",
            "role": "img",
            "aria-labelledby": "heatmap-description",
        },
    )

    description = ET.SubElement(
        root,
        f"{{{SVG_NAMESPACE}}}desc",
        {"id": "heatmap-description"},
    )
    description.text = (
        f"GitHub contribution calendar for {payload['username']}: "
        f"{int(stats['total']):,} contributions, "
        f"{int(stats['active_days'])} active days, longest streak "
        f"{int(stats['longest_streak'])} days."
    )

    definitions = ET.SubElement(root, f"{{{SVG_NAMESPACE}}}defs")
    gradient = ET.SubElement(
        definitions,
        f"{{{SVG_NAMESPACE}}}linearGradient",
        {"id": "accent", "x1": "0%", "y1": "0%", "x2": "100%", "y2": "0%"},
    )
    stops = (("0%", "#1F6FEB"), ("50%", "#58A6FF"), ("100%", "#8957E5"))
    for offset, color in stops:
        ET.SubElement(
            gradient,
            f"{{{SVG_NAMESPACE}}}stop",
            {"offset": offset, "stop-color": color},
        )
    clip_path = ET.SubElement(
        definitions,
        f"{{{SVG_NAMESPACE}}}clipPath",
        {"id": "rounded-frame"},
    )
    ET.SubElement(
        clip_path,
        f"{{{SVG_NAMESPACE}}}rect",
        {"x": "0.5", "y": "0.5", "width": "859", "height": "189", "rx": "12"},
    )

    style = ET.SubElement(root, f"{{{SVG_NAMESPACE}}}style")
    style.text = build_styles(diagonal_values, last_reveal)

    ET.SubElement(
        root,
        f"{{{SVG_NAMESPACE}}}rect",
        {
            "x": "0.5",
            "y": "0.5",
            "width": "859",
            "height": "189",
            "rx": "12",
            "fill": "#0D1117",
            "stroke": "#30363D",
        },
    )
    ET.SubElement(
        root,
        f"{{{SVG_NAMESPACE}}}rect",
        {
            "x": "0.5",
            "y": "0.5",
            "width": "859",
            "height": "4",
            "fill": "url(#accent)",
            "clip-path": "url(#rounded-frame)",
        },
    )

    labels = ET.SubElement(
        root,
        f"{{{SVG_NAMESPACE}}}g",
        {"fill": "#8B949E", "font-size": "10"},
    )
    for week, month in month_positions(days):
        add_text(labels, month, GRID_X + week * STEP, 34)
    for weekday, label in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        add_text(
            labels,
            label,
            GRID_X - 8,
            GRID_Y + weekday * STEP + 9,
            **{"text-anchor": "end"},
        )

    calendar = ET.SubElement(root, f"{{{SVG_NAMESPACE}}}g")
    for day in days:
        week = int(day["week"])
        weekday = int(day["weekday"])
        diagonal = week + weekday
        cell = ET.SubElement(
            calendar,
            f"{{{SVG_NAMESPACE}}}rect",
            {
                "class": f"day {diagonal_classes[diagonal]}",
                "x": f"{GRID_X + week * STEP:g}",
                "y": f"{GRID_Y + weekday * STEP:g}",
                "width": str(CELL_SIZE),
                "height": str(CELL_SIZE),
                "rx": "2",
                "fill": COLORS[int(day["level"])],
            },
        )
        count = day.get("count")
        shown_count = "Unknown" if count is None else str(int(count))
        title = ET.SubElement(cell, f"{{{SVG_NAMESPACE}}}title")
        title.text = f"{shown_count} contributions on {day['date']}"

    footer = ET.SubElement(
        root,
        f"{{{SVG_NAMESPACE}}}g",
        {"class": "finishing", "fill": "#8B949E", "font-size": "12"},
    )
    footer_text = (
        f"{int(stats['total']):,} contributions in the last year · "
        f"{int(stats['active_days'])} active days · longest streak "
        f"{int(stats['longest_streak'])}d"
    )
    add_text(footer, footer_text, 24, 174)

    legend = ET.SubElement(
        root,
        f"{{{SVG_NAMESPACE}}}g",
        {"class": "finishing", "fill": "#8B949E", "font-size": "10"},
    )
    legend_x = 696
    add_text(legend, "Less", legend_x, 174)
    squares_x = legend_x + 32
    for level, color in enumerate(COLORS):
        ET.SubElement(
            legend,
            f"{{{SVG_NAMESPACE}}}rect",
            {
                "x": str(squares_x + level * STEP),
                "y": "164",
                "width": str(CELL_SIZE),
                "height": str(CELL_SIZE),
                "rx": "2",
                "fill": color,
            },
        )
    add_text(legend, "More", squares_x + 5 * STEP + 2, 174)

    return ET.ElementTree(root)


def main() -> int:
    payload = load_data()
    tree = build_svg(payload)
    ET.indent(tree, space="  ")
    tree.write(OUTPUT_PATH, encoding="utf-8", xml_declaration=True)
    size = OUTPUT_PATH.stat().st_size
    print(f"{OUTPUT_PATH}: {size} bytes, {len(payload['days'])} celdas pintadas")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
