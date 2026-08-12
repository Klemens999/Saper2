#!/usr/bin/env python3
"""Generuje plan.html z room.json + template.html.

room.json jest jedynym zrodlem prawdy o wymiarach. Po kazdej zmianie pomiarow
uruchom ten skrypt, zeby odswiezyc rysunek:

    python3 room-design/build_plan.py
"""

import json
import sys
from pathlib import Path

HERE = Path(__file__).parent
ROOM = HERE / "room.json"
TEMPLATE = HERE / "template.html"
OUT = HERE / "plan.html"

MARKER = "/*__ROOM_DATA__*/"


def validate(data):
    """Wylapuje bledy w danych zanim trafia do rysunku."""
    problems = []
    room = data["room"]
    if room["width"] <= 0 or room["depth"] <= 0:
        problems.append("room.width / room.depth musza byc dodatnie")

    ids = {f["id"] for f in data["furniture"]}
    dupes = len(ids) != len(data["furniture"])
    if dupes:
        problems.append("zduplikowane id w furniture")

    zones = set(data["zones"])
    for f in data["furniture"]:
        if f["zone"] not in zones:
            problems.append(f"mebel {f['id']}: nieznana strefa {f['zone']!r}")

    for op in data["openings"] + data["fixtures"]:
        wall = op["wall"]
        if wall not in "NSEW":
            problems.append(f"{op['id']}: zla sciana {wall!r}")
            continue
        span = room["width"] if wall in "NS" else room["depth"]
        end = op["offset"] + op.get("width", 0)
        if op["offset"] < 0 or end > span:
            problems.append(
                f"{op['id']}: offset {op['offset']}+{op.get('width', 0)} wychodzi poza sciane {wall} ({span} cm)"
            )

    for layout in data["layouts"]:
        seen = set()
        for p in layout["placements"]:
            if p["ref"] not in ids:
                problems.append(f"uklad {layout['id']}: nieznany mebel {p['ref']!r}")
            if p["ref"] in seen:
                problems.append(f"uklad {layout['id']}: mebel {p['ref']!r} uzyty dwa razy")
            seen.add(p["ref"])
            if p.get("rot", 0) % 90:
                problems.append(f"uklad {layout['id']}/{p['ref']}: rot musi byc wielokrotnoscia 90")
        missing = ids - seen
        if missing:
            problems.append(
                f"uklad {layout['id']}: nie rozstawiono {', '.join(sorted(missing))}"
            )
    return problems


def main():
    data = json.loads(ROOM.read_text(encoding="utf-8"))

    problems = validate(data)
    if problems:
        print("Bledy w room.json:", file=sys.stderr)
        for p in problems:
            print("  - " + p, file=sys.stderr)
        return 1

    template = TEMPLATE.read_text(encoding="utf-8")
    if MARKER not in template:
        print(f"Brak znacznika {MARKER} w template.html", file=sys.stderr)
        return 1

    # </script> w danych rozerwalby tag <script>; w praktyce nie wystepuje,
    # ale escapujemy dla bezpieczenstwa
    payload = json.dumps(data, ensure_ascii=False, indent=2).replace("</", "<\\/")
    OUT.write_text(template.replace(MARKER, payload), encoding="utf-8")

    room = data["room"]
    print(f"OK  {OUT.relative_to(HERE.parent)}")
    print(f"    pokoj {room['width']}x{room['depth']} cm "
          f"({room['width'] * room['depth'] / 10000:.1f} m2), "
          f"{len(data['layouts'])} ukladow, {len(data['furniture'])} mebli")
    if data["meta"]["status"] == "PLACEHOLDER":
        print("    UWAGA: dane zastepcze - podmien na realne pomiary")
    return 0


if __name__ == "__main__":
    sys.exit(main())
