"""TXT-Abfragen über den Systemresolver, einen festen Nameserver oder DNS über HTTPS."""
from __future__ import annotations

from dataclasses import dataclass, field

import dns.exception
import dns.resolver
import requests

OK = "ok"
NXDOMAIN = "nxdomain"
KEINE_ANTWORT = "keine antwort"
FEHLER = "fehler"


@dataclass
class TxtAntwort:
    name: str
    zustand: str
    eintraege: list = field(default_factory=list)
    fehler: str = ""
    quelle: str = ""


class Resolver:
    def __init__(self, server: str | None = None, doh: str | None = None, verify=True):
        self.doh = doh
        self.verify = verify
        self.server = server
        if doh:
            self.beschreibung = f"DNS über HTTPS ({doh})"
        elif server:
            self.beschreibung = f"Nameserver {server}"
        else:
            self.beschreibung = "Systemresolver"
        self._r = dns.resolver.Resolver(configure=not server)
        if server:
            ip, _, port = server.partition(":") if server.count(":") == 1 else (server, "", "")
            self._r.nameservers = [ip]
            if port:
                self._r.port = int(port)
        self._r.lifetime = 8.0

    def txt(self, name: str) -> TxtAntwort:
        if self.doh:
            return self._txt_doh(name)
        try:
            antwort = self._r.resolve(name, "TXT")
        except dns.resolver.NXDOMAIN:
            return TxtAntwort(name, NXDOMAIN, quelle=self.beschreibung)
        except dns.resolver.NoAnswer:
            return TxtAntwort(name, KEINE_ANTWORT, quelle=self.beschreibung)
        except (dns.resolver.NoNameservers, dns.exception.Timeout) as e:
            return TxtAntwort(name, FEHLER, fehler=type(e).__name__, quelle=self.beschreibung)
        eintraege = []
        for r in antwort:
            eintraege.append(b"".join(r.strings).decode("utf-8", errors="replace"))
        return TxtAntwort(name, OK, eintraege, quelle=self.beschreibung)

    def _txt_doh(self, name: str) -> TxtAntwort:
        try:
            r = requests.get(self.doh, params={"name": name, "type": "TXT"},
                             headers={"Accept": "application/dns-json"}, timeout=10, verify=self.verify)
            daten = r.json()
        except (requests.RequestException, ValueError) as e:
            return TxtAntwort(name, FEHLER, fehler=str(e)[:150], quelle=self.beschreibung)
        status = daten.get("Status")
        if status == 3:
            return TxtAntwort(name, NXDOMAIN, quelle=self.beschreibung)
        if status != 0:
            return TxtAntwort(name, FEHLER, fehler=f"DNS-Status {status}", quelle=self.beschreibung)
        eintraege = []
        for a in daten.get("Answer", []):
            if a.get("type") == 16:
                eintraege.append(_txt_zusammensetzen(a.get("data", "")))
        if not eintraege:
            return TxtAntwort(name, KEINE_ANTWORT, quelle=self.beschreibung)
        return TxtAntwort(name, OK, eintraege, quelle=self.beschreibung)


def _txt_zusammensetzen(daten: str) -> str:
    """DoH liefert lange TXT-Einträge teils als mehrere Zeichenketten in Anführungszeichen."""
    d = daten.strip()
    if d.startswith('"'):
        teile, aktuell, innen, i = [], "", False, 0
        while i < len(d):
            z = d[i]
            if z == "\\" and i + 1 < len(d):
                aktuell += d[i + 1]
                i += 2
                continue
            if z == '"':
                if innen:
                    teile.append(aktuell)
                    aktuell = ""
                innen = not innen
            elif innen:
                aktuell += z
            i += 1
        return "".join(teile)
    return d
