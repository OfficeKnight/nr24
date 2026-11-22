"""Netzwerkhilfen für feste Namensauflösung, Proxyerkennung und zusätzliche Zertifizierungsstelle."""
from __future__ import annotations

import atexit
import os
import socket
import ssl
import tempfile
from urllib.parse import urlsplit

import requests

_AUFLOESEN: dict[str, str] = {}
_ORIGINAL_GETADDRINFO = socket.getaddrinfo


def _getaddrinfo(host, *args, **kwargs):
    if isinstance(host, str) and host.lower() in _AUFLOESEN:
        host = _AUFLOESEN[host.lower()]
    return _ORIGINAL_GETADDRINFO(host, *args, **kwargs)


def aufloesen_setzen(zuordnung: dict[str, str]) -> None:
    """Leitet Hostnamen fest auf Adressen um (wie curl --resolve).

    Für diese Hosts wird außerdem kein Proxy verwendet, damit die Anfrage
    wirklich beim angegebenen Server ankommt.
    """
    if not zuordnung:
        return
    _AUFLOESEN.update({k.lower(): v for k, v in zuordnung.items()})
    socket.getaddrinfo = _getaddrinfo
    for name in ("NO_PROXY", "no_proxy"):
        alt = os.environ.get(name, "")
        teile = [t for t in alt.split(",") if t]
        teile += [h for h in _AUFLOESEN if h not in teile]
        os.environ[name] = ",".join(teile)


def aufloesung() -> dict[str, str]:
    return dict(_AUFLOESEN)


def ueber_proxy(url: str) -> str | None:
    """Gibt den Proxy zurück, über den requests diese Adresse abrufen würde."""
    if requests.utils.should_bypass_proxies(url, no_proxy=None):
        return None
    proxys = requests.utils.get_environ_proxies(url)
    schema = urlsplit(url).scheme
    return proxys.get(schema) or proxys.get("all")


def ca_buendel(zusatz: str | None) -> str | bool:
    """Liefert den Wert für requests verify. Mit Zusatzdatei entsteht ein
    temporäres Bündel aus Systemzertifikaten und Zusatz, das beim Beenden
    gelöscht wird."""
    if not zusatz:
        return True
    basis = (os.environ.get("REQUESTS_CA_BUNDLE") or os.environ.get("SSL_CERT_FILE")
             or ssl.get_default_verify_paths().cafile)
    if not basis or not os.path.exists(basis):
        import certifi
        basis = certifi.where()
    fd, pfad = tempfile.mkstemp(prefix="abnahme-ca-", suffix=".pem")
    with os.fdopen(fd, "w", encoding="utf-8") as aus:
        with open(basis, encoding="utf-8") as ein:
            aus.write(ein.read())
        aus.write("\n")
        with open(zusatz, encoding="utf-8") as ein:
            aus.write(ein.read())
    atexit.register(lambda: os.path.exists(pfad) and os.remove(pfad))
    return pfad
