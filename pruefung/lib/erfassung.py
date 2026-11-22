"""Erfasst die Seiten des Ziels. Breitensuche über interne Links und die Sitemap."""
from __future__ import annotations

import re
import sys
import xml.etree.ElementTree as ET
from collections import deque
from dataclasses import dataclass, field
from functools import cached_property

from bs4 import BeautifulSoup

from .abruf import Antwort
from .adressen import absolut, host, normalisieren

SITEMAP_NS = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
DATEIENDUNGEN_OHNE_TEXT = re.compile(
    r"\.(pdf|zip|jpe?g|png|gif|webp|avif|svg|ico|mp4|webm|mp3|woff2?|ttf|otf|css|js|xml|txt)$", re.I)


@dataclass
class Seite:
    url: str
    antwort: Antwort

    @property
    def endadresse(self) -> str:
        return normalisieren(self.antwort.endadresse or self.url)

    @property
    def ok(self) -> bool:
        return self.antwort.status == 200 and not self.antwort.fehler

    @cached_property
    def soup(self) -> BeautifulSoup:
        return BeautifulSoup(self.antwort.text or "", "html.parser")


@dataclass
class Erfassung:
    hauptadresse: str
    eigene_hosts: set
    seiten: dict = field(default_factory=dict)
    links: list = field(default_factory=list)          # (quelle, href, ziel)
    nicht_geprueft: list = field(default_factory=list)
    ausgeschlossen: list = field(default_factory=list)  # (ziel, quelle)
    robots: Antwort | None = None
    sitemaps: list = field(default_factory=list)
    sitemap_urls: list = field(default_factory=list)
    sitemap_fehler: list = field(default_factory=list)  # (adresse, text)

    def intern(self, url: str) -> bool:
        return host(url) in self.eigene_hosts

    def html_seiten(self) -> list:
        """Alle erreichbaren HTML-Seiten auf eigenen Hosts, je Endadresse einmal."""
        gesehen, liste = set(), []
        for s in self.seiten.values():
            if s.ok and s.antwort.ist_html and self.intern(s.endadresse) and s.endadresse not in gesehen:
                gesehen.add(s.endadresse)
                liste.append(s)
        return liste

    def seite_zu(self, url: str) -> Seite | None:
        url = normalisieren(url)
        if url in self.seiten:
            return self.seiten[url]
        for s in self.seiten.values():
            if s.endadresse == url:
                return s
        return None


def _log(text: str) -> None:
    print(text, file=sys.stderr, flush=True)


def erfassen(kontext) -> Erfassung:
    ab = kontext.abrufer
    haupt = kontext.hauptadresse
    eigene = kontext.eigene_hosts
    budget = kontext.max_seiten
    ausschluss = [re.compile(m) for m in kontext.einstellungen.get("ausschliessen", [])]
    e = Erfassung(hauptadresse=haupt, eigene_hosts=eigene)
    verbraucht = 0

    def frei() -> bool:
        return verbraucht < budget

    # robots.txt und Sitemap
    basis = haupt.rstrip("/")
    e.robots = ab.folgen(basis + "/robots.txt")
    verbraucht += 1
    sitemap_adressen = []
    if e.robots.status == 200:
        for zeile in e.robots.text.splitlines():
            if zeile.lower().startswith("sitemap:"):
                sitemap_adressen.append(zeile.split(":", 1)[1].strip())
    if not sitemap_adressen:
        sitemap_adressen = [basis + "/sitemap.xml"]
    warte = deque(sitemap_adressen)
    while warte and len(e.sitemaps) < 6 and frei():
        adr = warte.popleft()
        a = ab.folgen(adr)
        verbraucht += 1
        e.sitemaps.append(a)
        if a.status != 200 or a.fehler:
            e.sitemap_fehler.append((adr, f"Status {a.status or a.fehler}"))
            continue
        try:
            wurzel = ET.fromstring(a.text.encode("utf-8"))
        except ET.ParseError as fehler:
            e.sitemap_fehler.append((adr, f"XML nicht lesbar ({fehler})"))
            continue
        if wurzel.tag == SITEMAP_NS + "sitemapindex":
            for loc in wurzel.iter(SITEMAP_NS + "loc"):
                warte.append((loc.text or "").strip())
        elif wurzel.tag == SITEMAP_NS + "urlset":
            for loc in wurzel.iter(SITEMAP_NS + "loc"):
                if loc.text and loc.text.strip():
                    e.sitemap_urls.append(loc.text.strip())
        else:
            e.sitemap_fehler.append((adr, f"Unbekanntes Wurzelelement {wurzel.tag}"))

    # Seiten
    schlange = deque([haupt])
    geplant = {haupt}
    nach_sitemap = [normalisieren(u) for u in e.sitemap_urls]

    def einplanen(ziel: str, quelle: str | None) -> None:
        if ziel in geplant:
            return
        if any(m.search(ziel) for m in ausschluss):
            e.ausgeschlossen.append((ziel, quelle))
            geplant.add(ziel)
            return
        geplant.add(ziel)
        schlange.append(ziel)

    sitemap_eingeplant = False
    while schlange or not sitemap_eingeplant:
        if not schlange:
            sitemap_eingeplant = True
            for u in nach_sitemap:
                if e.intern(u):
                    einplanen(u, None)
            continue
        url = schlange.popleft()
        if not frei():
            e.nicht_geprueft.append(url)
            continue
        text_lesen = not DATEIENDUNGEN_OHNE_TEXT.search(url)
        a = ab.folgen(url, text_lesen=text_lesen)
        verbraucht += 1
        seite = Seite(url, a)
        e.seiten[url] = seite
        _log(f"  Seite {verbraucht:>3}  {a.status or a.fehler}  {url}")
        ende = seite.endadresse
        geplant.add(ende)
        if seite.ok and a.ist_html and e.intern(ende):
            for tag in seite.soup.find_all(["a", "area"], href=True):
                ziel = absolut(ende, tag["href"])
                if not ziel:
                    continue
                if e.intern(ziel):
                    e.links.append((ende, tag["href"], ziel))
                    einplanen(ziel, ende)
        if len(schlange) == 0 and not sitemap_eingeplant:
            sitemap_eingeplant = True
            for u in nach_sitemap:
                if e.intern(u):
                    einplanen(u, None)
    return e
