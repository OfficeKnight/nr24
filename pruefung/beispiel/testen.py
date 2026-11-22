#!/usr/bin/env python3
"""Testet das Werkzeug gegen die lokalen Beispielseiten.

Startet Testserver und DNS-Server, führt vier Prüfläufe und einen Einzelaufruf aus und vergleicht
jedes Ergebnis mit der Erwartung. Benötigt Rechte für die Ports 80 und 443 auf 127.0.0.1 und 127.0.0.2.

Aufruf aus dem Repo mit python3 pruefung/beispiel/testen.py
"""
from __future__ import annotations

import json
import socket
import subprocess
import sys
import tempfile
import time
from datetime import date
from pathlib import Path

HIER = Path(__file__).resolve().parent
WURZEL = HIER.parent
sys.path.insert(0, str(WURZEL))
import lib.start  # noqa: E402,F401  wechselt bei Bedarf in die venv
PYTHON = str(WURZEL / ".venv" / "bin" / "python") if (WURZEL / ".venv" / "bin" / "python").exists() else sys.executable
B, N = "bestanden", "nicht bestanden"

GEMEINSAM = ["--dkim-selektor", "mail", "--ca-datei", str(HIER / "zertifikate" / "ca.crt"),
             "--dns-server", "127.0.0.1:5353"]


def aufloesen(*paare):
    args = []
    for h, ip in paare:
        args += ["--aufloesen", f"{h}={ip}"]
    return args


LAEUFE = [
    {"name": "gut.test im Modus demo, alles bestanden",
     "args": ["--ziel", "https://gut.test", "--modus", "demo",
              "--weiterleitungen", str(HIER / "weiterleitungen-gut.csv")]
     + aufloesen(("gut.test", "127.0.0.1"), ("www.gut.test", "127.0.0.1")),
     "erwartet": {i: B for i in range(1, 11)}, "rueckgabe": 0, "behalten": True},
    {"name": "schlecht.test im Modus demo, alles verletzt",
     "args": ["--ziel", "https://schlecht.test", "--modus", "demo",
              "--weiterleitungen", str(HIER / "weiterleitungen-schlecht.csv")]
     + aufloesen(("schlecht.test", "127.0.0.2"), ("www.schlecht.test", "127.0.0.2"),
                 ("drittanbieter.test", "127.0.0.1")),
     "erwartet": {i: N for i in range(1, 11)}, "rueckgabe": 1, "behalten": True},
    {"name": "live.test im Modus live, alles bestanden",
     "args": ["--ziel", "https://live.test", "--modus", "live",
              "--weiterleitungen", str(HIER / "weiterleitungen-gut.csv")]
     + aufloesen(("live.test", "127.0.0.1"), ("www.live.test", "127.0.0.1")),
     "erwartet": {i: B for i in range(1, 11)}, "rueckgabe": 0, "behalten": True},
    {"name": "gut.test im Modus live, noindex und robots.txt verletzt",
     "args": ["--ziel", "https://gut.test", "--modus", "live", "--nur", "5"]
     + aufloesen(("gut.test", "127.0.0.1"), ("www.gut.test", "127.0.0.1")),
     "erwartet": {5: N}, "rueckgabe": 1, "behalten": False,
     "teile": {"noindex passend zum Modus live": N, "robots.txt vorhanden": N, "Genau eine H1": B}},
]


def einheiten() -> None:
    from lib.dnsabfrage import _txt_zusammensetzen
    from pruefungen.p05_auffindbarkeit import _robots_sperrt_alles
    from pruefungen.p07_pflichtangaben import BESTELL_EINDEUTIG, MWST, PREIS, VERSAND, WIDERRUFSFUNKTION
    from pruefungen.p08_barrierefreiheit import zoom_gesperrt
    assert zoom_gesperrt("width=device-width, user-scalable=no") == "user-scalable=no"
    assert zoom_gesperrt("width=device-width, maximum-scale=1.0") == "maximum-scale=1.0"
    assert zoom_gesperrt("width=device-width, initial-scale=1") is None
    assert _robots_sperrt_alles("User-agent: *\nDisallow: /\n")
    assert not _robots_sperrt_alles("User-agent: *\nDisallow: /kasse/\n")
    assert not _robots_sperrt_alles("User-agent: Bot\nDisallow: /\n")
    assert _txt_zusammensetzen('"v=DKIM1; p=abc" "def"') == "v=DKIM1; p=abcdef"
    assert BESTELL_EINDEUTIG.search("Zahlungspflichtig bestellen")
    assert BESTELL_EINDEUTIG.search("Jetzt kaufen")
    assert not BESTELL_EINDEUTIG.search("Bestellen")
    assert not BESTELL_EINDEUTIG.search("Bestellung abschicken")
    assert PREIS.search("nur 1.299,00 €") and PREIS.search("EUR 11,90")
    assert MWST.search("inkl. MwSt.") and MWST.search("zzgl. gesetzl. MwSt") and MWST.search("gemäß § 19 UStG")
    assert VERSAND.search("zzgl. Versandkosten") and VERSAND.search("versandkostenfrei")
    assert WIDERRUFSFUNKTION.search("Vertrag widerrufen")
    assert not WIDERRUFSFUNKTION.search("Widerrufsbelehrung")
    print("Einzeltests der Hilfsfunktionen bestanden")


