#!/usr/bin/env python3
"""Cuenta lo que hay en el taller y lo vuelca a data/facts.json.

VanguardIA es privado, asi que el workflow de este repo no puede leerlo. Este
script se lanza a mano desde el portatil apuntando al repo, y deja en facts.json
solo agregados: cuantas skills, cuantos ADRs, cuantos commits. Ningun nombre de
fichero, ningun cliente, ningun contenido.

    python scripts/collect_workshop_facts.py --repo ~/Desktop/VanguardIA
"""
from __future__ import annotations

import argparse
import datetime
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FACTS = ROOT / "data" / "facts.json"

# etiqueta -> (subdirectorio, patron glob)
COUNTS = {
    "skills":   (".claude/skills", "*/SKILL.md"),
    "agents":   (".claude/agents", "*.md"),
    "commands": (".claude/commands", "*.md"),
    "rules":    (".claude/rules", "*.md"),
    "adrs":     ("notes/knowledge/decisions", "ADR-*.md"),
    "runbooks": ("notes/knowledge/runbooks", "*.md"),
    "patterns": ("notes/knowledge/patterns", "*.md"),
    "dailies":  ("notes/daily", "*.md"),
}


def git(repo: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(repo), *args],
                          capture_output=True, text=True, check=True).stdout.strip()


def collect(repo: Path) -> dict:
    if not (repo / ".git").exists():
        raise SystemExit(f"{repo} no es un repo git")

    out = {k: len(list((repo / sub).glob(pat))) for k, (sub, pat) in COUNTS.items()}
    out["commits"] = int(git(repo, "rev-list", "--count", "HEAD"))
    out["since"] = git(repo, "log", "--reverse", "--format=%ad", "--date=short").splitlines()[0]
    out["counted_at"] = datetime.date.today().isoformat()

    empty = [k for k, v in out.items() if isinstance(v, int) and v == 0]
    if empty:
        # un cero aqui casi siempre es una ruta que cambio, no un directorio vacio
        print(f"  aviso: a cero -> {', '.join(empty)}")
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True, type=Path, help="ruta al repo del taller")
    args = ap.parse_args()

    facts = json.loads(FACTS.read_text(encoding="utf-8"))
    facts["workshop"] = collect(args.repo.expanduser())
    FACTS.write_text(json.dumps(facts, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    w = facts["workshop"]
    print(f"{FACTS.relative_to(ROOT)} actualizado")
    print(f"  {w['commits']:,} commits desde {w['since']} · {w['skills']} skills · "
          f"{w['agents']} agents · {w['adrs']} ADRs · {w['runbooks']} runbooks")


if __name__ == "__main__":
    main()
