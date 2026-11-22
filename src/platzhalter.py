#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sammelt alle Platzhalter in eckigen Klammern, zum Beispiel [Bearbeitungszeit], aus den Quellen.

Aufruf aus der Repo-Wurzel:

    python3 src/platzhalter.py            Liste mit Anzahl und Fundstellen
    python3 src/platzhalter.py --markdown Tabelle für die README

Durchsucht werden die Texte in src/daten/*.json (nur Zeichenketten, nicht die JSON-Listen selbst),
src/inhalte/*.html und src/vorlagen/*.html. Nur Python-Standardbibliothek.
"""

import argparse
import json
import re
from collections import OrderedDict
from pathlib import Path

WURZEL = Path(__file__).resolve().parent.parent
SRC = WURZEL / "src"

# Ein Platzhalter beginnt mit einem Buchstaben oder einer Ziffer und enthält keine Klammern oder Anführungszeichen.
MUSTER = re.compile(r"\[([A-Za-zÄÖÜäöüß0-9][^\[\]\"<>{}]{0,120})\]")
# Keine Platzhalter: Zeichenklassen in pattern-Attributen wie [0-9] und CSS-Selektoren wie [hidden].
KEIN_PLATZHALTER = re.compile(r"^\[(?:[A-Za-z0-9]-[A-Za-z0-9]|hidden|data-[a-z-]+)\]$")


def texte_aus_json(wert, pfad=""):
    """Liefert (pfad, text) für jede Zeichenkette in einer JSON-Struktur."""
    if isinstance(wert, str):
        yield pfad, wert
    elif isinstance(wert, dict):
        for k, v in wert.items():
            yield from texte_aus_json(v, f"{pfad}.{k}" if pfad else k)
    elif isinstance(wert, list):
        for i, v in enumerate(wert):
            yield from texte_aus_json(v, f"{pfad}[{i}]")


def sammeln():
    funde = OrderedDict()

    def merken(name, ort):
        if KEIN_PLATZHALTER.match(name):
            return
        funde.setdefault(name, []).append(ort)

    for datei in sorted((SRC / "daten").glob("*.json")):
        daten = json.loads(datei.read_text(encoding="utf-8"))
        for pfad, text in texte_aus_json(daten):
            for m in MUSTER.finditer(text):
                merken(m.group(0), f"{datei.relative_to(WURZEL)} ({pfad})")
    for ordner in ("inhalte", "vorlagen"):
        for datei in sorted((SRC / ordner).glob("*.html")):
            text = datei.read_text(encoding="utf-8")
            text = re.sub(r"\{#.*?#\}", "", text, flags=re.S)   # Vorlagenkommentare
            for nr, zeile in enumerate(text.splitlines(), 1):
                for m in MUSTER.finditer(zeile):
                    merken(m.group(0), f"{datei.relative_to(WURZEL)}:{nr}")
    return funde


def main():
    parser = argparse.ArgumentParser(description="Platzhalter in eckigen Klammern sammeln.")
    parser.add_argument("--markdown", action="store_true", help="Ausgabe als Markdown-Tabelle")
    args = parser.parse_args()
    funde = sammeln()
    reihen = sorted(funde.items(), key=lambda kv: kv[0].lower())
    if args.markdown:
        print("| Platzhalter | Anzahl | Fundstellen (Auswahl) |")
        print("|---|---|---|")
        for name, orte in reihen:
            dateien = sorted({o.split(" (")[0].split(":")[0] for o in orte})
            print(f"| `{name}` | {len(orte)} | {', '.join(f'`{d}`' for d in dateien)} |")
    else:
        for name, orte in reihen:
            print(f"{name}  ({len(orte)}x)")
            for o in orte[:8]:
                print(f"    {o}")
            if len(orte) > 8:
                print(f"    und {len(orte) - 8} weitere")
    print(f"\n{len(funde)} verschiedene Platzhalter, {sum(len(o) for o in funde.values())} Fundstellen.")


if __name__ == "__main__":
    main()
