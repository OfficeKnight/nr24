"""Prüfung 9. Übertragene Daten je Seite, Zahl der Anfragen, größte Dateien, optional Lighthouse."""
if __name__ == "__main__":
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    import lib.start  # noqa: F401

import json
import os
import shutil
import subprocess
from pathlib import Path

from lib.kern import Beleg, Ergebnis

NUMMER = 9
TITEL = "Leistung"
WURZEL = Path(__file__).resolve().parents[1]


def _mb(b: int) -> str:
    return f"{b / 1_000_000:.3f} MB".replace(".", ",")


def _lighthouse(k, erg) -> None:
    lh = shutil.which("lighthouse") or (str(WURZEL / "node_modules" / ".bin" / "lighthouse")
                                        if (WURZEL / "node_modules" / ".bin" / "lighthouse").exists() else None)
    if not lh:
        erg.hinweis(k.hauptadresse, "Lighthouse",
                    "Lighthouse ist nicht installiert und wurde deshalb nicht ausgeführt")
        return
    try:
        pfad = subprocess.run(["node", "-e", "import('playwright').then(p=>console.log(p.chromium.executablePath()))"],
                              cwd=str(WURZEL), capture_output=True, text=True, timeout=60).stdout.strip()
        umgebung = dict(os.environ, CHROME_PATH=pfad)
        lauf = subprocess.run([lh, k.hauptadresse, "--quiet", "--only-categories=performance", "--output=json",
                               "--output-path=stdout", "--chrome-flags=--headless --no-sandbox"],
                              capture_output=True, text=True, timeout=300, env=umgebung)
        bericht = json.loads(lauf.stdout)
        wert = bericht["categories"]["performance"]["score"]
        lcp = bericht["audits"].get("largest-contentful-paint", {}).get("displayValue", "")
        erg.hinweis(k.hauptadresse, "Lighthouse Leistung", f"Wert {round((wert or 0) * 100)} von 100, LCP {lcp}")
    except (OSError, ValueError, KeyError, subprocess.SubprocessError) as e:
        erg.hinweis(k.hauptadresse, "Lighthouse", f"Lauf fehlgeschlagen ({type(e).__name__})")


def pruefen(k) -> Ergebnis:
    erg = Ergebnis(NUMMER, TITEL)
    daten = k.browser()
    grenze = int(k.einstellungen.get("max_bytes_je_seite", 500000))
    fehler, ok, unpruefbar = [], [], []
    dateien = {}
    for s in daten["seiten"]:
        if s.get("fehler"):
            unpruefbar.append(Beleg(s["url"], "Browserlauf", s["fehler"]))
            continue
        summe = sum(a["bytes"] for a in s["anfragen"])
        anzahl = len(s["anfragen"])
        groesste = max(s["anfragen"], key=lambda a: a["bytes"], default=None)
        text = f"{_mb(summe)} in {anzahl} Anfragen"
        if groesste:
            text += f", größte Datei {groesste['url']} mit {_mb(groesste['bytes'])}"
        if summe >= grenze:
            fehler.append(Beleg(s["url"], "Übertragene Daten", f"{text}, Grenze {_mb(grenze)}"))
        else:
            ok.append(Beleg(s["url"], "Übertragene Daten", text))
        for a in s["anfragen"]:
            if a["bytes"] > dateien.get(a["url"], (0, ""))[0]:
                dateien[a["url"]] = (a["bytes"], s["url"])
    grenze_text = f"{grenze / 1_000_000:g} MB".replace(".", ",")
    erg.bewerten(f"Übertragene Daten je Seite unter {grenze_text}", fehler, ok, None, unpruefbar)
    gross = sorted(dateien.items(), key=lambda x: -x[1][0])[:10]
    belege = [Beleg(quelle, f"Datei {url}", _mb(b), "ok") for url, (b, quelle) in gross]
    erg.teil("Größte Dateien", "bestanden", belege)
    anzahlen = [len(s["anfragen"]) for s in daten["seiten"] if not s.get("fehler")]
    if anzahlen:
        erg.hinweis(k.hauptadresse, "Zahl der Anfragen",
                    f"Je Seite zwischen {min(anzahlen)} und {max(anzahlen)}, im Mittel {sum(anzahlen) / len(anzahlen):.1f}".replace(".", ","))
    erg.hinweis(k.hauptadresse, "Messung",
                "Gezählt werden Header und Inhalt jeder Antwort beim ersten Laden ohne Zwischenspeicher. "
                f"Die Grenze beträgt {grenze} Byte")
    _lighthouse(k, erg)
    return erg


if __name__ == "__main__":
    from lib.ablauf import einzeln
    einzeln(sys.modules[__name__])
