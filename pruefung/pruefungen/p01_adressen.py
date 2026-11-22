"""Prüfung 1. Adressen, Umleitung auf https, Hauptadresse und alte Weiterleitungen."""
if __name__ == "__main__":
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    import lib.start  # noqa: F401

import csv

from lib.adressen import host, mit_www, normalisieren, ohne_www
from lib.kern import Beleg, Ergebnis

NUMMER = 1
TITEL = "Adressen und Weiterleitungen"


def _kette_text(kette) -> str:
    teile = []
    for url, status, _ort, fehler in kette:
        teile.append(f"{url} ({status or fehler})")
    return " nach ".join(teile)


def _nicht_aufloesbar(a) -> bool:
    return bool(a.fehler and "Name nicht auflösbar" in a.fehler)


def pruefen(k) -> Ergebnis:
    erg = Ergebnis(NUMMER, TITEL)
    ab = k.abrufer
    basis = ohne_www(k.zielhost)
    varianten = [f"http://{basis}/", f"http://{mit_www(basis)}/",
                 f"https://{basis}/", f"https://{mit_www(basis)}/"]
    ergebnisse = {v: ab.folgen(v, text_lesen=False) for v in varianten}

    # 1a http leitet per 301 auf https um
    fehler, ok, hinweise, unpruefbar = [], [], [], []
    for v in varianten[:2]:
        a = ergebnisse[v]
        if a.fehler:
            if _nicht_aufloesbar(a) and v != varianten[0] and k.modus == "demo":
                hinweise.append(Beleg(v, "DNS", "Variante hat keinen DNS-Eintrag, im Modus demo nur ein Hinweis"))
            elif _nicht_aufloesbar(a) and v != varianten[0]:
                fehler.append(Beleg(v, "DNS", "Variante hat keinen DNS-Eintrag"))
            else:
                unpruefbar.append(Beleg(v, "Erster Abruf", a.fehler))
            continue
        erster = a.kette[0]
        ort = erster[2] or ""
        if erster[1] != 301:
            fehler.append(Beleg(v, "Statuscode erster Antwort", f"Status {erster[1]} statt 301"))
        elif not ort.startswith("https://"):
            fehler.append(Beleg(v, "Location", f"Ziel {ort} ist nicht https"))
        else:
            ok.append(Beleg(v, "Location", f"301 nach {ort}"))
    erg.bewerten("http leitet per 301 auf https um", fehler, ok, hinweise, unpruefbar)

    # 1b alle Varianten landen auf einer Hauptadresse
    fehler, ok, hinweise, unpruefbar = [], [], [], []
    try:
        haupt = k.hauptadresse
    except Exception as e:  # noqa: BLE001
        erg.nicht_pruefbar("Eine Hauptadresse für alle Varianten", k.ziel, "Startseite", str(e))
        haupt = None
    if haupt:
        for v, a in ergebnisse.items():
            if a.fehler:
                if _nicht_aufloesbar(a) and k.modus == "demo" and host(v) != k.zielhost:
                    hinweise.append(Beleg(v, "DNS", "Variante hat keinen DNS-Eintrag, im Modus demo nur ein Hinweis"))
                elif _nicht_aufloesbar(a):
                    fehler.append(Beleg(v, "DNS", "Variante hat keinen DNS-Eintrag"))
                else:
                    unpruefbar.append(Beleg(v, "Abruf", a.fehler))
                continue
            ende = normalisieren(a.endadresse)
            if ende != haupt:
                fehler.append(Beleg(v, "Endadresse", f"Endet auf {ende} statt auf {haupt}, Kette {_kette_text(a.kette)}"))
            elif a.status != 200:
                fehler.append(Beleg(v, "Endadresse", f"Hauptadresse liefert Status {a.status}"))
            else:
                umwege = [s for s in a.kette[:-1] if s[1] != 301]
                if umwege:
                    fehler.append(Beleg(v, "Weiterleitungskette",
                                        f"Zwischenschritt ohne 301, Kette {_kette_text(a.kette)}"))
                else:
                    ok.append(Beleg(v, "Endadresse", f"Landet auf {haupt} nach {len(a.kette) - 1} Weiterleitung(en)"))
                    if len(a.kette) > 2:
                        hinweise.append(Beleg(v, "Weiterleitungskette",
                                              f"Mehrere Sprünge, Kette {_kette_text(a.kette)}"))
        erg.bewerten("Eine Hauptadresse für alle Varianten", fehler, ok, hinweise, unpruefbar)

    # 1c alte Adressen aus der CSV
    if k.weiterleitungen:
        fehler, ok, hinweise = [], [], []
        try:
            paare = _csv_lesen(k.weiterleitungen)
        except (OSError, ValueError) as e:
            erg.nicht_pruefbar("Alte Adressen leiten per 301 weiter", k.weiterleitungen, "CSV", f"Datei nicht lesbar ({e})")
            return erg
        basisadresse = haupt or k.ziel
        for zeile, alt, neu in paare:
            alt_abs = normalisieren(_absolut(basisadresse, alt))
            neu_abs = normalisieren(_absolut(basisadresse, neu))
            fund = f"CSV Zeile {zeile}"
            a = ab.folgen(alt_abs, text_lesen=False)
            if a.fehler and len(a.kette) == 1:
                fehler.append(Beleg(alt_abs, fund, f"Alte Adresse nicht abrufbar ({a.fehler})"))
                continue
            erster = a.kette[0]
            if erster[1] != 301:
                fehler.append(Beleg(alt_abs, fund, f"Status {erster[1]} statt 301"))
                continue
            ende = normalisieren(a.endadresse)
            if a.fehler or a.status != 200:
                fehler.append(Beleg(alt_abs, fund, f"Ziel {ende} liefert {a.status or a.fehler}"))
            elif ende != neu_abs:
                fehler.append(Beleg(alt_abs, fund, f"Endet auf {ende}, erwartet war {neu_abs}"))
            else:
                ok.append(Beleg(alt_abs, fund, f"301 nach {ende}, Ziel liefert 200"))
                if len(a.kette) > 2:
                    hinweise.append(Beleg(alt_abs, fund, f"Mehrere Sprünge, Kette {_kette_text(a.kette)}"))
        if not paare:
            erg.nicht_pruefbar("Alte Adressen leiten per 301 weiter", k.weiterleitungen, "CSV", "Keine Einträge gefunden")
        else:
            erg.bewerten("Alte Adressen leiten per 301 weiter", fehler, ok, hinweise)
    else:
        erg.hinweis(k.ziel, "Weiterleitungsliste", "Keine Datei mit --weiterleitungen angegeben, alte Adressen wurden nicht geprüft")
    return erg


def _absolut(basis: str, wert: str) -> str:
    from urllib.parse import urljoin
    return urljoin(basis, wert.strip())


def _csv_lesen(pfad: str) -> list:
    paare = []
    with open(pfad, encoding="utf-8-sig", newline="") as f:
        for nr, zeile in enumerate(csv.reader(f, delimiter=";"), start=1):
            if not zeile or not "".join(zeile).strip() or zeile[0].strip().startswith("#"):
                continue
            if nr == 1 and zeile[0].strip().lower() == "url_alt":
                continue
            if len(zeile) < 2:
                raise ValueError(f"Zeile {nr} hat keine zwei Spalten")
            paare.append((nr, zeile[0], zeile[1]))
    return paare


if __name__ == "__main__":
    from lib.ablauf import einzeln
    einzeln(sys.modules[__name__])
