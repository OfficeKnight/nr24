#!/usr/bin/env python3
"""Automatische Abnahmeprüfung für den Onlineshop Notebook Reparatur 24.

Beispiel
    python3 pruefung/pruefen.py --ziel https://nr24.kazas.dev --modus demo
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lib.start  # noqa: E402,F401  wechselt bei Bedarf in die venv

from lib.ablauf import ausgeben, modul_ausfuehren, rueckgabewert  # noqa: E402
from lib.bericht import schreiben  # noqa: E402
from lib.kontext import Kontext, parser_bauen  # noqa: E402
from pruefungen import ALLE  # noqa: E402


def main() -> int:
    p = parser_bauen("Automatische Abnahmeprüfung für einen deutschen Onlineshop")
    p.add_argument("--nur", help="Nur diese Prüfungen ausführen, etwa 3,5,7")
    args = p.parse_args()
    module = ALLE
    if args.nur:
        gewuenscht = {int(x) for x in args.nur.split(",") if x.strip()}
        module = [m for m in ALLE if m.NUMMER in gewuenscht]
    kontext = Kontext(args)
    print(f"Abnahmeprüfung für {kontext.ziel} im Modus {kontext.modus}", file=sys.stderr)
    ergebnisse = [modul_ausfuehren(m, kontext) for m in module]
    verz = schreiben(kontext, ergebnisse)
    ausgeben(ergebnisse, verz)
    return rueckgabewert(ergebnisse, args.streng)


if __name__ == "__main__":
    sys.exit(main())
