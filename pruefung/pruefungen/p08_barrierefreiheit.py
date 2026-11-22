"""Prüfung 8. Barrierefreiheit mit axe-core (WCAG 2.2 A und AA) und Zoombarkeit."""
if __name__ == "__main__":
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    import lib.start  # noqa: F401

import re

from lib.kern import Beleg, Ergebnis

NUMMER = 8
TITEL = "Barrierefreiheit"


def zoom_gesperrt(inhalt: str | None) -> str | None:
    if not inhalt:
        return None
    werte = {}
    for teil in re.split(r"[,;]", inhalt):
        k, _, v = teil.partition("=")
        werte[k.strip().lower()] = v.strip().lower()
    if werte.get("user-scalable") in ("no", "0"):
        return f"user-scalable={werte['user-scalable']}"
    if "maximum-scale" in werte:
        try:
            if float(werte["maximum-scale"]) < 2:
                return f"maximum-scale={werte['maximum-scale']}"
        except ValueError:
            pass
    return None


def pruefen(k) -> Ergebnis:
    erg = Ergebnis(NUMMER, TITEL)
    daten = k.browser()
    seiten = daten["seiten"]

    fehler, ok, hinweise, unpruefbar = [], [], [], []
    for s in seiten:
        if s.get("fehler") or s.get("axe") is None:
            unpruefbar.append(Beleg(s["url"], "axe-core", s.get("fehler") or "Keine Ergebnisse"))
            continue
        v = s["axe"]["verstoesse"]
        for regel in v:
            for knoten in regel["knoten"][:3]:
                fehler.append(Beleg(s["url"], f"{regel['id']} ({regel['impact']}) {knoten['ziel']}",
                                    f"{regel['hilfe']}. {knoten['html']}"))
            if regel["anzahl"] > 3:
                fehler.append(Beleg(s["url"], f"{regel['id']} ({regel['impact']})",
                                    f"Weitere {regel['anzahl'] - 3} Stellen auf dieser Seite"))
        if not v:
            ok.append(Beleg(s["url"], "axe-core", "Keine Verstöße"))
        for regel in s["axe"]["unklar"]:
            hinweise.append(Beleg(s["url"], f"{regel['id']} an {regel['anzahl']} Stellen",
                                  f"{regel['hilfe']}. axe-core kann das nicht automatisch entscheiden, bitte von Hand prüfen"))
    erg.bewerten("axe-core WCAG 2.2 A und AA", fehler, ok, hinweise, unpruefbar)

    fehler, ok, hinweise = [], [], []
    for s in seiten:
        if s.get("fehler"):
            continue
        sperre = zoom_gesperrt(s.get("viewport"))
        if sperre:
            fehler.append(Beleg(s["url"], 'meta name="viewport"', f"Zoomen gesperrt durch {sperre}"))
        elif s.get("viewport") is None:
            hinweise.append(Beleg(s["url"], 'meta name="viewport"', "Keine Viewport-Angabe, Darstellung am Handy prüfen"))
        else:
            ok.append(Beleg(s["url"], 'meta name="viewport"', s["viewport"]))
    erg.bewerten("Zoomen am Handy nicht gesperrt", fehler, ok, hinweise)
    erg.hinweis(k.hauptadresse, "Werkzeug",
                f"axe-core {daten.get('axe')} mit den Regelgruppen {', '.join(k.einstellungen.get('axe_tags', []))}. "
                "Automatische Tests finden nur einen Teil der Barrieren, eine Prüfung von Hand bleibt nötig")
    return erg


if __name__ == "__main__":
    from lib.ablauf import einzeln
    einzeln(sys.modules[__name__])
