"""Prüfung 2. TLS-Versionen und Restlaufzeit des Zertifikats."""
if __name__ == "__main__":
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    import lib.start  # noqa: F401

import socket
import ssl
import time

from lib.adressen import host, mit_www, ohne_www
from lib.kern import Beleg, Ergebnis
from lib.netz import ueber_proxy

NUMMER = 2
TITEL = "TLS"

VERSIONEN = [
    ("TLS 1.0", "TLSv1", False),
    ("TLS 1.1", "TLSv1_1", False),
    ("TLS 1.2", "TLSv1_2", True),
    ("TLS 1.3", "TLSv1_3", True),
]
CLIENTSEITIG = ("NO_PROTOCOLS_AVAILABLE", "NO_CIPHERS_AVAILABLE", "NO_SUITABLE_SIGNATURE_ALGORITHM")


def _handshake(h: str, port: int, version_name: str):
    """Gibt (angenommen, text, clientseitig_unmöglich) zurück. angenommen ist None, wenn unklar."""
    version = getattr(ssl.TLSVersion, version_name)
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    try:
        ctx.set_ciphers("ALL:@SECLEVEL=0")
    except ssl.SSLError:
        pass
    try:
        ctx.minimum_version = version
        ctx.maximum_version = version
    except (ValueError, ssl.SSLError) as e:
        return None, f"Prüfrechner kann diese Version nicht anbieten ({e})", True
    try:
        with socket.create_connection((h, port), timeout=10) as sock:
            with ctx.wrap_socket(sock, server_hostname=h) as s:
                return True, f"Handschlag mit {s.version()} und {s.cipher()[0]}", False
    except ssl.SSLError as e:
        grund = getattr(e, "reason", None) or str(e)
        if any(c in str(grund) for c in CLIENTSEITIG):
            return None, f"Prüfrechner kann diese Version nicht anbieten ({grund})", True
        return False, f"Abgelehnt ({grund})", False
    except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError) as e:
        return False, f"Abgelehnt, Verbindung getrennt ({type(e).__name__})", False
    except OSError as e:
        return None, f"Keine Verbindung ({e})", False


def _zertifikat(h: str, port: int, cafile: str | None):
    ctx = ssl.create_default_context(cafile=cafile) if cafile else ssl.create_default_context()
    with socket.create_connection((h, port), timeout=10) as sock:
        with ctx.wrap_socket(sock, server_hostname=h) as s:
            return s.getpeercert()


def pruefen(k) -> Ergebnis:
    erg = Ergebnis(NUMMER, TITEL)
    try:
        haupt = k.hauptadresse
        h = host(haupt)
    except Exception:  # noqa: BLE001
        h = k.zielhost
        haupt = f"https://{h}/"
    port = 443
    proxy = ueber_proxy(f"https://{h}/")
    if proxy:
        grund = (f"Ausgehende Verbindungen laufen über den Proxy {proxy}. Ein Proxy kann TLS neu aufbauen, "
                 "dann würde der Proxy statt des Servers geprüft. Bitte ohne Proxy ausführen.")
        erg.nicht_pruefbar("Nur TLS 1.2 und 1.3 werden angenommen", haupt, "Verbindung", grund)
        erg.nicht_pruefbar("Zertifikat gilt noch mindestens 30 Tage", haupt, "Verbindung", grund)
        return erg

    # 2a Versionen
    fehler, ok, unpruefbar = [], [], []
    angenommen_modern = []
    for anzeige, name, erlaubt in VERSIONEN:
        fund = f"{h}:{port} {anzeige}"
        angenommen, text, clientseitig = _handshake(h, port, name)
        if angenommen is None:
            unpruefbar.append(Beleg(haupt, fund, text))
            continue
        if erlaubt:
            if angenommen:
                angenommen_modern.append(anzeige)
                ok.append(Beleg(haupt, fund, f"Angenommen. {text}"))
            else:
                ok.append(Beleg(haupt, fund, f"Nicht angeboten. {text}"))
        elif angenommen:
            fehler.append(Beleg(haupt, fund, f"Veraltete Version wird angenommen. {text}"))
        else:
            ok.append(Beleg(haupt, fund, text))
    if not angenommen_modern and not unpruefbar:
        fehler.append(Beleg(haupt, f"{h}:{port}", "Weder TLS 1.2 noch TLS 1.3 wird angenommen"))
    hinweise = []
    if angenommen_modern == ["TLS 1.2"]:
        hinweise.append(Beleg(haupt, f"{h}:{port}", "TLS 1.3 wird nicht angeboten"))
    erg.bewerten("Nur TLS 1.2 und 1.3 werden angenommen", fehler, ok, hinweise, unpruefbar)

    # 2b Zertifikat
    mindesttage = int(k.einstellungen.get("zertifikat_mindesttage", 30))
    fehler, ok, unpruefbar = [], [], []
    namen = [h]
    anderer = mit_www(h) if not h.startswith("www.") else ohne_www(h)
    try:
        socket.getaddrinfo(anderer, port)
        namen.append(anderer)
    except OSError:
        pass
    for name in namen:
        adresse = f"https://{name}/"
        try:
            zert = _zertifikat(name, port, k.verify if isinstance(k.verify, str) else None)
        except ssl.SSLCertVerificationError as e:
            fehler.append(Beleg(adresse, f"Zertifikat {name}", f"Prüfung fehlgeschlagen ({e.verify_message})"))
            continue
        except (ssl.SSLError, OSError) as e:
            unpruefbar.append(Beleg(adresse, f"Zertifikat {name}", f"Keine Verbindung ({e})"))
            continue
        ende = ssl.cert_time_to_seconds(zert["notAfter"])
        tage = (ende - time.time()) / 86400
        aussteller = dict(x[0] for x in zert.get("issuer", ())).get("organizationName") or \
            dict(x[0] for x in zert.get("issuer", ())).get("commonName", "unbekannt")
        text = f"Gültig bis {zert['notAfter']}, noch {tage:.0f} Tage, ausgestellt von {aussteller}"
        if tage < mindesttage:
            fehler.append(Beleg(adresse, f"Zertifikat {name}", f"{text}, weniger als {mindesttage} Tage"))
        else:
            ok.append(Beleg(adresse, f"Zertifikat {name}", text))
    erg.bewerten(f"Zertifikat gilt noch mindestens {mindesttage} Tage", fehler, ok, None, unpruefbar)
    return erg


if __name__ == "__main__":
    from lib.ablauf import einzeln
    einzeln(sys.modules[__name__])
