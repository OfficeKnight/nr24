"""Prüfung 7. Pflichtangaben, geprüft wird nur das Vorhandensein. Kein Rechtsrat."""
if __name__ == "__main__":
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    import lib.start  # noqa: F401

import re

from lib.adressen import absolut, pfad
from lib.kern import Beleg, Ergebnis, NichtPruefbar

NUMMER = 7
TITEL = "Pflichtangaben"

SEITEN = {
    "Impressum": re.compile(r"(?i)impressum|imprint|anbieterkennzeichnung"),
    "Datenschutz": re.compile(r"(?i)datenschutz|privacy"),
    "AGB": re.compile(r"(?i)\bagb\b|allgemeine\s+geschäftsbedingungen|/agb"),
    "Widerruf": re.compile(r"(?i)widerruf"),
}
WIDERRUFSFUNKTION = re.compile(
    r"(?i)(vertrag\w*\s+(hier\s+|jetzt\s+)?widerrufen|widerruf\s+(online\s+)?(erklären|einreichen|absenden|senden|starten)"
    r"|widerrufsbutton|widerrufsfunktion|(jetzt|hier|online)\s+widerrufen|widerruf\s+bestätigen)")
PREIS = re.compile(r"(\d{1,3}(?:\.\d{3})*,\d{2}\s?(?:€|EUR)|(?:€|EUR)\s?\d{1,3}(?:\.\d{3})*,\d{2})")
MWST = re.compile(r"(?i)((inkl\.?|inklusive|zzgl\.?|zuzüglich|exkl\.?)\s*(der\s+)?(gesetzl\w*\.?\s+)?"
                  r"(mwst|mehrwertsteuer|ust|umsatzsteuer)|§\s*19\s*ustg|mwst\.?\s+(enthalten|inklusive))")
VERSAND = re.compile(r"(?i)((zzgl\.?|zuzüglich|inkl\.?|inklusive|exkl\.?|plus)\s*(\w+\s+)?versand"
                     r"|versandkosten|versandkostenfrei|versandfrei|kostenloser\s+versand)")
BESTELL_KANDIDAT = re.compile(
    r"(?i)(bestell|kaufen|zahlungspflichtig|kostenpflichtig|\border\b|checkout|auftrag\s+(erteilen|absenden)"
    r"|jetzt\s+buchen|zahlen)")
BESTELL_EINDEUTIG = re.compile(
    r"(?i)^\s*((zahlungspflichtig|kostenpflichtig)\s+(bestellen|buchen|beauftragen|abschließen|abschliessen|kaufen)"
    r"|(jetzt\s+)?kaufen|kauf\s+abschließen)\s*$")
OHNE_BESTELLUNG = re.compile(r"(?i)warenkorb|zur\s+kasse|weiter|prüfen|ändern")


def _links_mit_text(seite):
    for a in seite.soup.find_all("a", href=True):
        text = " ".join(filter(None, [a.get_text(" ", strip=True), a.get("aria-label"), a.get("title")]))
        yield a, text


def _sichtbarer_text(seite) -> str:
    soup = seite.soup
    teile = []
    for knoten in soup.find_all(string=True):
        if knoten.parent and knoten.parent.name in ("script", "style", "noscript", "template", "title"):
            continue
        teile.append(str(knoten))
    return re.sub(r"\s+", " ", " ".join(teile))


def _knopf_text(el) -> str:
    if el.name == "input":
        return (el.get("value") or el.get("aria-label") or "").strip()
    return " ".join(filter(None, [el.get_text(" ", strip=True), el.get("aria-label")])).strip()


