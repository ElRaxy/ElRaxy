#!/usr/bin/env python3
"""Descarga y normaliza el calendario de contribuciones de GitHub."""

from __future__ import annotations

import json
import re
import sys
from datetime import UTC, datetime
from pathlib import Path

import requests
from bs4 import BeautifulSoup


USERNAME = "ElRaxy"
SOURCE_URL = f"https://github.com/users/{USERNAME}/contributions"
REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = REPO_ROOT / "data" / "contributions.json"
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/140.0.0.0 Safari/537.36"
)
CELL_ID_RE = re.compile(r"^contribution-day-component-(\d+)-(\d+)$")
COUNT_RE = re.compile(r"^(No|[\d,]+)\s+contribution")


def fetch_html() -> str:
    """Obtiene el HTML con límites adecuados para una ejecución automatizada."""
    response = requests.get(
        SOURCE_URL,
        headers={"User-Agent": USER_AGENT},
        timeout=20,
    )
    response.raise_for_status()
    return response.text


def parse_days(html: str) -> list[dict[str, int | str | None]]:
    """Convierte las celdas y sus tooltips asociados en registros diarios."""
    soup = BeautifulSoup(html, "html.parser")
    tooltips = {
        tooltip["for"]: tooltip
        for tooltip in soup.find_all("tool-tip", attrs={"for": True})
    }
    days: list[dict[str, int | str | None]] = []

    cells = soup.select(
        "td.ContributionCalendar-day[data-date][data-level][id]"
    )
    for cell in cells:
        cell_id = str(cell["id"])
        id_match = CELL_ID_RE.fullmatch(cell_id)
        if id_match is None:
            continue

        weekday = int(id_match.group(1))
        week = int(id_match.group(2))
        tooltip = tooltips.get(cell_id)
        count: int | None = None

        if tooltip is not None:
            tooltip_text = tooltip.get_text(" ", strip=True)
            count_match = COUNT_RE.match(tooltip_text)
            if count_match is not None:
                raw_count = count_match.group(1)
                count = 0 if raw_count == "No" else int(raw_count.replace(",", ""))

        days.append(
            {
                "date": str(cell["data-date"]),
                "count": count,
                "level": int(str(cell["data-level"])),
                "week": week,
                "weekday": weekday,
            }
        )

    return sorted(days, key=lambda day: str(day["date"]))


def calculate_current_streak(days: list[dict[str, int | str | None]]) -> int:
    """Calcula la racha vigente ignorando huecos y el cero del último día."""
    known_counts = [
        int(day["count"])
        for day in days
        if day["count"] is not None
    ]
    if not known_counts:
        return 0

    # GitHub no penaliza el día en curso cuando todavía figura con cero.
    if known_counts[-1] == 0:
        known_counts.pop()

    streak = 0
    for count in reversed(known_counts):
        if count <= 0:
            break
        streak += 1
    return streak


def calculate_longest_streak(days: list[dict[str, int | str | None]]) -> int:
    """Obtiene la racha histórica; un dato ausente no suma ni interrumpe."""
    longest = 0
    current = 0
    for day in days:
        count = day["count"]
        if count is None:
            continue
        if int(count) > 0:
            current += 1
            longest = max(longest, current)
        else:
            current = 0
    return longest


def build_stats(
    days: list[dict[str, int | str | None]],
) -> dict[str, int | str | dict[str, int | str]]:
    """Resume los datos ya validados del calendario."""
    known_days = [day for day in days if day["count"] is not None]
    best_day = max(known_days, key=lambda day: int(day["count"]))

    return {
        "total": sum(int(day["count"]) for day in known_days),
        "days_tracked": len(days),
        "days_missing_count": len(days) - len(known_days),
        "active_days": sum(int(day["count"]) > 0 for day in known_days),
        "current_streak": calculate_current_streak(days),
        "longest_streak": calculate_longest_streak(days),
        "best_day": {
            "date": str(best_day["date"]),
            "count": int(best_day["count"]),
        },
        "weeks": len({int(day["week"]) for day in days}),
        "first_date": str(days[0]["date"]),
        "last_date": str(days[-1]["date"]),
    }


def main() -> int:
    try:
        days = parse_days(fetch_html())
    except (requests.RequestException, TypeError, ValueError) as error:
        print(f"No se pudieron obtener las contribuciones: {error}", file=sys.stderr)
        return 1

    if not days:
        print("Scrape roto: no se encontró ningún día.", file=sys.stderr)
        return 1

    missing_count = sum(day["count"] is None for day in days)
    if missing_count > len(days) * 0.5:
        print(
            "Scrape roto: más del 50% de los días no tiene conteo.",
            file=sys.stderr,
        )
        return 1

    stats = build_stats(days)
    payload = {
        "username": USERNAME,
        "generated_at": datetime.now(UTC).isoformat(timespec="seconds").replace(
            "+00:00", "Z"
        ),
        "source_url": SOURCE_URL,
        "days": days,
        "stats": stats,
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print(
        f"total={stats['total']} "
        f"active_days={stats['active_days']} "
        f"current_streak={stats['current_streak']} "
        f"longest_streak={stats['longest_streak']} "
        f"days_missing_count={stats['days_missing_count']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
