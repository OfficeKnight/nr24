#!/usr/bin/env python3
"""Lokaler Testserver für die Beispielseiten.

Bedient auf 127.0.0.1 die Ports 80 (http) und 443 (https) und unterscheidet nach Hostnamen.

gut.test           Variante mit lauter bestandenen Prüfungen, Modus demo (noindex)
live.test          wie gut.test, aber ohne noindex und mit offener robots.txt, Modus live
schlecht.test      Variante mit absichtlich verletzten Prüfungen
drittanbieter.test fremder Host mit Skript und Cookie, wird von schlecht.test eingebunden

Die Zertifikate erzeugt zertifikate.py. Der Server verlangt Rechte für die Ports 80 und 443.
gut.test, live.test und drittanbieter.test liegen auf 127.0.0.1, schlecht.test auf 127.0.0.2.
"""
from __future__ import annotations

import argparse
import warnings
import hashlib
import mimetypes
import ssl
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

warnings.filterwarnings("ignore", category=DeprecationWarning)  # TLS 1.0 ist hier absichtlich erlaubt
HIER = Path(__file__).resolve().parent
ZERT = HIER / "zertifikate"

HAUPTHOST = {
    "gut.test": "gut", "www.gut.test": "gut",
    "live.test": "live", "www.live.test": "live",
    "schlecht.test": "schlecht", "www.schlecht.test": "schlecht",
    "drittanbieter.test": "dritt",
}
VERZEICHNIS = {"gut": HIER / "gut", "live": HIER / "gut", "schlecht": HIER / "schlecht"}

SICHERHEITSHEADER = {
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    "Content-Security-Policy": ("default-src 'self'; img-src 'self' data:; style-src 'self'; script-src 'self'; "
                                "font-src 'self'; connect-src 'self'; form-action 'self'; base-uri 'self'; "
                                "object-src 'none'; frame-ancestors 'none'"),
    "X-Content-Type-Options": "nosniff",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": "camera=(), microphone=(), geolocation=(), payment=()",
    "X-Frame-Options": "DENY",
}

WEITERLEITUNGEN = {
    "gut": {"/alt/displaykabel.html": ("301", "/ersatzteile/displays/displaykabel-x72/"),
            "/shop/index.php": ("301", "/"),
            "/alt/agb.html": ("301", "/agb/")},
    "live": {"/alt/displaykabel.html": ("301", "/ersatzteile/displays/displaykabel-x72/"),
             "/shop/index.php": ("301", "/"),
             "/alt/agb.html": ("301", "/agb/")},
    "schlecht": {"/alt/displaykabel.html": ("302", "/ersatzteile/displays/kabel/"),
                 "/alt/agb.html": ("301", "/agb/")},
}


def grosse_datei() -> bytes:
    """Ein gültiges Skript mit etwa 600 kB, das der Browser vollständig lädt."""
    block, daten = b"nr24", bytearray(b"/* ")
    while len(daten) < 600_000:
        block = hashlib.sha256(block).digest()
        daten += block.hex().encode()
    return bytes(daten) + b" */\n"


GROSS = grosse_datei()