def pruefen(k) -> Ergebnis:
    erg = Ergebnis(NUMMER, TITEL)
    e = k.erfassung()
    seiten = e.html_seiten()
    if not seiten:
        raise NichtPruefbar("Keine erreichbare HTML-Seite gefunden.")

    # 7a Rechtstexte von jeder Seite erreichbar
    for name, muster in SEITEN.items():
        fehler, ok = [], []
        ziele = {}
        for s in seiten:
            treffer = None
            if muster.search(pfad(s.endadresse)):  # die Seite selbst muss nicht auf sich verlinken
                ziele.setdefault(s.endadresse, []).append(s.endadresse)
                continue
            for a, text in _links_mit_text(s):
                ziel = absolut(s.endadresse, a["href"])
                if ziel and (muster.search(text) or muster.search(a["href"])):
                    if name == "Widerruf" and WIDERRUFSFUNKTION.search(text):
                        continue
                    treffer = (a["href"], ziel)
                    break
            if not treffer:
                fehler.append(Beleg(s.endadresse, f"Link {name}", "Kein Link auf dieser Seite gefunden"))
            else:
                ziele.setdefault(treffer[1], []).append(s.endadresse)
        for ziel, quellen in ziele.items():
            zs = e.seite_zu(ziel)
            if zs is None:
                fehler.append(Beleg(quellen[0], f"Link {name} nach {ziel}", "Ziel wurde nicht abgerufen"))
            elif not zs.ok:
                fehler.append(Beleg(quellen[0], f"Link {name} nach {ziel}",
                                    f"Ziel liefert {zs.antwort.status or zs.antwort.fehler}"))
            else:
                ok.append(Beleg(ziel, f"Link {name}", f"Von {len(quellen)} von {len(seiten)} Seiten verlinkt, Status 200"))
        erg.bewerten(f"{name} von jeder Seite erreichbar", fehler, ok)

    # 7b Widerrufsfunktion
    ok, hinweise = [], []
    fundseiten = []
    for s in seiten:
        for el in s.soup.find_all(["a", "button", "input"]):
            text = _knopf_text(el) if el.name != "a" else " ".join(
                filter(None, [el.get_text(" ", strip=True), el.get("aria-label")]))
            if text and WIDERRUFSFUNKTION.search(text):
                fundseiten.append(s.endadresse)
                ok.append(Beleg(s.endadresse, f"<{el.name}> {text[:80]}", "Element zur Widerrufsfunktion gefunden"))
                break
    if fundseiten:
        if len(set(fundseiten)) < len(seiten):
            hinweise.append(Beleg(k.hauptadresse, "Widerrufsfunktion",
                                  f"Auf {len(set(fundseiten))} von {len(seiten)} Seiten gefunden"))
        erg.bewerten("Widerrufsfunktion auffindbar", [], ok[:20], hinweise)
    else:
        erg.bewerten("Widerrufsfunktion auffindbar", [Beleg(
            k.hauptadresse, "Links und Knöpfe",
            f"Auf {len(seiten)} Seiten kein Link oder Knopf wie Vertrag widerrufen gefunden")])

    # 7c Preise mit Hinweis auf Mehrwertsteuer und Versand
    fehler, ok = [], []
    for s in seiten:
        text = _sichtbarer_text(s)
        preise = PREIS.findall(text)
        if not preise:
            continue
        maengel = []
        if not MWST.search(text):
            maengel.append("Mehrwertsteuer")
        if not VERSAND.search(text):
            maengel.append("Versandkosten")
        if maengel:
            fehler.append(Beleg(s.endadresse, f"Preis {preise[0]}", "Kein Hinweis auf " + " und ".join(maengel)))
        else:
            ok.append(Beleg(s.endadresse, f"Preis {preise[0]}",
                            f"{len(preise)} Preise, Hinweis {MWST.search(text).group(0)} und {VERSAND.search(text).group(0)}"))
    if fehler or ok:
        erg.bewerten("Preise mit Hinweis auf Mehrwertsteuer und Versand", fehler, ok)
    else:
        erg.nicht_pruefbar("Preise mit Hinweis auf Mehrwertsteuer und Versand", k.hauptadresse, "Seitentext",
                           "Auf keiner Seite einen Preis gefunden")

    # 7d Bestellknopf
    fehler, ok = [], []
    for s in seiten:
        kandidaten = []
        for el in s.soup.find_all(["button", "input"]):
            if el.name == "input" and (el.get("type") or "").lower() not in ("submit", "image", "button"):
                continue
            if el.name == "button" and (el.get("type") or "submit").lower() not in ("submit",):
                continue
            text = _knopf_text(el)
            if text and BESTELL_KANDIDAT.search(text) and not OHNE_BESTELLUNG.search(text):
                kandidaten.append((el, text))
        if not kandidaten:
            continue
        eindeutig = [t for _, t in kandidaten if BESTELL_EINDEUTIG.search(t)]
        if eindeutig:
            ok.append(Beleg(s.endadresse, f"Knopf {eindeutig[0]}", "Beschriftung eindeutig"))
        else:
            for _, t in kandidaten:
                fehler.append(Beleg(s.endadresse, f"Knopf {t}", "Beschriftung nicht eindeutig, etwa zahlungspflichtig bestellen"))
    if fehler or ok:
        erg.bewerten("Bestellknopf eindeutig beschriftet", fehler, ok)
    else:
        erg.nicht_pruefbar("Bestellknopf eindeutig beschriftet", k.hauptadresse, "Absendeknöpfe",
                           "Kein Bestellknopf ohne Interaktion gefunden, etwa weil die Kasse erst nach Anmeldung oder mit gefülltem Warenkorb erscheint")
    erg.hinweis(k.hauptadresse, "Umfang", "Geprüft wird nur das Vorhandensein, nicht die inhaltliche oder rechtliche Richtigkeit")
    return erg


if __name__ == "__main__":
    from lib.ablauf import einzeln
    einzeln(sys.modules[__name__])
