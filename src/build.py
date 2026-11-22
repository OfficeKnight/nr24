#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build der Demo-Seite „Notebook Reparatur 24“.

Aufruf aus der Repo-Wurzel:

    python3 src/build.py
    python3 src/build.py --artikel PFAD/artikel.json --seite PFAD/seite.json   (mit Stub-Daten)

Der Build liest
  - src/daten/artikel.json   (Kategorien und Artikel)
  - src/daten/seite.json     (alle Texte der Seiten)
  - src/daten/bilder-*.json  (Bild-Manifeste)
  - src/inhalte/*.html       (Rechtstexte als HTML-Fragmente)
  - src/vorlagen/*.html      (Vorlagen)
und schreibt alle Seiten als statisches HTML in die Repo-Wurzel, dazu
assets/js/daten.js, sitemap.xml und 404.html.

Nur Python-Standardbibliothek, lauffähig ab Python 3.9.

Vorlagensyntax (bewusst klein gehalten, Schleifen laufen in Python):
  {{ pfad.zum.wert }}        Wert, HTML-escaped
  {{{ pfad.zum.wert }}}      Wert roh (für fertig erzeugtes HTML)
  {% if pfad %} … {% else %} … {% endif %}   Bedingung, auch {% if not pfad %}
  {% include name %}         bindet src/vorlagen/name.html mit denselben Daten ein
  {# Kommentar #}            wird entfernt
"""

import argparse
import base64
import hashlib
import html
import json
import re
import sys
import unicodedata
from pathlib import Path
from urllib.parse import quote

# ---------------------------------------------------------------------------
# Grundeinstellungen
# ---------------------------------------------------------------------------

WURZEL = Path(__file__).resolve().parent.parent
SRC = WURZEL / "src"
VORLAGEN = SRC / "vorlagen"
LISTE_ERZEUGT = SRC / "erzeugte-dateien.txt"

SHOPNAME = "Notebook Reparatur 24"
MWST = 19

# Dateien anderer Pakete. Fehlen sie, ist das mit --nachsichtig nur eine Warnung.
FREMDE_DATEIEN = (
    "assets/css/schriften.css",
    "assets/css/themen.css",
    "assets/js/demo.js",
    "assets/js/shop.js",
)

# Inhaltssicherheitsrichtlinie laut Bauplan Abschnitt 7.
CSP = ("default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; "
       "script-src 'self'{extra}; font-src 'self'; connect-src 'self'; form-action 'self'; "
       "base-uri 'self'; object-src 'none'")

# Kleines Skript für 404.html. GitHub Pages liefert die Fehlerseite unter jeder
# beliebigen Adresse aus. Das Skript setzt deshalb ein <base>, das auf die Wurzel
# zeigt (auch unter /nr24/), damit alle relativen Pfade stimmen.
SKRIPT_404 = ("(function(){var p=location.pathname;"
              "var r=/^\\/nr24(\\/|$)/.test(p)?'/nr24/':'/';"
              "var b=document.createElement('base');b.href=r;"
              "document.head.appendChild(b);})();")

# sizes der Produktkarten. Unter 600 px ist das Kartenbild 104 px breit (style.css .produkt),
# ab 600 px liegt es im Raster mit Spalten ab 230 px. shop.js nutzt denselben Wert.
KARTEN_SIZES = "(min-width: 1024px) 280px, (min-width: 600px) 45vw, 104px"

WARNUNGEN = []
FEHLER = []


def warnung(text):
    WARNUNGEN.append(text)


def fehler(text):
    FEHLER.append(text)


# ---------------------------------------------------------------------------
# Hilfsfunktionen für Text und Zahlen
# ---------------------------------------------------------------------------

def esc(wert):
    """HTML-escapen (auch Anführungszeichen, damit es in Attributen sicher ist)."""
    if wert is None:
        return ""
    return html.escape(str(wert), quote=True)


def preis_text(betrag):
    """189.0 -> '189,00 €' mit geschütztem Leerzeichen, deutsches Format."""
    ganz = f"{float(betrag):,.2f}"            # 1,234.50
    ganz = ganz.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{ganz} €"


def preis_attr(betrag):
    """Preis für data-preis, immer mit Punkt und zwei Stellen."""
    return f"{float(betrag):.2f}"


def ohne_tags(text):
    """Entfernt HTML-Tags und fasst Leerraum zusammen (für JSON-LD und Beschreibungen)."""
    text = re.sub(r"<[^>]+>", " ", text or "")
    text = html.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def wert_slug(name):
    """'Anderer Hersteller' -> 'anderer', 'HP' -> 'hp' (Wert der Hersteller-Radios)."""
    erstes = (name or "").split()[0] if name else ""
    erstes = erstes.lower()
    for alt, neu in (("ä", "ae"), ("ö", "oe"), ("ü", "ue"), ("ß", "ss")):
        erstes = erstes.replace(alt, neu)
    return re.sub(r"[^a-z0-9]", "", erstes)


def kuerzen(text, laenge):
    """Kürzt an einer Wortgrenze, ohne Auslassungszeichen."""
    if len(text) <= laenge:
        return text
    stueck = text[:laenge + 1].rsplit(" ", 1)[0]
    return stueck.rstrip(",;. ") + "."


def seitentitel(title):
    """Seitentitel nach Muster „… | Notebook Reparatur 24“, höchstens 60 Zeichen.

    Passt das Muster nicht in 60 Zeichen (lange Artikelnamen), steht der Name allein,
    notfalls an einer Wortgrenze gekürzt. So bleiben Titel kurz und eindeutig.
    """
    zusatz = f" | {SHOPNAME}"
    if title.endswith(zusatz.strip()) or title.endswith(zusatz):
        return title
    if len(title) + len(zusatz) <= 60:
        return title + zusatz
    if len(title) <= 60:
        return title
    woerter = title[:61].rsplit(" ", 1)[0].split()
    # Nicht hinter einem Füllwort wie „mit“ oder „für“ abschneiden.
    while len(woerter) > 1 and woerter[-1].lower().strip(",;:.") in FUELLWOERTER:
        woerter.pop()
    return " ".join(woerter).rstrip(",;:. ")


FUELLWOERTER = {"mit", "für", "und", "oder", "im", "in", "am", "an", "auf", "aus", "von", "vom", "zum", "zur",
                "der", "die", "das", "den", "dem", "des", "ein", "eine", "einem", "einen", "einer", "bei", "ohne"}


def artikelnummer(a):
    """Sprechende Artikelnummer aus der internen ID, z. B. a18 -> NR24-0018."""
    ziffern = re.sub(r"\D", "", a.get("id", ""))
    return f"NR24-{int(ziffern):04d}" if ziffern else a.get("id", "")


def ist_platzhalter(wert):
    """True, wenn der Wert fehlt oder nur ein Platzhalter in eckigen Klammern ist."""
    return not wert or bool(re.fullmatch(r"\s*\[[^\]]*\]\s*", str(wert)))


def such_norm(wert):
    """Gleiche Normalisierung wie norm() in assets/js/shop.js (für die Trefferprüfung im Build)."""
    s = str(wert or "").lower()
    s = "".join(z for z in unicodedata.normalize("NFD", s) if not unicodedata.combining(z))
    s = s.replace("ß", "ss").replace("ae", "a").replace("oe", "o").replace("ue", "u")
    return re.sub(r"[\s\-\u2010\u2011_]+", "", s)


# ---------------------------------------------------------------------------
# Die kleine Vorlagen-Engine
# ---------------------------------------------------------------------------

TOKEN = re.compile(r"(\{\{\{.*?\}\}\}|\{\{.*?\}\}|\{%.*?%\}|\{#.*?#\})", re.S)


class Vorlagen:
    """Lädt Vorlagen aus src/vorlagen, zerlegt sie einmal und füllt sie mit Daten."""

    def __init__(self, ordner):
        self.ordner = Path(ordner)
        self.cache = {}

    def _baum(self, name):
        if name not in self.cache:
            datei = self.ordner / f"{name}.html"
            if not datei.exists():
                raise SystemExit(f"Vorlage fehlt: {datei}")
            self.cache[name] = self._zerlege(datei.read_text(encoding="utf-8"), name)
        return self.cache[name]

    def _zerlege(self, text, name):
        """Macht aus dem Vorlagentext einen Baum aus Knoten (Text, Wert, Bedingung, Einbindung)."""
        wurzel = []
        stapel = [("wurzel", wurzel, None)]
        for teil in TOKEN.split(text):
            if not teil:
                continue
            ziel = stapel[-1][1]
            if teil.startswith("{#"):
                continue
            if teil.startswith("{{{"):
                ziel.append(("wert", teil[3:-3].strip(), True))
            elif teil.startswith("{{"):
                ziel.append(("wert", teil[2:-2].strip(), False))
            elif teil.startswith("{%"):
                befehl = teil[2:-2].strip().split()
                if not befehl:
                    raise SystemExit(f"Leerer Befehl in Vorlage {name}")
                if befehl[0] == "if":
                    negiert = len(befehl) == 3 and befehl[1] == "not"
                    pfad = befehl[-1]
                    knoten = ["wenn", pfad, negiert, [], []]
                    ziel.append(knoten)
                    stapel.append(("wenn", knoten[3], knoten))
                elif befehl[0] == "else":
                    art, _, knoten = stapel.pop()
                    if art != "wenn":
                        raise SystemExit(f"else ohne if in Vorlage {name}")
                    stapel.append(("sonst", knoten[4], knoten))
                elif befehl[0] == "endif":
                    art, _, _ = stapel.pop()
                    if art not in ("wenn", "sonst"):
                        raise SystemExit(f"endif ohne if in Vorlage {name}")
                elif befehl[0] == "include":
                    ziel.append(("einbinden", befehl[1]))
                else:
                    raise SystemExit(f"Unbekannter Befehl {befehl[0]} in Vorlage {name}")
            else:
                ziel.append(("text", teil))
        if len(stapel) != 1:
            raise SystemExit(f"if ohne endif in Vorlage {name}")
        return wurzel

    @staticmethod
    def wert(daten, pfad, vorlage):
        """Löst 'a.b.c' in verschachtelten Dicts und Listen auf. Fehlt etwas, gibt es eine Warnung."""
        aktuell = daten
        for schluessel in pfad.split("."):
            if isinstance(aktuell, dict) and schluessel in aktuell:
                aktuell = aktuell[schluessel]
            elif isinstance(aktuell, list) and schluessel.isdigit() and int(schluessel) < len(aktuell):
                aktuell = aktuell[int(schluessel)]
            else:
                warnung(f"Vorlage {vorlage}: Wert '{pfad}' fehlt in den Daten")
                return ""
        return aktuell

    def _rendern(self, knoten_liste, daten, name, aus):
        for knoten in knoten_liste:
            art = knoten[0]
            if art == "text":
                aus.append(knoten[1])
            elif art == "wert":
                wert = self.wert(daten, knoten[1], name)
                if wert is None:
                    wert = ""
                aus.append(str(wert) if knoten[2] else esc(wert))
            elif art == "wenn":
                _, pfad, negiert, dann, sonst = knoten
                wert = self._still(daten, pfad)
                bedingung = bool(wert) != negiert
                self._rendern(dann if bedingung else sonst, daten, name, aus)
            elif art == "einbinden":
                self._rendern(self._baum(knoten[1]), daten, knoten[1], aus)

    @staticmethod
    def _still(daten, pfad):
        """Wie wert(), aber ohne Warnung (für Bedingungen)."""
        aktuell = daten
        for schluessel in pfad.split("."):
            if isinstance(aktuell, dict) and schluessel in aktuell:
                aktuell = aktuell[schluessel]
            else:
                return None
        return aktuell

    def fuelle(self, name, daten):
        aus = []
        self._rendern(self._baum(name), daten, name, aus)
        return "".join(aus)


# ---------------------------------------------------------------------------
# Daten laden
# ---------------------------------------------------------------------------

def lade_json(pfad, pflicht=True):
    pfad = Path(pfad)
    if not pfad.exists():
        if pflicht:
            raise SystemExit(f"Datei fehlt: {pfad}  (eventuell mit --artikel/--seite einen Stub angeben)")
        return None
    with pfad.open(encoding="utf-8") as f:
        return json.load(f)


def lade_manifeste():
    """Fasst alle src/daten/bilder-*.json zu einem Wörterbuch zusammen."""
    manifest = {}
    dateien = sorted((SRC / "daten").glob("bilder-*.json"))
    if not dateien:
        warnung("Keine Bild-Manifeste gefunden, Bilder werden als neutrale Rahmen gezeigt")
    for datei in dateien:
        try:
            manifest.update(lade_json(datei))
        except json.JSONDecodeError as e:
            warnung(f"Bild-Manifest {datei.name} ist kein gültiges JSON ({e}), wird übersprungen")
    return manifest


# ---------------------------------------------------------------------------
# Der eigentliche Build
# ---------------------------------------------------------------------------

class Build:
    def __init__(self, artikel_pfad, seite_pfad):
        daten = lade_json(artikel_pfad)
        self.seite = lade_json(seite_pfad)
        self.shop = self.seite["shop"]
        self.basis = self.shop.get("basis_url", "https://nr24.kazas.dev/")
        self.stand = daten.get("stand", "")
        self.kategorien = sorted(daten["kategorien"], key=lambda k: k.get("reihenfolge", 99))
        self.kat_nach_slug = {k["slug"]: k for k in self.kategorien}
        self.artikel = sorted(daten["artikel"], key=lambda a: a.get("rang", 999))
        self.art_nach_id = {a["id"]: a for a in self.artikel}
        # Kategorien ohne Artikel werden laut Bauplan ausgeblendet.
        belegt = {a["kategorie"] for a in self.artikel}
        self.kategorien = [k for k in self.kategorien if k["slug"] in belegt]
        self.manifest = lade_manifeste()
        self.vorlagen = Vorlagen(VORLAGEN)
        self.seiten = []            # alle erzeugten Seiten (für Sitemap und Prüfung)
        self.dateien = {}           # relativer Pfad -> Inhalt
        self.fehlende_bilder = set()
        self.preloads = self.schrift_preloads()

    # ----- Suche (wie shop.js) ----------------------------------------------

    def heuhaufen(self, a):
        kat = self.kat_nach_slug.get(a["kategorie"], {"name": a["kategorie"]})
        teile = [a["name"], a.get("teilenummer"), "|".join(a.get("modelle", [])), a.get("hersteller"),
                 kat["name"], "|".join(a.get("suchbegriffe", []))]
        return "|".join(such_norm(x) for x in teile)

    def treffer(self, anfrage):
        """Anzahl der Suchtreffer für anfrage, nach derselben Regel wie suchen() in shop.js."""
        ganz = such_norm(anfrage)
        woerter = [w for w in str(anfrage or "").split() if such_norm(w)]
        if not ganz or not woerter:
            return 0

        def varianten(w):
            v = [such_norm(w)]
            if "-" in w:
                vorn = such_norm(w.rsplit("-", 1)[0])
                if len(vorn) >= 4:
                    v.append(vorn)
            return v

        anzahl = 0
        for a in self.artikel:
            h = self.heuhaufen(a)
            if ganz in h or all(any(v in h for v in varianten(w)) for w in woerter):
                anzahl += 1
        return anzahl

    # ----- Adressen ---------------------------------------------------------

    @staticmethod
    def artikel_pfad(a):
        return f"ersatzteile/{a['kategorie']}/{a['slug']}/"

    @staticmethod
    def root_fuer(pfad):
        """data-root: './' auf der Startseite, sonst '../' je Ordnerebene."""
        tiefe = pfad.count("/")
        return "./" if tiefe == 0 else "../" * tiefe

    # ----- Schriften --------------------------------------------------------

    def schrift_preloads(self):
        """Sucht in schriften.css die Dateien der Standardschriften (Inter 400, Space Grotesk)."""
        css = WURZEL / "assets/css/schriften.css"
        if not css.exists():
            warnung("assets/css/schriften.css fehlt noch, keine Schrift-Preloads")
            return []
        text = css.read_text(encoding="utf-8")
        gefunden = {}
        for block in re.findall(r"@font-face\s*\{([^}]*)\}", text):
            fam = re.search(r"font-family\s*:\s*['\"]?([^;'\"]+)", block)
            url = re.search(r"url\(\s*['\"]?([^)'\"]+\.woff2)", block)
            if not fam or not url:
                continue
            familie = fam.group(1).strip()
            stil = re.search(r"font-style\s*:\s*([a-z]+)", block)
            if stil and stil.group(1) != "normal":
                continue
            gewicht = re.search(r"font-weight\s*:\s*([0-9 ]+)", block)
            zahlen = [int(z) for z in gewicht.group(1).split()] if gewicht else [400]
            passt_400 = min(zahlen) <= 400 <= max(zahlen)
            ziel = (css.parent / url.group(1)).resolve()
            try:
                rel = ziel.relative_to(WURZEL).as_posix()
            except ValueError:
                continue
            if familie == "Inter" and passt_400 and "Inter" not in gefunden:
                gefunden["Inter"] = rel
            elif familie == "Space Grotesk" and "Space Grotesk" not in gefunden:
                gefunden["Space Grotesk"] = rel
        ergebnis = []
        for familie in ("Inter", "Space Grotesk"):
            rel = gefunden.get(familie)
            if rel and (WURZEL / rel).exists():
                ergebnis.append(rel)
            else:
                warnung(f"Keine Schriftdatei für {familie} in schriften.css gefunden, kein Preload")
        return ergebnis

    # ----- Bilder -----------------------------------------------------------

    def bild_daten(self, schluessel, bevorzugt=800):
        """Liefert src, srcset, w, h für einen Manifest-Schlüssel oder None."""
        eintrag = self.manifest.get(schluessel)
        if not eintrag:
            if schluessel not in self.fehlende_bilder:
                warnung(f"Bild '{schluessel}' steht in keinem Manifest, neutraler Rahmen")
                self.fehlende_bilder.add(schluessel)
            return None
        breiten = []
        for b in sorted(eintrag.get("breiten", [])):
            if (WURZEL / f"assets/bilder/{schluessel}-{b}.webp").exists():
                breiten.append(b)
            elif f"{schluessel}-{b}" not in self.fehlende_bilder:
                warnung(f"Bilddatei assets/bilder/{schluessel}-{b}.webp fehlt")
                self.fehlende_bilder.add(f"{schluessel}-{b}")
        if not breiten:
            return None
        passend = [b for b in breiten if b <= bevorzugt]
        src_breite = max(passend) if passend else min(breiten)
        return {
            "src": f"assets/bilder/{schluessel}-{src_breite}.webp",
            "srcset": ", ".join(f"assets/bilder/{schluessel}-{b}.webp {b}w" for b in breiten),
            "gross": f"assets/bilder/{schluessel}-{max(breiten)}.webp",
            "w": eintrag["w"],
            "h": eintrag["h"],
        }

    def bild(self, root, schluessel, alt, sizes, klasse="", erstes=False, bevorzugt=800, sofort=False):
        """Erzeugt ein vollständiges <img> oder einen neutralen Bildrahmen.

        erstes=True: großes erstes Bild mit fetchpriority="high". sofort=True: ohne lazy, aber ohne Vorrang
        (z. B. die erste Reihe Produktkarten, die beim Laden schon sichtbar ist)."""
        d = self.bild_daten(schluessel, bevorzugt)
        if not d:
            return (f'<span class="bildrahmen {esc(klasse)}" role="img" aria-label="{esc(alt)}">'
                    f'<svg class="ico" aria-hidden="true"><use href="#i-display"></use></svg></span>')
        srcset = ", ".join(root + teil for teil in d["srcset"].split(", "))
        if erstes:
            laden = 'fetchpriority="high" decoding="async"'
        elif sofort:
            laden = 'decoding="async"'
        else:
            laden = 'loading="lazy" decoding="async"'
        klasse_attr = f' class="{esc(klasse)}"' if klasse else ""
        return (f'<img{klasse_attr} src="{root}{d["src"]}" srcset="{srcset}" sizes="{esc(sizes)}" '
                f'width="{d["w"]}" height="{d["h"]}" {laden} alt="{esc(alt)}">')

    # ----- Bausteine --------------------------------------------------------

    def zustand_satz(self, a):
        if a.get("art") == "reparatur":
            return f"{a.get('zustand', 'Dienstleistung')} · " + ("sofort buchbar" if a.get("verfuegbar") else "derzeit nicht buchbar")
        return f"{a.get('zustand', '')} · " + ("sofort lieferbar" if a.get("verfuegbar") else "derzeit nicht lieferbar")

    def produktkarte(self, root, a, ebene="h3", erstes=False, sofort=False):
        """Produktkarte genau nach Markup-Vertrag (Bauplan Abschnitt 8)."""
        bild = a["bilder"][0] if a.get("bilder") else {"datei": "", "alt": a["name"]}
        kat = self.kat_nach_slug.get(a["kategorie"], {"name": a["kategorie"]})
        daten = {
            "root": root,
            "a": a,
            "url": root + self.artikel_pfad(a),
            "ebene": ebene,
            "kategorie_name": kat["name"],
            "preis": preis_text(a["preis"]),
            "preis_attr": preis_attr(a["preis"]),
            "verfuegbar": "1" if a.get("verfuegbar") else "0",
            "zustand_satz": self.zustand_satz(a),
            "bild": self.bild(root, bild["datei"], bild.get("alt", a["name"]),
                              KARTEN_SIZES, "produkt__bild", erstes=erstes, bevorzugt=400, sofort=sofort),
        }
        return self.vorlagen.fuelle("_produktkarte", daten)

    @staticmethod
    def preis_zusatz(a, klasse):
        """Kurzer Zusatz vor dem Preis, z. B. „Diagnose“, wenn der Preis nicht die ganze Reparatur abdeckt."""
        if not a.get("preis_label"):
            return ""
        return f'<span class="{klasse}">{esc(a["preis_label"])}</span> '

    def karten(self, root, liste, ebene="h3", sofort=0):
        """Produktkarten. sofort = Anzahl der ersten Karten, deren Bild ohne lazy geladen wird."""
        return "\n".join(self.produktkarte(root, a, ebene, sofort=i < sofort) for i, a in enumerate(liste))

    def faq_html(self, eintraege):
        teile = []
        for e in eintraege:
            teile.append(self.vorlagen.fuelle("_faq", {"frage": e["frage"], "antwort": e["antwort"]}))
        return "\n".join(teile)

    def faq_jsonld(self, eintraege, pfad):
        return {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "url": self.basis + pfad,
            "mainEntity": [{
                "@type": "Question",
                "name": e["frage"],
                "acceptedAnswer": {"@type": "Answer", "text": ohne_tags(e["antwort"])},
            } for e in eintraege],
        }

    def brotkrumen(self, root, kette):
        """kette = [(Name, Pfad), …], letzter Eintrag ist die aktuelle Seite."""
        if not kette:
            return ""
        teile = [f'<li><a href="{root}">Startseite</a></li>']
        for i, (name, pfad) in enumerate(kette):
            if i == len(kette) - 1:
                teile.append(f'<li><span aria-current="page">{esc(name)}</span></li>')
            else:
                teile.append(f'<li><a href="{root}{pfad}">{esc(name)}</a></li>')
        return ('<nav class="brotkrumen" aria-label="Brotkrumenpfad"><div class="huelle"><ol>'
                + "".join(teile) + "</ol></div></nav>")

    def brotkrumen_jsonld(self, kette):
        eintraege = [("Startseite", "")] + list(kette)
        return {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [{
                "@type": "ListItem", "position": i + 1, "name": name, "item": self.basis + pfad,
            } for i, (name, pfad) in enumerate(eintraege)],
        }

    def navigation(self, root, aktiv):
        """Kategorieleiste. aktiv = Pfad der Seite, für aria-current und Hervorhebung."""
        punkte = [("Alle Ersatzteile", "ersatzteile/")]
        punkte += [(k["name"], f"ersatzteile/{k['slug']}/") for k in self.kategorien]
        service = [("Reparatur-Service", "notebook-reparatur/"), ("Werkstatt", "werkstatt/"),
                   ("Kontakt", "kontakt/")]

        def li(name, pfad, extra=""):
            if aktiv == pfad:
                attr = ' aria-current="page"'
            elif pfad != "ersatzteile/" and aktiv.startswith(pfad) and pfad:
                attr = ' class="ist-aktiv"'
            elif pfad == "ersatzteile/" and aktiv == "ersatzteile/":
                attr = ' aria-current="page"'
            else:
                attr = ""
            return f'<li{extra}><a href="{root}{pfad}"{attr}>{esc(name)}</a></li>'

        teile = [li(n, p) for n, p in punkte]
        teile.append('<li class="kategorieleiste__trenner" aria-hidden="true"></li>')
        teile += [li(n, p, ' class="kategorieleiste__service"') for n, p in service]
        teile.append(f'<li class="kategorieleiste__anfrage"><a class="knopf knopf--primaer knopf--block" '
                     f'href="{root}notebook-reparatur/anfrage/">Reparatur anfragen</a></li>')
        return "\n".join(teile)

    def fuss_daten(self, root):
        kat_links = "".join(f'<li><a href="{root}ersatzteile/{k["slug"]}/">{esc(k["name"])}</a></li>'
                            for k in self.kategorien)
        hersteller_links = "".join(
            f'<li><a href="{root}notebook-reparatur/{h["slug"]}/">{esc(h["name"])}-Reparatur</a></li>'
            for h in self.seite.get("hersteller", []) if self.hat_herstellerseite(h))
        zeiten = "".join(f"<tr><th scope=\"row\">{esc(t)}</th><td>{esc(z)}</td></tr>"
                         for t, z in self.shop.get("oeffnungszeiten", []))
        zahlarten = " · ".join(esc(z["name"]) for z in self.seite.get("zahlarten", []))
        return {"fuss_kategorien": kat_links, "fuss_hersteller": hersteller_links,
                "fuss_zeiten": zeiten, "fuss_zahlarten": zahlarten}

    def hat_herstellerseite(self, h):
        return bool(h.get("seite")) and isinstance(self.seite.get(h["slug"]), dict)

    def hersteller_link(self, root, h):
        """Eigene Seite, sonst Suche. Findet die Suche nichts, führt der Link zur Reparaturanfrage."""
        if self.hat_herstellerseite(h):
            return f"{root}notebook-reparatur/{h['slug']}/"
        if self.treffer(h["name"]):
            return f"{root}suche/?q={quote(h['name'])}"
        return f"{root}notebook-reparatur/anfrage/?hersteller={wert_slug(h['name'])}"

    def kennzahlen_html(self):
        teile = []
        for k in self.seite.get("kennzahlen", []):
            teile.append(
                f'<li class="kennzahl"><svg class="ico" aria-hidden="true"><use href="#{esc(k.get("icon", "i-check"))}"></use></svg>'
                f'<span class="kennzahl__wert">{esc(k["wert"])}</span> <span class="kennzahl__text">{esc(k["text"])}</span></li>')
        return "\n".join(teile)

    def ablauf_html(self):
        teile = []
        for i, s in enumerate(self.seite.get("ablauf", []), start=1):
            teile.append(
                f'<li class="ablauf__schritt"><span class="ablauf__nummer" aria-hidden="true">{i}</span>'
                f'<svg class="ico ablauf__ico" aria-hidden="true"><use href="#{esc(s.get("icon", "i-check"))}"></use></svg>'
                f'<h3 class="ablauf__titel"><span class="sr-only">Schritt {i}. </span>{esc(s["titel"])}</h3>'
                f'<p>{esc(s["text"])}</p></li>')
        return "\n".join(teile)

    def jsonld_html(self, objekte):
        teile = []
        for o in objekte:
            text = json.dumps(o, ensure_ascii=False, indent=1).replace("</", "<\\/")
            teile.append(f'<script type="application/ld+json">\n{text}\n</script>')
        return "\n".join(teile)

    def organisation(self):
        s = self.shop
        return {
            "@type": "ComputerStore",
            "name": s["name"],
            "url": self.basis,
            "logo": self.basis + "favicon.svg",
            "telephone": s.get("telefon_href", ""),
            "email": s.get("email", ""),
            "address": {"@type": "PostalAddress", "streetAddress": s.get("strasse", ""),
                        "postalCode": s.get("plz", ""), "addressLocality": s.get("ort", ""),
                        "addressCountry": "DE"},
        }

    # ----- Seite zusammensetzen --------------------------------------------

    def seite_schreiben(self, pfad, vorlage, daten, title, description, kette=None, jsonld=None,
                        datei=None, ist_404=False, koerper_klasse=""):
        """Füllt Seitenvorlage und base.html und merkt sich das Ergebnis."""
        root = "./" if ist_404 else self.root_fuer(pfad)
        kette = kette or []
        jsonld = list(jsonld or [])
        if kette:
            jsonld.append(self.brotkrumen_jsonld(kette))
        voll_titel = seitentitel(title)
        grund = {
            "root": root,
            "shop": self.shop,
            "seite": self.seite,
            "pfad": pfad,
            "jahr": (self.stand or "2026")[:4],
        }
        grund.update(daten)
        inhalt = self.vorlagen.fuelle(vorlage, grund)
        extra_csp = ""
        skript_404 = ""
        if ist_404:
            digest = hashlib.sha256(SKRIPT_404.encode("utf-8")).digest()
            extra_csp = f" 'sha256-{base64.b64encode(digest).decode('ascii')}'"
            skript_404 = f"<script>{SKRIPT_404}</script>"
        grund.update({
            "inhalt": inhalt,
            "titel_voll": voll_titel,
            "description": description,
            "canonical": self.basis + ("" if ist_404 else pfad),
            "csp": CSP.format(extra=extra_csp),
            "skript_404": skript_404,
            "preloads": "\n".join(f'<link rel="preload" href="{root}{p}" as="font" type="font/woff2" crossorigin>'
                                  for p in self.preloads),
            "jsonld": self.jsonld_html(jsonld),
            "brotkrumen": self.brotkrumen(root, kette),
            "navigation": self.navigation(root, pfad),
            "koerper_klasse": koerper_klasse,
            "ist_404": ist_404,
            "kennzahlen_fuss": self.kennzahlen_html(),
        })
        grund.update(self.fuss_daten(root))
        text = self.vorlagen.fuelle("base", grund)
        text = platzhalter_markieren(text)
        text = re.sub(r"[ \t]+\n", "\n", text)
        ziel = datei or (pfad + "index.html")
        self.dateien[ziel] = text
        self.seiten.append({"pfad": pfad, "datei": ziel, "sitemap": not ist_404})

    # ----- Die einzelnen Seiten --------------------------------------------

    def startseite(self):
        s = self.seite["start"]
        root = "./"
        fest = [self.art_nach_id[i] for i in s.get("festpreise_ids", []) if i in self.art_nach_id]
        for i in s.get("festpreise_ids", []):
            if i not in self.art_nach_id:
                warnung(f"start.festpreise_ids enthält unbekannte ID {i}")
        festpreise = "".join(
            f'<li class="festpreise__eintrag"><a class="festpreise__link" href="{root}{self.artikel_pfad(a)}">'
            f'<span class="festpreise__name">{esc(a["name"])}</span>'
            f'<span class="festpreise__preis preis">{self.preis_zusatz(a, "festpreise__zusatz")}{esc(preis_text(a["preis"]))}</span></a></li>'
            for a in fest)
        kacheln = []
        for k in self.kategorien:
            anzahl = sum(1 for a in self.artikel if a["kategorie"] == k["slug"])
            kacheln.append(
                f'<li class="kachel"><a class="kachel__link" href="{root}ersatzteile/{k["slug"]}/">'
                f'<span class="kachel__bild">{self.bild(root, k.get("bild", ""), k.get("bild_alt", ""), "(min-width: 1024px) 220px, (min-width: 720px) 30vw, 45vw", bevorzugt=400)}</span>'
                f'<span class="kachel__text"><span class="kachel__name">{esc(k["name"])}</span>'
                f'<span class="kachel__kurz">{esc(k.get("kurz", ""))}</span>'
                f'<span class="kachel__anzahl">{anzahl} {"Angebot" if anzahl == 1 else "Angebote"}</span></span></a></li>')
        beliebt = [a for a in self.artikel if a.get("beliebt")][:8]
        hersteller = "".join(
            f'<li><a class="hersteller__link" href="{self.hersteller_link(root, h)}">{esc(h["name"])}</a></li>'
            for h in self.seite.get("hersteller", []))
        schnellsuche = "".join(
            f'<li><a href="{root}suche/?q={quote(q)}">{esc(q)}</a></li>'
            for q in s.get("suche_beispiele", ["Nitro 5", "LA-H431P", "iMac A1312", "Legion"]))
        faq = self.seite.get("faq", {}).get("start", [])
        daten = {
            "s": s,
            "festpreise": festpreise,
            "kacheln": "\n".join(kacheln),
            "beliebt": self.karten(root, beliebt, "h3"),
            "kennzahlen": self.kennzahlen_html(),
            "ablauf": self.ablauf_html(),
            "faq": self.faq_html(faq),
            "hersteller": hersteller,
            "schnellsuche": schnellsuche,
            "foto_werkstatt": self.bild(root, "fotos/werkbank", "Arbeitsplatz mit Lötstation und Oszilloskop in unserer Werkstatt",
                                        "(min-width: 1024px) 560px, 100vw", "foto", erstes=False),
        }
        jsonld = [dict({"@context": "https://schema.org"}, **self.organisation())]
        if faq:
            jsonld.append(self.faq_jsonld(faq, ""))
        self.seite_schreiben("", "startseite", daten, s["title"], s["description"], jsonld=jsonld,
                             koerper_klasse="seite-start")

    def katalog(self, kategorie=None):
        """Kategorie-Seite. Ohne kategorie: /ersatzteile/ mit allen Artikeln und Kategorie-Filter."""
        if kategorie:
            pfad = f"ersatzteile/{kategorie['slug']}/"
            liste = [a for a in self.artikel if a["kategorie"] == kategorie["slug"]]
            kopf = {"h1": kategorie["h1"], "einleitung": kategorie.get("einleitung", "")}
            title, description = kategorie["title"], kategorie["description"]
            kette = [("Ersatzteile", "ersatzteile/"), (kategorie["name"], pfad)]
        else:
            e = self.seite["ersatzteile"]
            pfad = "ersatzteile/"
            liste = list(self.artikel)
            kopf = {"h1": e["h1"], "einleitung": e.get("einleitung", "")}
            title, description = e["title"], e["description"]
            kette = [("Ersatzteile", pfad)]
        root = self.root_fuer(pfad)

        def gruppe(name, legende, werte, wert_name=None):
            zaehler = {}
            for w in werte:
                zaehler[w] = zaehler.get(w, 0) + 1
            if len(zaehler) < 2 and name != "kategorie":
                return ""
            zeilen = []
            for w in sorted(zaehler, key=lambda x: (wert_name or {}).get(x, x)):
                anzeige = (wert_name or {}).get(w, w)
                zeilen.append(f'<label class="auswahl auswahl--zeile"><input type="checkbox" name="{name}" value="{esc(w)}">'
                              f'<span>{esc(anzeige)} <span class="filter__anzahl">({zaehler[w]})</span></span></label>')
            return (f'<fieldset class="feld-gruppe"><legend>{esc(legende)}</legend>'
                    + "".join(zeilen) + "</fieldset>")

        filter_html = ""
        if not kategorie:
            namen = {k["slug"]: k["name"] for k in self.kategorien}
            filter_html += gruppe("kategorie", "Kategorie", [a["kategorie"] for a in liste], namen)
        filter_html += gruppe("hersteller", "Hersteller", [a["hersteller"] for a in liste
                                                         if not ist_platzhalter(a.get("hersteller"))])
        filter_html += gruppe("zustand", "Zustand", [a["zustand"] for a in liste])
        daten = {
            "k": kopf,
            "filter_gruppen": filter_html,
            "anzahl": f"{len(liste)} Artikel",
            "raster": self.karten(root, liste, "h2", sofort=3),
            "preis_max": int(max(a["preis"] for a in liste) + 1) if liste else 0,
            "katalog_klasse": "" if kategorie else " katalog--alle",
        }
        self.seite_schreiben(pfad, "katalog", daten, title, description, kette=kette)

    def produkt_description(self, a):
        """Meta-Description für Produktseiten (120 bis 160 Zeichen) aus den Artikeldaten."""
        if a.get("description"):
            return a["description"]
        kurz = a.get("kurz", a["name"]).rstrip(".") + "."
        teile = [kurz]
        betrag = preis_text(a["preis"]).replace(chr(160), " ")
        steuer = ", differenzbesteuert." if a.get("differenzbesteuert") else " inkl. MwSt."
        if a.get("art") == "reparatur":
            art = a.get("preis_label") or "Festpreis"
            if art.lower() in kurz.lower():
                art = "Preis"
            teile.append(f"{art} {betrag}{steuer}")
            teile.append("Mit 1 Jahr Gewährleistung auf die Reparatur.")
        else:
            zustand = a.get("zustand", "")
            if zustand and zustand.lower() not in kurz.lower():
                teile.append(f"{zustand} für {betrag}{steuer}")
            else:
                teile.append(f"Preis {betrag}{steuer}")
            if zustand != "Neu":
                teile.append("Geprüft von Notebook Reparatur 24.")
        teile.append("Jetzt bei Notebook Reparatur 24 ansehen.")
        text = ""
        for t in teile:
            if len((text + " " + t).strip()) <= 160:
                text = (text + " " + t).strip()
        return text

    def produkt(self, a):
        pfad = self.artikel_pfad(a)
        root = self.root_fuer(pfad)
        kat = self.kat_nach_slug[a["kategorie"]]
        bilder = a.get("bilder") or [{"datei": "", "alt": a["name"]}]
        haupt = self.bild(root, bilder[0]["datei"], bilder[0].get("alt", a["name"]),
                          "(min-width: 1024px) 560px, (min-width: 720px) 50vw, 100vw",
                          "galerie__bild", erstes=True)
        # Bilder, die es nur klein gibt (z. B. 400 px), nicht über ihre Größe hinaus aufziehen.
        groesse = (self.manifest.get(bilder[0]["datei"]) or {}).get("w", 800)
        galerie_klasse = " galerie__haupt--klein" if groesse < 800 else ""
        weitere = "".join(
            f'<li>{self.bild(root, b["datei"], b.get("alt", a["name"]), "(min-width: 1024px) 180px, 30vw", "galerie__klein", bevorzugt=400)}</li>'
            for b in bilder[1:])
        merkmale = "".join(f'<tr><th scope="row">{esc(k)}</th><td>{esc(v)}</td></tr>'
                           for k, v in a.get("merkmale", []))
        modelle = "".join(f"<li>{esc(m)}</li>" for m in a.get("modelle", []))
        aehnlich = [x for x in self.artikel if x["kategorie"] == a["kategorie"] and x["id"] != a["id"]]
        if len(aehnlich) < 4:
            aehnlich += [x for x in self.artikel if x.get("beliebt") and x["id"] != a["id"] and x not in aehnlich]
        aehnlich = aehnlich[:4]
        ist_rep = a.get("art") == "reparatur"
        daten = {
            "a": a,
            "kat": kat,
            "kat_url": f"{root}ersatzteile/{kat['slug']}/",
            "preis": preis_text(a["preis"]),
            "zustand_satz": self.zustand_satz(a),
            "ist_reparatur": ist_rep,
            "lieferzeit_label": "Bearbeitungszeit" if ist_rep else "Lieferzeit",
            "galerie_haupt": haupt,
            "galerie_klasse": galerie_klasse,
            "artikelnummer": artikelnummer(a),
            "galerie_weitere": weitere,
            "merkmale": merkmale,
            "modelle": modelle,
            "aehnlich": self.karten(root, aehnlich, "h3"),
            "kennzahlen": self.kennzahlen_html(),
            "anfrage_url": f"{root}notebook-reparatur/anfrage/?hersteller={wert_slug(a.get('hersteller', ''))}",
        }
        produkt_ld = {
            "@context": "https://schema.org",
            "@type": "Product",
            "name": a["name"],
            "sku": artikelnummer(a),
            "description": ohne_tags(a.get("kurz") or a.get("beschreibung", "")),
            "category": kat["name"],
            "url": self.basis + pfad,
            "offers": {
                "@type": "Offer",
                "price": preis_attr(a["preis"]),
                "priceCurrency": "EUR",
                "availability": "https://schema.org/InStock" if a.get("verfuegbar") else "https://schema.org/OutOfStock",
                "url": self.basis + pfad,
                "seller": {"@type": "Organization", "name": SHOPNAME},
            },
        }
        if a.get("teilenummer"):
            produkt_ld["mpn"] = a["teilenummer"]
        # Marke nur, wenn sie bekannt ist. Ein Platzhalter wie [Hersteller] gehört nicht in strukturierte Daten.
        if not ist_platzhalter(a.get("hersteller")):
            produkt_ld["brand"] = {"@type": "Brand", "name": a["hersteller"]}
        # Dienstleistungen (Reparaturen) gelten als neue Leistung, damit offers vollständig ist.
        zustand = {"Neu": "NewCondition", "Gebraucht": "UsedCondition", "Generalüberholt": "RefurbishedCondition",
                   "Dienstleistung": "NewCondition"}
        if a.get("zustand") in zustand:
            produkt_ld["offers"]["itemCondition"] = "https://schema.org/" + zustand[a["zustand"]]
        bilder_abs = []
        for b in bilder:
            d = self.bild_daten(b["datei"])
            if d:
                bilder_abs.append(self.basis + d["gross"])
        if bilder_abs:
            produkt_ld["image"] = bilder_abs
        kette = [("Ersatzteile", "ersatzteile/"), (kat["name"], f"ersatzteile/{kat['slug']}/"), (a["name"], pfad)]
        self.seite_schreiben(pfad, "produkt", daten, a.get("title", a["name"]), self.produkt_description(a),
                             kette=kette, jsonld=[produkt_ld], koerper_klasse="seite-produkt")

    def preistabelle(self, root, liste):
        zeilen = []
        for a in liste:
            nummer = (f'<span class="teilenummer">{esc(a["teilenummer"])}</span>' if a.get("teilenummer")
                      else '<span class="preistabelle__leer">alle Varianten</span>')
            zeilen.append(
                f'<tr><th scope="row" data-label="Leistung"><a href="{root}{self.artikel_pfad(a)}">{esc(a["name"])}</a></th>'
                f'<td data-label="Hersteller">{esc(a.get("hersteller", ""))}</td>'
                f'<td data-label="Platine">{nummer}</td>'
                f'<td data-label="Preis" class="preistabelle__preis">{self.preis_zusatz(a, "preistabelle__zusatz")}<span class="preis">{esc(preis_text(a["preis"]))}</span></td>'
                f'<td class="preistabelle__aktion"><button class="knopf knopf--zweit knopf--klein" type="button" '
                f'data-wk-add="{esc(a["id"])}">'
                f'<svg class="ico" aria-hidden="true"><use href="#i-korb"></use></svg><span>Buchen</span>'
                f'<span class="sr-only"> {esc(a["name"])}</span></button></td></tr>')
        return "\n".join(zeilen)

    def leistungen_html(self, liste):
        return "\n".join(
            f'<li class="leistung"><svg class="ico leistung__ico" aria-hidden="true"><use href="#{esc(l.get("icon", "i-werkzeug"))}"></use></svg>'
            f'<h3 class="leistung__titel">{esc(l["titel"])}</h3><p>{esc(l["text"])}</p></li>'
            for l in liste)

    def reparatur(self):
        s = self.seite["reparatur"]
        pfad = "notebook-reparatur/"
        root = self.root_fuer(pfad)
        rep = sorted([a for a in self.artikel if a.get("art") == "reparatur"],
                     key=lambda a: (a.get("hersteller", ""), a["preis"], a["name"]))
        faq = self.seite.get("faq", {}).get("reparatur", [])
        hersteller = "".join(
            f'<li><a class="hersteller__link" href="{self.hersteller_link(root, h)}">{esc(h["name"])}</a></li>'
            for h in self.seite.get("hersteller", []))
        daten = {
            "s": s,
            "leistungen": self.leistungen_html(s.get("leistungen", [])),
            "ablauf": self.ablauf_html(),
            "preise": self.preistabelle(root, rep),
            "faq": self.faq_html(faq),
            "kennzahlen": self.kennzahlen_html(),
            "hersteller": hersteller,
            "aufruf_titel": s.get("aufruf_titel", "Ihr Gerät ist nicht in der Liste?"),
            "aufruf_text": s.get("aufruf_text", s.get("preise_hinweis", "")),
            "foto": self.bild(root, "fotos/loeten", "Löten an einer Notebook-Platine in der Werkstatt",
                              "(min-width: 1024px) 520px, 100vw", "foto", erstes=True),
        }
        jsonld = [self.faq_jsonld(faq, pfad)] if faq else []
        self.seite_schreiben(pfad, "reparatur", daten, s["title"], s["description"],
                             kette=[("Reparatur-Service", pfad)], jsonld=jsonld)

    def anfrage(self):
        s = self.seite["anfrage"]
        pfad = "notebook-reparatur/anfrage/"
        hersteller = "\n".join(
            f'<label class="auswahl auswahl--kachel"><input type="radio" name="hersteller" value="{wert_slug(h)}" required>'
            f'<span>{esc(h)}</span></label>' for h in s.get("hersteller", []))
        probleme = "\n".join(
            f'<label class="auswahl auswahl--zeile"><input type="checkbox" name="problem" value="{esc(p)}">'
            f'<span>{esc(p)}</span></label>' for p in s.get("probleme", []))
        daten = {"s": s, "hersteller_radios": hersteller, "problem_boxen": probleme,
                 "kennzahlen": self.kennzahlen_html()}
        self.seite_schreiben(pfad, "anfrage", daten, s["title"], s["description"],
                             kette=[("Reparatur-Service", "notebook-reparatur/"), (s["h1"], pfad)],
                             koerper_klasse="seite-formular")

    def herstellerseite(self, h):
        s = self.seite[h["slug"]]
        pfad = f"notebook-reparatur/{h['slug']}/"
        root = self.root_fuer(pfad)
        passend = [a for a in self.artikel if a.get("hersteller") == h["name"] and a.get("art") == "reparatur"]
        anfrage = f"{root}notebook-reparatur/anfrage/?hersteller={h['slug']}"
        modelle = "".join(
            f'<li><a href="{root}suche/?q={quote(m)}">{esc(m)}</a></li>' if self.treffer(m)
            else f'<li><a href="{anfrage}">{esc(m)} anfragen</a></li>'
            for m in s.get("modelle", []))
        fehler_html = "\n".join(
            f'<li class="fehlerbild"><h3 class="fehlerbild__titel">{esc(f["titel"])}</h3><p>{esc(f["text"])}</p></li>'
            for f in s.get("fehlerbilder", []))
        abschnitte = "\n".join(
            f'<section class="abschnitt-text"><h2>{esc(x["titel"])}</h2>{x["html"]}</section>'
            for x in s.get("abschnitte", []))
        faq = self.seite.get("faq", {}).get(h["slug"], [])
        daten = {
            "s": s, "h": h,
            "modelle": modelle,
            "fehlerbilder": fehler_html,
            "abschnitte": abschnitte,
            "karten": self.karten(root, passend, "h3"),
            "faq": self.faq_html(faq),
            "anfrage_url": f"{root}notebook-reparatur/anfrage/?hersteller={h['slug']}",
            "foto": self.bild(root, "fotos/notebook-offen", f"Geöffnetes Notebook auf der Werkbank",
                              "(min-width: 1024px) 480px, 100vw", "foto", erstes=True),
        }
        jsonld = [self.faq_jsonld(faq, pfad)] if faq else []
        self.seite_schreiben(pfad, "hersteller", daten, s["title"], s["description"],
                             kette=[("Reparatur-Service", "notebook-reparatur/"), (s["h1"], pfad)], jsonld=jsonld)

    def einfache_seite(self, pfad, vorlage, schluessel, kette_name=None, extra=None, klasse=""):
        s = self.seite[schluessel]
        daten = {"s": s}
        daten.update(extra or {})
        self.seite_schreiben(pfad, vorlage, daten, s["title"], s["description"],
                             kette=[(kette_name or s["h1"], pfad)], koerper_klasse=klasse)

    def kasse(self):
        root = self.root_fuer("kasse/")
        versand = "\n".join(
            f'<label class="auswahl auswahl--option"><input type="radio" name="versand" value="{esc(v["id"])}" required'
            f'{" checked" if i == 0 else ""}><span class="auswahl__inhalt"><span class="auswahl__titel">{esc(v["name"])}</span>'
            f'<span class="auswahl__text">{esc(v.get("text", ""))}</span></span>'
            f'<span class="auswahl__preis preis">{esc(preis_text(v.get("preis", 0)))}</span></label>'
            for i, v in enumerate(self.seite.get("versand", [])))
        versand_namen = {v["id"]: v["name"] for v in self.seite.get("versand", [])}

        def bedingung(z):
            nur = z.get("nur_versand")
            if not nur:
                return ""
            if nur not in versand_namen:
                fehler(f"seite.json: Zahlart {z['id']} verweist auf unbekannte Versandart {nur}")
                return ""
            meldung = (f"{z['name']} ist nur mit der Versandart {versand_namen[nur]} möglich. Bitte wählen Sie eine "
                       f"andere Zahlart oder ändern Sie im Schritt Versand die Versandart.")
            return f' data-nur-versand="{esc(nur)}" data-kombi-fehler="{esc(meldung)}"'

        zahlung = "\n".join(
            f'<label class="auswahl auswahl--option"><input type="radio" name="zahlung" value="{esc(z["id"])}" required'
            f'{bedingung(z)}{" checked" if i == 0 else ""}><span class="auswahl__inhalt"><span class="auswahl__titel">{esc(z["name"])}</span>'
            f'<span class="auswahl__text">{esc(z.get("text", ""))}</span></span>'
            + (f'<span class="auswahl__preis preis">+ {esc(preis_text(z["preis"]))}</span>' if z.get("preis") else "")
            + '</label>'
            for i, z in enumerate(self.seite.get("zahlarten", [])))
        self.einfache_seite("kasse/", "kasse", "kasse",
                            extra={"versand_radios": versand, "zahlung_radios": zahlung}, klasse="seite-formular")

    def kontakt(self):
        betreffe = "".join(f'<option value="{esc(b)}">{esc(b)}</option>'
                           for b in self.seite["kontakt"].get("betreffe", []))
        zeiten = "".join(f'<tr><th scope="row">{esc(t)}</th><td>{esc(z)}</td></tr>'
                         for t, z in self.shop.get("oeffnungszeiten", []))
        self.einfache_seite("kontakt/", "kontakt", "kontakt",
                            extra={"betreffe": betreffe, "zeiten": zeiten}, klasse="seite-formular")

    def werkstatt(self):
        root = self.root_fuer("werkstatt/")
        s = self.seite["werkstatt"]
        # fotos/werkbank ist dem Titelbild vorbehalten, damit kein Foto doppelt untereinander steht.
        fotos = ["fotos/notebook-offen", "fotos/messgeraet", "fotos/loeten", "fotos/mainboard"]
        alt = ["Geöffnetes Notebook mit Mainboard, Festplatte und Lüfter", "Messgerät bei der Fehlersuche an einer Platine",
               "Löten an einer Notebook-Platine", "Notebook-Mainboard in Nahaufnahme"]
        abschnitte = []
        for i, x in enumerate(s.get("abschnitte", [])):
            foto = self.bild(root, fotos[i % len(fotos)], alt[i % len(alt)], "(min-width: 1024px) 520px, 100vw", "foto")
            abschnitte.append(
                f'<section class="werkstatt-abschnitt"><div class="werkstatt-abschnitt__bild">{foto}</div>'
                f'<div class="werkstatt-abschnitt__text abschnitt-text"><h2>{esc(x["titel"])}</h2>{x["html"]}</div></section>')
        self.einfache_seite("werkstatt/", "werkstatt", "werkstatt", extra={
            "abschnitte": "\n".join(abschnitte),
            "kennzahlen": self.kennzahlen_html(),
            "foto": self.bild(root, "fotos/werkbank", "Arbeitsplatz mit Werkzeug und Mikroskop in der Werkstatt",
                              "(min-width: 1024px) 1200px, 100vw", "foto", erstes=True, bevorzugt=1600),
        })

    def bildnachweise(self):
        """Seite mit Urheber, Quelle und Lizenz aller Fotos aus bilder-fotos.json."""
        s = self.seite.get("bildnachweise")
        if not s:
            warnung("seite.json: bildnachweise fehlt, Seite wird übersprungen")
            return
        pfad = "bildnachweise/"
        root = self.root_fuer(pfad)
        fotos = [(k, v) for k, v in self.manifest.items() if k.startswith("fotos/")]
        # Fotos mit Namensnennungspflicht zuerst, danach gemeinfreie.
        fotos.sort(key=lambda kv: (not kv[1].get("lizenz", "").startswith("CC BY"), kv[1].get("motiv", kv[0])))
        eintraege = []
        for schluessel, f in fotos:
            for feld in ("motiv", "urheber", "quelle_url", "lizenz", "lizenz_url"):
                if not f.get(feld):
                    fehler(f"bilder-fotos.json: {schluessel} ohne Angabe {feld}")
            titel = f.get("titel")
            plattform = f.get("plattform", "der Quelle")
            name = f"„{titel}“" if titel else f.get("motiv", "")
            quelle_text = f"{name} bei {plattform}" if titel else f"{name} im {plattform}"
            bild = self.bild(root, schluessel, "", "(min-width: 1024px) 360px, (min-width: 600px) 45vw, 100vw",
                             "nachweis__bild", bevorzugt=480)
            eintraege.append(
                f'<li class="nachweis">{bild}<div class="nachweis__text">'
                f'<h3 class="nachweis__titel">{esc(f.get("motiv", ""))}</h3><dl class="nachweis__daten">'
                f'<div><dt>Titel</dt><dd>{esc(name if titel else "ohne Titel")}</dd></div>'
                f'<div><dt>Urheber</dt><dd>{esc(f.get("urheber", ""))}</dd></div>'
                f'<div><dt>Quelle</dt><dd><a href="{esc(f.get("quelle_url", ""))}" rel="noopener nofollow">{esc(quelle_text)}</a></dd></div>'
                f'<div><dt>Lizenz</dt><dd><a href="{esc(f.get("lizenz_url", ""))}" rel="noopener nofollow license">{esc(f.get("lizenz", ""))}'
                f'<span class="sr-only"> Lizenztext für das Foto {esc(name)}</span></a></dd></div>'
                f'</dl></div></li>')
        daten = {"s": s, "nachweise": "\n".join(eintraege)}
        self.seite_schreiben(pfad, "bildnachweise", daten, s["title"], s["description"],
                             kette=[(s["h1"], pfad)], koerper_klasse="seite-recht")

    def rechtsseiten(self):
        reihenfolge = [("impressum", "Impressum"), ("agb", "AGB"), ("widerruf", "Widerrufsbelehrung"),
                       ("datenschutz", "Datenschutz"), ("versand-und-zahlung", "Versand und Zahlung")]
        for slug, kurzname in reihenfolge:
            s = self.seite.get("rechtsseiten", {}).get(slug)
            if not s:
                warnung(f"seite.json: rechtsseiten.{slug} fehlt, Seite wird übersprungen")
                continue
            pfad = f"{slug}/"
            root = self.root_fuer(pfad)
            datei = SRC / "inhalte" / f"{slug}.html"
            if datei.exists():
                fragment = datei.read_text(encoding="utf-8")
            else:
                warnung(f"src/inhalte/{slug}.html fehlt, Platzhaltertext eingesetzt")
                fragment = "<h2>Inhalt</h2><p>[Rechtstext]</p>"
            if re.search(r"<h1[\s>]", fragment):
                fehler(f"src/inhalte/{slug}.html enthält ein h1")
            aktuell = ' aria-current="page"'
            seitennav = "".join(
                f'<li><a href="{root}{x}/"{aktuell if x == slug else ""}>{esc(n)}</a></li>'
                for x, n in reihenfolge if self.seite.get("rechtsseiten", {}).get(x))
            daten = {"s": s, "fragment": fragment, "seitennav": seitennav}
            self.seite_schreiben(pfad, "rechtsseite", daten, s["title"], s["description"],
                                 kette=[(s["h1"], pfad)], koerper_klasse="seite-recht")

    def nicht_gefunden(self):
        s = self.seite["nicht_gefunden"]
        beliebt = [a for a in self.artikel if a.get("beliebt")][:4]
        daten = {"s": s, "karten": self.karten("./", beliebt, "h3")}
        description = s.get("description") or kuerzen(
            s.get("text", "") + " Notebook-Ersatzteile und Reparaturen finden Sie über die Suche und die Kategorien von Notebook Reparatur 24.", 158)
        self.seite_schreiben("", "nicht_gefunden", daten, s["title"], description, datei="404.html", ist_404=True)

    # ----- daten.js und sitemap.xml ----------------------------------------

    def daten_js(self):
        liste = []
        for a in self.artikel:
            kat = self.kat_nach_slug.get(a["kategorie"], {"name": a["kategorie"]})
            b = (a.get("bilder") or [{}])[0]
            d = self.bild_daten(b.get("datei", ""), bevorzugt=400) if b else None
            liste.append({
                "id": a["id"], "name": a["name"], "url": self.artikel_pfad(a),
                "kategorie": a["kategorie"], "kategorie_name": kat["name"],
                "hersteller": a.get("hersteller") or "", "modelle": a.get("modelle", []),
                "teilenummer": a.get("teilenummer"), "preis": float(a["preis"]),
                "zustand": a.get("zustand", ""), "verfuegbar": bool(a.get("verfuegbar")),
                "art": a.get("art", "ware"), "kurz": a.get("kurz", ""), "rang": a.get("rang", 999),
                "differenzbesteuert": bool(a.get("differenzbesteuert")),
                "suchbegriffe": a.get("suchbegriffe", []),
                "bild": ({"src": d["src"], "srcset": d["srcset"], "w": d["w"], "h": d["h"],
                          "alt": b.get("alt", a["name"])} if d else None),
            })
        daten = {"artikel": liste, "versand": self.seite.get("versand", []),
                 "zahlarten": self.seite.get("zahlarten", []), "mwst": MWST}
        text = ("/* Erzeugt von src/build.py. Nicht von Hand bearbeiten. */\n"
                "window.NR24 = " + json.dumps(daten, ensure_ascii=False, indent=1) + ";\n")
        self.dateien["assets/js/daten.js"] = text

    def sitemap(self):
        zeilen = ['<?xml version="1.0" encoding="UTF-8"?>',
                  '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
        for s in self.seiten:
            if s["sitemap"]:
                zeilen.append(f"  <url><loc>{esc(self.basis + s['pfad'])}</loc><lastmod>{esc(self.stand)}</lastmod></url>")
        zeilen.append("</urlset>")
        self.dateien["sitemap.xml"] = "\n".join(zeilen) + "\n"

    # ----- Ablauf -----------------------------------------------------------

    def alles(self):
        self.startseite()
        self.katalog()
        for k in self.kategorien:
            self.katalog(k)
        for a in self.artikel:
            if a["kategorie"] not in self.kat_nach_slug:
                fehler(f"Artikel {a['id']} hat unbekannte Kategorie {a['kategorie']}")
                continue
            self.produkt(a)
        self.reparatur()
        self.anfrage()
        for h in self.seite.get("hersteller", []):
            if self.hat_herstellerseite(h):
                self.herstellerseite(h)
            elif h.get("seite"):
                warnung(f"Hersteller {h['slug']} hat seite=true, aber keinen Abschnitt in seite.json")
        self.einfache_seite("warenkorb/", "warenkorb", "warenkorb")
        self.kasse()
        self.einfache_seite("suche/", "suche", "suche")
        self.kontakt()
        self.werkstatt()
        self.rechtsseiten()
        self.bildnachweise()
        self.nicht_gefunden()
        self.daten_js()
        self.sitemap()


# ---------------------------------------------------------------------------
# Platzhalter [ … ] im sichtbaren Text markieren
# ---------------------------------------------------------------------------

# Bereiche, deren Inhalt kein sichtbarer Fließtext ist oder keine Elemente enthalten darf.
GESCHUETZT = re.compile(r"(<(script|style|title|textarea|option)\b[^>]*>.*?</\2\s*>)", re.S | re.I)
PLATZHALTER = re.compile(r"\[([^\[\]<>]{1,160})\]")


def platzhalter_markieren(text):
    """Umhüllt jedes [ … ] im sichtbaren Text mit <span class="ph">, nicht in Attributen."""
    teile = GESCHUETZT.split(text)
    aus = []
    # re.split mit zwei Gruppen liefert immer Dreiergruppen: Text, geschützter Block, Tagname.
    for i, stueck in enumerate(teile):
        rest = i % 3
        if rest == 0:
            aus.append(_markiere_text(stueck))
        elif rest == 1:
            aus.append(stueck)
    return "".join(aus)


def _markiere_text(text):
    teile = re.split(r"(<[^>]*>)", text)
    in_ph = 0
    for i, teil in enumerate(teile):
        if teil.startswith("<"):
            # Bereits vorhandene .ph-Spans (z. B. aus src/inhalte) nicht doppelt umhüllen.
            if re.match(r'<span\b[^>]*class="[^"]*\bph\b', teil):
                in_ph += 1
            elif teil.startswith("</span") and in_ph:
                in_ph -= 1
            continue
        if not in_ph and "[" in teil:
            teile[i] = PLATZHALTER.sub(r'<span class="ph">[\1]</span>', teil)
    return "".join(teile)


# ---------------------------------------------------------------------------
# Schreiben, Aufräumen, Prüfen
# ---------------------------------------------------------------------------

def schreiben(dateien):
    """Schreibt alle Dateien (nur bei Änderung) und löscht veraltete aus dem letzten Lauf."""
    alt = set()
    if LISTE_ERZEUGT.exists():
        alt = {z.strip() for z in LISTE_ERZEUGT.read_text(encoding="utf-8").splitlines() if z.strip()}
    neu = set(dateien)
    for rel, inhalt in dateien.items():
        ziel = WURZEL / rel
        ziel.parent.mkdir(parents=True, exist_ok=True)
        if not ziel.exists() or ziel.read_text(encoding="utf-8") != inhalt:
            ziel.write_text(inhalt, encoding="utf-8")
    geloescht = 0
    for rel in sorted(alt - neu):
        ziel = (WURZEL / rel).resolve()
        if WURZEL not in ziel.parents or not ziel.is_file():
            continue
        ziel.unlink()
        geloescht += 1
        # Leer gewordene Ordner entfernen (nie die Wurzel selbst).
        ordner = ziel.parent
        while ordner != WURZEL and ordner.is_dir() and not any(ordner.iterdir()):
            ordner.rmdir()
            ordner = ordner.parent
    LISTE_ERZEUGT.write_text("\n".join(sorted(neu)) + "\n", encoding="utf-8")
    return geloescht


# Seiten, auf denen Links zu fremden Seiten erlaubt sind (Quellen und Lizenztexte der Fotos).
EXTERN_ERLAUBT = ("bildnachweise/",)

ATTR_URL = re.compile(r'\s(href|src|srcset|action)="([^"]*)"')
SPRITE_ID = re.compile(r'<symbol\s+id="([^"]+)"')


def pruefen(build, nachsichtig):
    """Eingebaute Prüfung aller erzeugten HTML-Seiten."""
    beschreibungen = {}
    titel = {}
    fehlend = {}     # fehlendes Ziel -> Seiten, die darauf verweisen
    for s in build.seiten:
        rel = s["datei"]
        text = build.dateien[rel]
        ordner = (WURZEL / rel).parent

        # Pflicht im Kopf
        t = re.search(r"<title>(.*?)</title>", text, re.S)
        if not t or not t.group(1).strip():
            fehler(f"{rel}: title fehlt")
        else:
            wert = html.unescape(t.group(1).strip())
            titel.setdefault(wert, []).append(rel)
            if len(wert) > 60:
                warnung(f"{rel}: title hat {len(wert)} Zeichen (empfohlen höchstens 60)")
        d = re.search(r'<meta name="description" content="([^"]*)"', text)
        if not d or not d.group(1).strip():
            fehler(f"{rel}: meta description fehlt")
        else:
            wert = html.unescape(d.group(1))
            beschreibungen.setdefault(wert, []).append(rel)
            if not 120 <= len(wert) <= 160:
                warnung(f"{rel}: description hat {len(wert)} Zeichen (soll 120 bis 160)")
        if not re.search(r'<meta name="robots" content="noindex, nofollow">', text):
            fehler(f"{rel}: noindex fehlt")

        # Genau ein h1
        anzahl_h1 = len(re.findall(r"<h1[\s>]", text))
        if anzahl_h1 != 1:
            fehler(f"{rel}: {anzahl_h1} h1-Elemente statt genau einem")

        # Doppelte IDs
        ids = re.findall(r'\sid="([^"]+)"', text)
        doppelt = {i for i in ids if ids.count(i) > 1}
        if doppelt:
            fehler(f"{rel}: doppelte IDs {', '.join(sorted(doppelt))}")
        sprite = set(SPRITE_ID.findall(text))
        idset = set(ids) | sprite

        # Relative Verweise
        for attr, wert in ATTR_URL.findall(text):
            urls = [teil.strip().split(" ")[0] for teil in wert.split(",")] if attr == "srcset" else [wert]
            for url in urls:
                url = html.unescape(url)
                if url.startswith("#"):
                    if len(url) > 1 and url[1:] not in idset:
                        fehler(f"{rel}: Sprungziel {url} existiert nicht")
                    continue
                if re.match(r"^(mailto:|tel:|data:|javascript:)", url):
                    continue
                if re.match(r"^[a-z]+://", url) or url.startswith("//"):
                    if attr == "href" and url.startswith(build.basis):
                        continue                    # canonical
                    if attr == "href" and s["pfad"] in EXTERN_ERLAUBT and url.startswith("https://"):
                        continue                    # Quellen und Lizenzen, rel wird unten geprüft
                    fehler(f"{rel}: absolute URL {url}")
                    continue
                if url.startswith("/"):
                    fehler(f"{rel}: Pfad beginnt mit / ({url})")
                    continue
                pfad = url.split("#")[0].split("?")[0]
                ziel = (ordner / pfad).resolve() if pfad else ordner
                ziel_rel = None
                try:
                    ziel_rel = ziel.relative_to(WURZEL).as_posix()
                except ValueError:
                    fehler(f"{rel}: {url} zeigt aus dem Repo heraus")
                    continue
                vorhanden = (ziel.is_file() or (ziel.is_dir() and (ziel / "index.html").is_file())
                             or ziel_rel in build.dateien
                             or (ziel_rel.rstrip("/") + "/index.html").lstrip("./") in build.dateien
                             or (ziel_rel == "." and "index.html" in build.dateien))
                if not vorhanden:
                    fehlend.setdefault(ziel_rel, []).append(rel)

        # Externe Links (nur auf erlaubten Seiten) brauchen rel="noopener".
        for tag in re.findall(r"<a\b[^>]*>", text):
            ziel = re.search(r'href="(https?://[^"]*)"', tag)
            if ziel and not ziel.group(1).startswith(build.basis):
                if not re.search(r'rel="[^"]*\bnoopener\b', tag):
                    fehler(f"{rel}: externer Link ohne rel=noopener ({ziel.group(1)})")

        # Gedankenstriche
        for treffer in re.finditer(r".{0,30}[–—].{0,30}", text):
            warnung(f"{rel}: Gedankenstrich gefunden: …{treffer.group(0).strip()}…")
        if re.search(r"[^\s>]\s-\s[^\s<]", re.sub(r"<(script|style)\b.*?</\1>", "", text, flags=re.S)):
            warnung(f"{rel}: freistehender Bindestrich ' - ' im Text")

    # Fehlende Ziele zusammengefasst melden (eine Zeile je Ziel statt je Seite).
    for ziel_rel, seiten in sorted(fehlend.items()):
        mehr = f" und {len(seiten) - 1} weiteren Seiten" if len(seiten) > 1 else ""
        meldung = f"Ziel fehlt {ziel_rel} (verlinkt in {seiten[0]}{mehr})"
        if nachsichtig and ziel_rel in FREMDE_DATEIEN:
            warnung(meldung + ", Datei eines anderen Pakets")
        else:
            fehler(meldung)

    for wert, liste in titel.items():
        if len(liste) > 1:
            warnung(f"title doppelt ({wert}): {', '.join(liste)}")
    for wert, liste in beschreibungen.items():
        if len(liste) > 1:
            warnung(f"description doppelt: {', '.join(liste)}")


def main():
    parser = argparse.ArgumentParser(description="Baut die Demo-Seite Notebook Reparatur 24.")
    parser.add_argument("--artikel", default=str(SRC / "daten" / "artikel.json"), help="Pfad zu artikel.json")
    parser.add_argument("--seite", default=str(SRC / "daten" / "seite.json"), help="Pfad zu seite.json")
    parser.add_argument("--nachsichtig", action="store_true",
                        help="fehlende Dateien anderer Pakete (CSS, JS) nur als Warnung melden")
    parser.add_argument("--still", action="store_true", help="Warnungen nicht einzeln ausgeben")
    args = parser.parse_args()

    build = Build(args.artikel, args.seite)
    build.alles()
    geloescht = schreiben(build.dateien)
    pruefen(build, args.nachsichtig)

    print(f"{len(build.dateien)} Dateien erzeugt, {len(build.seiten)} Seiten, {geloescht} veraltete gelöscht.")
    if WARNUNGEN:
        print(f"{len(WARNUNGEN)} Warnungen")
        if not args.still:
            for w in WARNUNGEN:
                print("  Warnung:", w)
    if FEHLER:
        print(f"{len(FEHLER)} Fehler")
        for f in FEHLER:
            print("  FEHLER:", f)
        sys.exit(1)
    print("Prüfung bestanden.")


if __name__ == "__main__":
    main()
