"""Führt Prüfmodule aus, schreibt den Bericht und ermittelt den Rückgabewert."""
from __future__ import annotations

import sys
import traceback

from .bericht import SYMBOL, schreiben
from .kern import NICHT_BESTANDEN, NICHT_PRUEFBAR, Ergebnis, NichtPruefbar
from .kontext import Kontext, parser_bauen


def modul_ausfuehren(modul, kontext) -> Ergebnis:
    print(f"[{modul.NUMMER}] {modul.TITEL}", file=sys.stderr, flush=True)
    try:
        return modul.pruefen(kontext)
    except NichtPruefbar as e:
        erg = Ergebnis(modul.NUMMER, modul.TITEL)
        erg.nicht_pruefbar("Voraussetzung", kontext.ziel, "Prüflauf", str(e))
        return erg
    except Exception as e:  # ein Fehler im Werkzeug darf die übrigen Prüfungen nicht verhindern
        traceback.print_exc()
        erg = Ergebnis(modul.NUMMER, modul.TITEL)
        erg.nicht_pruefbar("Voraussetzung", kontext.ziel, "Werkzeugfehler", f"{type(e).__name__} {e}")
        return erg


def rueckgabewert(ergebnisse: list, streng: bool) -> int:
    if any(e.status == NICHT_BESTANDEN for e in ergebnisse):
        return 1
    if streng and any(e.status == NICHT_PRUEFBAR for e in ergebnisse):
        return 3
    return 0


def ausgeben(ergebnisse: list, verzeichnis) -> None:
    print("", file=sys.stderr)
    for e in ergebnisse:
        print(f"  {e.nummer:>2}. {e.titel:<32} {SYMBOL[e.status]}")
    print(f"\nBericht unter {verzeichnis}")


def einzeln(modul) -> None:
    """Einstieg für den direkten Aufruf eines einzelnen Prüfmoduls."""
    args = parser_bauen(f"Prüfung {modul.NUMMER} {modul.TITEL}").parse_args()
    kontext = Kontext(args)
    erg = modul_ausfuehren(modul, kontext)
    verz = schreiben(kontext, [erg], name=f"pruefung-{modul.NUMMER:02d}")
    ausgeben([erg], verz)
    sys.exit(rueckgabewert([erg], args.streng))
