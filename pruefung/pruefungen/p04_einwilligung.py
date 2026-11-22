"""Prüfung 4. Verhalten vor jeder Einwilligung, gemessen in einem frischen Browser."""
if __name__ == "__main__":
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    import lib.start  # noqa: F401

import re

from lib.adressen import host
from lib.kern import Beleg, Ergebnis

NUMMER = 4
TITEL = "Vor Einwilligung"


def _eigener_cookie(domain: str, eigene: set) -> bool:
    d = domain.lstrip(".").lower()
    return any(d == h or h.endswith("." + d) for h in eigene)


def pruefen(k) -> Ergebnis:
    erg = Ergebnis(NUMMER, TITEL)
    daten = k.browser()
    eigene = k.eigene_hosts
    noetig = [re.compile(m) for m in k.einstellungen.get("noetige_cookies", [])]
    seiten = daten["seiten"]

    # 4a keine Anfragen an fremde Hosts
    fehler, ok, unpruefbar = [], [], []
    for s in seiten:
        if s.get("fehler"):
            unpruefbar.append(Beleg(s["url"], "Browserlauf", s["fehler"]))
            continue
        fremd = [a for a in s["anfragen"] if a["url"].startswith(("http://", "https://"))
                 and host(a["url"]) not in eigene]
        for a in fremd:
            zusatz = f", fehlgeschlagen ({a['fehler']})" if a.get("fehler") else ""
            fehler.append(Beleg(s["url"], f"Anfrage {a['typ']} an {host(a['url'])}",
                                f"{a['methode']} {a['url']}{zusatz}"))
        if not fremd:
            ok.append(Beleg(s["url"], "Netzwerkanfragen",
                            f"{len(s['anfragen'])} Anfragen, alle an eigene Hosts"))
    erg.bewerten("Keine Anfragen an fremde Hosts", fehler, ok, None, unpruefbar)

    # 4b nur technisch nötige Cookies
    fehler, ok, hinweise = [], [], []
    for s in seiten:
        if s.get("fehler"):
            continue
        for c in s["cookies"]:
            fund = f"Cookie {c['name']} auf {c['domain']}"
            if not _eigener_cookie(c["domain"], eigene):
                fehler.append(Beleg(s["url"], fund, "Cookie eines fremden Hosts vor Einwilligung"))
            elif any(m.search(c["name"]) for m in noetig):
                ok.append(Beleg(s["url"], fund, "Steht auf der Liste technisch nötiger Cookies"))
            else:
                fehler.append(Beleg(s["url"], fund,
                                    "Nicht als technisch nötig eingestuft, gesetzt ohne Einwilligung"))
        for art in ("local", "session"):
            for schluessel in s.get("speicher", {}).get(art, []):
                hinweise.append(Beleg(s["url"], f"{art}Storage {schluessel}",
                                      "Speichereintrag vor Einwilligung, bitte auf Erforderlichkeit prüfen"))
    if not any(b for b in fehler) and not ok:
        ok.append(Beleg(k.hauptadresse, "Cookies", f"Auf {len(seiten)} Seiten keine Cookies gesetzt"))
    erg.bewerten("Nur technisch nötige Cookies", fehler, ok, hinweise)
    erg.hinweis(k.hauptadresse, "Verfahren",
                f"Jede Seite wurde in einem neu gestarteten Chromium {daten.get('chromium')} geladen, "
                "ohne Klick und ohne gespeicherte Daten. Erfasst wurde nach dem Laden und einer kurzen Wartezeit")
    return erg


if __name__ == "__main__":
    from lib.ablauf import einzeln
    einzeln(sys.modules[__name__])