class Bearbeiter(BaseHTTPRequestHandler):
    server_version = "Beispielserver"
    sys_version = ""
    schema = "http"

    def log_message(self, fmt, *args):  # ruhig bleiben
        pass

    def _host(self) -> str:
        return (self.headers.get("Host") or "").split(":")[0].lower()

    def _senden(self, status: int, kopf: dict, inhalt: bytes = b"", cookies=()):
        self.send_response(status)
        for k, v in kopf.items():
            self.send_header(k, v)
        for c in cookies:
            self.send_header("Set-Cookie", c)
        self.send_header("Content-Length", str(len(inhalt)))
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(inhalt)

    def do_POST(self):
        self._senden(405, {"Content-Type": "text/plain; charset=utf-8"}, "Nur lesende Abrufe".encode())

    def do_HEAD(self):
        self.do_GET()

    def do_GET(self):
        h = self._host()
        variante = HAUPTHOST.get(h)
        pfad = self.path.split("?")[0].split("#")[0]
        if variante is None:
            return self._senden(404, {"Content-Type": "text/plain"}, b"Unbekannter Host")
        if variante == "dritt":
            return self._drittanbieter(pfad)
        haupt = {"gut": "gut.test", "live": "live.test", "schlecht": "schlecht.test"}[variante]

        # Weiterleitungen auf die Hauptadresse
        if variante in ("gut", "live"):
            if self.schema == "http" or h != haupt:
                return self._senden(301, {"Location": f"https://{haupt}{self.path}"})
        else:
            if self.schema == "http":
                return self._senden(302, {"Location": f"https://{h}{self.path}"})
            # www.schlecht.test liefert die Inhalte direkt aus, ohne Weiterleitung

        if pfad in WEITERLEITUNGEN[variante]:
            code, ziel = WEITERLEITUNGEN[variante][pfad]
            return self._senden(int(code), {"Location": f"https://{haupt}{ziel}"})

        kopf = dict(SICHERHEITSHEADER) if variante in ("gut", "live") else {}
        cookies = []
        if variante in ("gut", "live"):
            cookies.append("sitzung=b1a2c3; Path=/; Secure; HttpOnly; SameSite=Lax")
        else:
            cookies.append("sitzung=b1a2c3; Path=/")
            cookies.append("werbung_id=x9y8; Path=/; Max-Age=31536000")

        if variante == "schlecht" and pfad == "/assets/gross.js":
            kopf["Content-Type"] = "application/javascript"
            return self._senden(200, kopf, GROSS, cookies)

        datei = self._datei(VERZEICHNIS[variante], pfad, variante)
        if datei is None:
            fehler = VERZEICHNIS[variante] / "404.html"
            inhalt = fehler.read_bytes() if fehler.exists() else b"<!doctype html><title>Nicht gefunden</title>"
            kopf["Content-Type"] = "text/html; charset=utf-8"
            return self._senden(404, kopf, self._ersetzen(inhalt, haupt, variante), cookies)
        typ = mimetypes.guess_type(datei.name)[0] or "application/octet-stream"
        if typ.startswith("text/") or typ in ("application/javascript", "application/xml", "image/svg+xml"):
            typ += "; charset=utf-8"
        kopf["Content-Type"] = typ
        inhalt = datei.read_bytes()
        if datei.suffix in (".html", ".xml", ".txt"):
            inhalt = self._ersetzen(inhalt, haupt, variante)
        self._senden(200, kopf, inhalt, cookies)

    def _datei(self, wurzel: Path, pfad: str, variante: str) -> Path | None:
        if pfad == "/robots.txt" and variante == "live":
            return wurzel / "robots-live.txt"
        if pfad == "/robots-live.txt":
            return None
        ziel = (wurzel / pfad.lstrip("/")).resolve()
        if wurzel.resolve() not in ziel.parents and ziel != wurzel.resolve():
            return None
        if ziel.is_dir():
            ziel = ziel / "index.html"
        return ziel if ziel.is_file() and ziel.name != "404.html" else None

    @staticmethod
    def _ersetzen(inhalt: bytes, haupt: str, variante: str) -> bytes:
        text = inhalt.decode("utf-8").replace("{{HOST}}", haupt)
        if variante == "live":
            text = text.replace('<meta name="robots" content="noindex, nofollow">\n', "")
        return text.encode("utf-8")

    def _drittanbieter(self, pfad: str):
        if pfad == "/tracker.js":
            js = (b"document.cookie='_verfolgung=1; path=/; max-age=31536000';\n"
                  b"fetch('https://drittanbieter.test/pixel.gif', {credentials: 'include', mode: 'no-cors'});\n")
            return self._senden(200, {"Content-Type": "application/javascript"}, js,
                                ["dritt_id=42; Path=/; Secure; SameSite=None; Max-Age=31536000"])
        if pfad == "/pixel.gif":
            gif = bytes.fromhex("47494638396101000100800000000000ffffff21f90401000000002c00000000010001000002024401003b")
            return self._senden(200, {"Content-Type": "image/gif"}, gif,
                                ["dritt_id=42; Path=/; Secure; SameSite=None; Max-Age=31536000"])
        return self._senden(404, {"Content-Type": "text/plain"}, b"")


class HttpsBearbeiter(Bearbeiter):
    schema = "https"


class Server(ThreadingHTTPServer):
    def handle_error(self, request, client_address):
        pass  # abgebrochene Handschläge aus der TLS-Prüfung sind hier gewollt


def kontext(namen: list, alt: bool) -> ssl.SSLContext:
    """Ein Kontext je Sicherheitsstufe. Das Zertifikat wird per SNI gewählt."""
    def neu(name: str) -> ssl.SSLContext:
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ctx.load_cert_chain(ZERT / f"{name}.crt", ZERT / f"{name}.key")
        if alt:
            ctx.set_ciphers("ALL:@SECLEVEL=0")
            ctx.minimum_version = ssl.TLSVersion.TLSv1
        else:
            ctx.minimum_version = ssl.TLSVersion.TLSv1_2
        return ctx

    je_host = {}
    for name in namen:
        c = neu(name)
        je_host[f"{name}.test"] = c
        je_host[f"www.{name}.test"] = c

    def sni(sock, servername, _ctx):
        if servername in je_host:
            sock.context = je_host[servername]

    haupt = neu(namen[0])
    haupt.sni_callback = sni
    return haupt


def starten(adresse: str, http_port: int, https_port: int, ctx: ssl.SSLContext) -> None:
    http = Server((adresse, http_port), Bearbeiter)
    https = Server((adresse, https_port), HttpsBearbeiter)
    https.socket = ctx.wrap_socket(https.socket, server_side=True)
    threading.Thread(target=http.serve_forever, daemon=True).start()
    threading.Thread(target=https.serve_forever, daemon=True).start()


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--adresse-modern", default="127.0.0.1",
                   help="Adresse für gut.test, live.test und drittanbieter.test")
    p.add_argument("--adresse-alt", default="127.0.0.2", help="Adresse für schlecht.test")
    args = p.parse_args()
    # Getrennte Adressen, weil OpenSSL die erlaubten TLS-Versionen vor der SNI-Auswahl festlegt.
    starten(args.adresse_modern, 80, 443, kontext(["gut", "live", "drittanbieter"], alt=False))
    starten(args.adresse_alt, 80, 443, kontext(["schlecht"], alt=True))
    print(f"Beispielserver auf {args.adresse_modern} und {args.adresse_alt}, Ports 80 und 443", flush=True)
    threading.Event().wait()


if __name__ == "__main__":
    main()
