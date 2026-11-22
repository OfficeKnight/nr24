"""Lesende HTTP-Abrufe mit fester Mindestpause zwischen zwei Anfragen."""
from __future__ import annotations

import re
import time
from dataclasses import dataclass, field
from urllib.parse import urljoin

import requests

BENUTZERAGENT = "nr24-Abnahmepruefung/1.0 (nur lesend, Pause mindestens 1 s)"
MAX_TEXT = 5 * 1024 * 1024


@dataclass
class Antwort:
    url: str
    status: int | None = None
    headers: dict = field(default_factory=dict)
    set_cookies: list = field(default_factory=list)
    text: str = ""
    location: str | None = None
    fehler: str | None = None
    endadresse: str | None = None
    kette: list = field(default_factory=list)

    @property
    def inhaltstyp(self) -> str:
        return self.headers.get("content-type", "").split(";")[0].strip().lower()

    @property
    def ist_html(self) -> bool:
        return self.inhaltstyp in ("text/html", "application/xhtml+xml")


class Abrufer:
    """Führt nur GET und HEAD aus und wartet zwischen zwei Anfragen."""

    def __init__(self, pause: float = 1.0, timeout: float = 20.0, verify=True):
        if pause < 1.0:
            raise ValueError("Die Pause muss mindestens eine Sekunde betragen.")
        self.pause = pause
        self.timeout = timeout
        self.verify = verify
        self.sitzung = requests.Session()
        self.sitzung.headers.update({
            "User-Agent": BENUTZERAGENT,
            "Accept-Language": "de-DE,de;q=0.9",
        })
        self._letzte = 0.0
        self.anzahl = 0

    def _warten(self) -> None:
        rest = self._letzte + self.pause - time.monotonic()
        if rest > 0:
            time.sleep(rest)
        self._letzte = time.monotonic()

    def einzeln(self, url: str, methode: str = "GET", text_lesen: bool = True) -> Antwort:
        """Ein einzelner Abruf ohne Folgen von Weiterleitungen."""
        if methode not in ("GET", "HEAD"):
            raise ValueError("Es sind nur lesende Abrufe erlaubt.")
        self._warten()
        self.anzahl += 1
        a = Antwort(url=url)
        try:
            # Cookies werden nicht weitergegeben, jeder Abruf startet ohne Zustand.
            self.sitzung.cookies.clear()
            r = self.sitzung.request(methode, url, allow_redirects=False, timeout=self.timeout,
                                     verify=self.verify, stream=True)
        except requests.exceptions.SSLError as e:
            a.fehler = f"TLS-Fehler ({_kurz(e)})"
            return a
        except requests.exceptions.ConnectionError as e:
            a.fehler = f"Verbindung fehlgeschlagen ({_kurz(e)})"
            return a
        except requests.exceptions.Timeout:
            a.fehler = "Zeitüberschreitung"
            return a
        except requests.exceptions.RequestException as e:
            a.fehler = f"Abruf fehlgeschlagen ({_kurz(e)})"
            return a
        with r:
            a.status = r.status_code
            a.headers = {k.lower(): v for k, v in r.headers.items()}
            try:
                a.set_cookies = list(r.raw.headers.getlist("Set-Cookie"))
            except AttributeError:
                a.set_cookies = [v for k, v in r.raw.headers.items() if k.lower() == "set-cookie"]
            if "location" in a.headers:
                a.location = urljoin(url, a.headers["location"])
            if text_lesen and methode == "GET" and (a.ist_html or a.inhaltstyp.startswith("text/")
                                                    or "xml" in a.inhaltstyp or "json" in a.inhaltstyp):
                roh = r.raw.read(MAX_TEXT, decode_content=True) or b""
                kodierung = r.encoding or "utf-8"
                if a.ist_html and "charset" not in a.headers.get("content-type", ""):
                    kodierung = "utf-8"
                try:
                    a.text = roh.decode(kodierung, errors="replace")
                except LookupError:
                    a.text = roh.decode("utf-8", errors="replace")
        return a

    def folgen(self, url: str, max_spruenge: int = 10, text_lesen: bool = True) -> Antwort:
        """Folgt Weiterleitungen Schritt für Schritt. kette enthält jeden Sprung."""
        kette = []
        aktuell = url
        for _ in range(max_spruenge + 1):
            a = self.einzeln(aktuell, text_lesen=text_lesen)
            kette.append((aktuell, a.status, a.location, a.fehler))
            if a.fehler or a.status not in (301, 302, 303, 307, 308) or not a.location:
                a.kette = kette
                a.endadresse = aktuell
                a.url = url
                return a
            aktuell = a.location
        a.fehler = "Zu viele Weiterleitungen"
        a.kette = kette
        a.endadresse = aktuell
        a.url = url
        return a


def _kurz(e: Exception) -> str:
    text = str(e)
    for merkmal in ("NameResolutionError", "Name or service not known", "nodename nor servname",
                    "Failed to resolve", "getaddrinfo failed"):
        if merkmal in text:
            return "Name nicht auflösbar"
    m = re.search(r"Tunnel connection failed: (\d+)", text)
    if m:
        return f"Proxy verweigert die Verbindung mit Status {m.group(1)}"
    if "ProxyError" in text:
        return "Proxy verweigert die Verbindung"
    if "Connection refused" in text:
        return "Verbindung abgelehnt"
    if "certificate has expired" in text:
        return "Zertifikat abgelaufen"
    if "Hostname mismatch" in text or "doesn't match" in text:
        return "Zertifikat passt nicht zum Hostnamen"
    if "self-signed" in text or "unable to get local issuer" in text:
        return "Zertifikat nicht vertrauenswürdig"
    if "CERTIFICATE_VERIFY_FAILED" in text:
        return "Zertifikat nicht gültig"
    if "timed out" in text.lower():
        return "Zeitüberschreitung"
    return text[:200].replace(": ", " ")
