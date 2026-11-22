"""Gemeinsamer Zustand eines Prüflaufs. Erfassung und Browserlauf werden nur einmal ausgeführt."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from urllib.parse import urlsplit

from .abruf import Abrufer
from .adressen import host, mit_www, normalisieren, ohne_www
from .browser import BrowserNichtVerfuegbar, browser_erfassen
from .dnsabfrage import Resolver
from .kern import NichtPruefbar
from .netz import aufloesen_setzen, ca_buendel

WURZEL = Path(__file__).resolve().parents[1]
VERSION = "1.0.0"


def einstellungen_laden(pfad: str | None) -> dict:
    with open(WURZEL / "einstellungen.json", encoding="utf-8") as f:
        werte = json.load(f)
    if pfad:
        with open(pfad, encoding="utf-8") as f:
            werte.update(json.load(f))
    return werte


def parser_bauen(beschreibung: str) -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=beschreibung)
    p.add_argument("--ziel", required=True, help="Adresse des Shops, etwa https://nr24.kazas.dev")
    p.add_argument("--modus", required=True, choices=["demo", "live"],
                   help="demo verlangt noindex auf jeder Seite, live verbietet es")
    p.add_argument("--weiterleitungen", help="CSV mit url_alt;url_neu")
    p.add_argument("--dkim-selektor", help="DKIM-Selektor, etwa default oder mail")
    p.add_argument("--mail-domain", help="Domain für SPF, DMARC und DKIM (Vorgabe ist der Host ohne www)")
    p.add_argument("--einstellungen", help="JSON-Datei mit abweichenden Grenzwerten und Mustern")
    p.add_argument("--berichte", help="Zielverzeichnis für Berichte (Vorgabe pruefung/berichte)")
    p.add_argument("--pause", type=float, help="Pause zwischen Abrufen in Sekunden, mindestens 1")
    p.add_argument("--max-seiten", type=int, help="Höchstzahl erfasster Seiten, höchstens 200")
    p.add_argument("--aufloesen", action="append", default=[], metavar="HOST=IP",
                   help="Host fest auf eine Adresse auflösen, ohne Proxy (mehrfach möglich)")
    p.add_argument("--ca-datei", help="Zusätzliche Zertifizierungsstelle (PEM), etwa für Testserver")
    p.add_argument("--dns-server", metavar="IP[:PORT]", help="Nameserver für die DNS-Prüfung")
    p.add_argument("--dns-ueber-https", action="store_true",
                   help="DNS-Prüfung über DNS über HTTPS statt über den Systemresolver")
    p.add_argument("--streng", action="store_true",
                   help="Rückgabewert 3, wenn eine Prüfung nicht prüfbar war und keine fehlschlug")
    return p


class Kontext:
    def __init__(self, args: argparse.Namespace):
        ziel = args.ziel.strip()
        if "://" not in ziel:
            ziel = "https://" + ziel
        self.ziel = normalisieren(ziel)
        self.modus = args.modus
        self.einstellungen = einstellungen_laden(args.einstellungen)
        self.pause = max(1.0, args.pause or self.einstellungen.get("pause_sekunden", 1.0))
        self.max_seiten = max(1, min(200, args.max_seiten or self.einstellungen.get("max_seiten", 200)))
        self.weiterleitungen = args.weiterleitungen
        self.dkim_selektor = args.dkim_selektor
        self.ca_datei = args.ca_datei
        zuordnung = {}
        for eintrag in args.aufloesen:
            name, _, ip = eintrag.partition("=")
            if not ip:
                print(f"--aufloesen erwartet HOST=IP, erhalten wurde {eintrag}", file=sys.stderr)
                raise SystemExit(2)
            zuordnung[name.strip().lower()] = ip.strip()
        aufloesen_setzen(zuordnung)
        self.verify = ca_buendel(self.ca_datei)
        self.abrufer = Abrufer(self.pause, self.einstellungen.get("zeitlimit_sekunden", 20), self.verify)
        self.mail_domain = (args.mail_domain or ohne_www(host(self.ziel))).lower().strip(".")
        doh = self.einstellungen.get("doh_adresse") if args.dns_ueber_https else None
        self.resolver = Resolver(server=args.dns_server, doh=doh, verify=self.verify)
        self.berichte = Path(args.berichte) if args.berichte else WURZEL / "berichte"
        self.streng = args.streng
        self.beginn = datetime.now().astimezone()
        self._haupt = None
        self._haupt_fehler = None
        self._erfassung = None
        self._browser = None
        self._browser_fehler = None

    @property
    def zielhost(self) -> str:
        return host(self.ziel)

    @property
    def hauptadresse(self) -> str:
        """Endadresse nach allen Weiterleitungen, als Ursprung mit Schrägstrich."""
        if self._haupt is None and self._haupt_fehler is None:
            a = self.abrufer.folgen(self.ziel)
            if a.fehler or a.status != 200:
                self._haupt_fehler = f"{self.ziel} liefert {a.status or a.fehler}"
            else:
                t = urlsplit(a.endadresse)
                self._haupt = normalisieren(f"{t.scheme}://{t.netloc}/")
        if self._haupt_fehler:
            raise NichtPruefbar(f"Startseite nicht erreichbar, {self._haupt_fehler}")
        return self._haupt

    @property
    def eigene_hosts(self) -> set:
        menge = set()
        for h in (self.zielhost, host(self.hauptadresse)):
            menge |= {h, ohne_www(h), mit_www(ohne_www(h))}
        menge |= {h.lower() for h in self.einstellungen.get("eigene_hosts", [])}
        return menge

    def erfassung(self):
        if self._erfassung is None:
            from .erfassung import erfassen
            haupt = self.hauptadresse
            print(f"Erfasse Seiten ab {haupt} (höchstens {self.max_seiten})", file=sys.stderr)
            self._erfassung = erfassen(self)
        return self._erfassung

    def browser(self) -> dict:
        """Browserdaten je Endadresse."""
        if self._browser_fehler:
            raise NichtPruefbar(self._browser_fehler)
        if self._browser is None:
            urls = [s.endadresse for s in self.erfassung().html_seiten()]
            if not urls:
                raise NichtPruefbar("Keine erreichbare HTML-Seite für den Browserlauf.")
            print(f"Browserlauf für {len(urls)} Seiten", file=sys.stderr)
            try:
                daten = browser_erfassen(self, urls)
            except BrowserNichtVerfuegbar as e:
                self._browser_fehler = f"Browserlauf nicht möglich. {e}"
                raise NichtPruefbar(self._browser_fehler)
            self._browser = daten
        return self._browser
