"""Hilfen rund um Adressen und Hostnamen."""
from __future__ import annotations

from urllib.parse import urljoin, urlsplit, urlunsplit


def normalisieren(url: str) -> str:
    """Entfernt Fragment, schreibt Schema und Host klein und ergänzt den Pfad."""
    t = urlsplit(url.strip())
    schema = t.scheme.lower()
    host = (t.hostname or "").lower()
    netz = host
    if t.port and not ((schema == "https" and t.port == 443) or (schema == "http" and t.port == 80)):
        netz = f"{host}:{t.port}"
    pfad = t.path or "/"
    return urlunsplit((schema, netz, pfad, t.query, ""))


def host(url: str) -> str:
    return (urlsplit(url).hostname or "").lower()


def ohne_www(h: str) -> str:
    return h[4:] if h.startswith("www.") else h


def mit_www(h: str) -> str:
    return h if h.startswith("www.") else "www." + h


def absolut(basis: str, href: str) -> str | None:
    href = (href or "").strip()
    if not href or href.startswith(("#", "mailto:", "tel:", "javascript:", "data:", "sms:", "fax:")):
        return None
    ziel = urljoin(basis, href)
    if urlsplit(ziel).scheme not in ("http", "https"):
        return None
    return normalisieren(ziel)


def pfad(url: str) -> str:
    return urlsplit(url).path or "/"