def warten_auf(adresse: str, port: int, sekunden: float = 10) -> None:
    ende = time.time() + sekunden
    while time.time() < ende:
        try:
            with socket.create_connection((adresse, port), timeout=1):
                return
        except OSError:
            time.sleep(0.2)
    raise SystemExit(f"Server auf {adresse}:{port} startet nicht")


def lauf(args: list, berichte: Path) -> tuple:
    befehl = [PYTHON, str(WURZEL / "pruefen.py"), *args, *GEMEINSAM, "--berichte", str(berichte)]
    r = subprocess.run(befehl, capture_output=True, text=True, timeout=1800)
    return r.returncode, r.stdout, r.stderr


def main() -> int:
    einheiten()
    subprocess.run([sys.executable, str(HIER / "bauen.py")], check=True)
    subprocess.run([sys.executable, str(HIER / "zertifikate.py")], check=True)
    server = subprocess.Popen([sys.executable, str(HIER / "server.py")], stdout=subprocess.DEVNULL)
    dns = subprocess.Popen([sys.executable, str(HIER / "dns_server.py")], stdout=subprocess.DEVNULL)
    fehlschlaege = []
    try:
        warten_auf("127.0.0.1", 443)
        warten_auf("127.0.0.2", 443)
        with tempfile.TemporaryDirectory(prefix="abnahme-test-") as tmp:
            for l in LAEUFE:
                print(f"\nLauf {l['name']}", flush=True)
                ziel = WURZEL / "berichte" if l["behalten"] else Path(tmp)
                rc, aus, _fehl = lauf(l["args"], ziel)
                host = l["args"][1].split("//")[1]
                bericht = json.loads((ziel / f"{date.today():%Y-%m-%d}-{host}" / "bericht.json").read_text("utf-8"))
                ist = {p["nummer"]: p["status"] for p in bericht["pruefungen"]}
                for nr, soll in l["erwartet"].items():
                    zeichen = "ok" if ist.get(nr) == soll else "ABWEICHUNG"
                    print(f"  Prüfung {nr:>2} erwartet {soll:<16} ist {ist.get(nr)!s:<16} {zeichen}")
                    if ist.get(nr) != soll:
                        fehlschlaege.append(f"{l['name']} Prüfung {nr}")
                for name, soll in l.get("teile", {}).items():
                    teile = {t["name"]: t["status"] for p in bericht["pruefungen"] for t in p["teilpruefungen"]}
                    zeichen = "ok" if teile.get(name) == soll else "ABWEICHUNG"
                    print(f"  Teil {name} erwartet {soll} ist {teile.get(name)} {zeichen}")
                    if teile.get(name) != soll:
                        fehlschlaege.append(f"{l['name']} Teil {name}")
                zeichen = "ok" if rc == l["rueckgabe"] else "ABWEICHUNG"
                print(f"  Rückgabewert erwartet {l['rueckgabe']} ist {rc} {zeichen}")
                if rc != l["rueckgabe"]:
                    fehlschlaege.append(f"{l['name']} Rückgabewert")

            print("\nLauf Einzelaufruf von Prüfung 3 für gut.test", flush=True)
            befehl = [PYTHON, str(WURZEL / "pruefungen" / "p03_sicherheitsheader.py"), "--ziel", "https://gut.test",
                      "--modus", "demo", *aufloesen(("gut.test", "127.0.0.1"), ("www.gut.test", "127.0.0.1")),
                      *GEMEINSAM, "--berichte", tmp]
            r = subprocess.run(befehl, capture_output=True, text=True, timeout=600)
            datei = Path(tmp) / f"{date.today():%Y-%m-%d}-gut.test" / "pruefung-03.json"
            ok = r.returncode == 0 and datei.exists() and json.loads(datei.read_text("utf-8"))["gesamtergebnis"] == B
            print(f"  Einzelaufruf Rückgabewert {r.returncode}, Bericht {'vorhanden' if datei.exists() else 'fehlt'} "
                  f"{'ok' if ok else 'ABWEICHUNG'}")
            if not ok:
                fehlschlaege.append("Einzelaufruf Prüfung 3")
    finally:
        server.terminate()
        dns.terminate()
        server.wait(10)
        dns.wait(10)
    print()
    if fehlschlaege:
        print("Abweichungen bei " + ", ".join(fehlschlaege))
        return 1
    print("Alle Testläufe entsprechen der Erwartung")
    return 0


if __name__ == "__main__":
    sys.exit(main())
