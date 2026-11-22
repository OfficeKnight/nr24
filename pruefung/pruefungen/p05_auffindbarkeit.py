"""Prüfung 5. Auffindbarkeit je Seite, Indexierung, sitemap.xml und robots.txt."""
if __name__ == "__main__":
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    import lib.start  # noqa: F401

from collections import defaultdict

from lib.adressen import host, normalisieren
from lib.kern import Beleg, Ergebnis, NichtPruefbar

NUMMER = 5
TITEL = "Auffindbarkeit"


def _noindex(seite) -> str | None:
    for m in seite.soup.find_all("meta"):
        if (m.get("name") or "").lower() in ("robots", "googlebot") and "noindex" in (m.get("content") or "").lower():
            return f"meta {m.get('name')} {m.get('content')}"
    kopf = seite.antwort.headers.get("x-robots-tag", "")
    if "noindex" in kopf.lower():
        return f"X-Robots-Tag {kopf}"
    return None


def _robots_sperrt_alles(text: str) -> bool:
    gruppe_alle, sperrt = False, False
    for zeile in text.splitlines():
        z = zeile.split("#", 1)[0].strip()
        if not z or ":" not in z:
            continue
        feld, wert = (t.strip() for t in z.split(":", 1))
        feld = feld.lower()
        if feld == "user-agent":
            gruppe_alle = wert == "*"
        elif feld == "disallow" and gruppe_alle and wert == "/":
            sperrt = True
    return sperrt


def pruefen(k) -> Ergebnis:
    erg = Ergebnis(NUMMER, TITEL)
    e = k.erfassung()
    seiten = e.html_seiten()
    if not seiten:
        raise NichtPruefbar("Keine erreichbare HTML-Seite gefunden.")
    haupthost = host(k.hauptadresse)

    titel_fehler, titel_ok = [], []
    titel_zu_seiten = defaultdict(list)
    beschr_f, beschr_ok = [], []
    h1_f, h1_ok = [], []
    can_f, can_ok, can_h = [], [], []
    lang_f, lang_ok = [], []
    bild_f, bild_ok, bild_h = [], [], []
    index_f, index_ok = [], []

    for s in seiten:
        adr = s.endadresse
        soup = s.soup
        t = soup.title.get_text(" ", strip=True) if soup.title else ""
        if not t:
            titel_fehler.append(Beleg(adr, "<title>", "Kein Titel"))
        else:
            titel_zu_seiten[t].append(adr)
        d = None
        for m in soup.find_all("meta"):
            if (m.get("name") or "").lower() == "description":
                d = (m.get("content") or "").strip()
        if not d:
            beschr_f.append(Beleg(adr, 'meta name="description"', "Fehlt oder ist leer"))
        else:
            beschr_ok.append(Beleg(adr, 'meta name="description"', f"{len(d)} Zeichen"))
        h1 = soup.find_all("h1")
        if len(h1) != 1:
            texte = " und ".join(h.get_text(" ", strip=True)[:60] for h in h1) or "keine"
            h1_f.append(Beleg(adr, "<h1>", f"{len(h1)} Überschriften erster Ebene ({texte})"))
        else:
            h1_ok.append(Beleg(adr, "<h1>", h1[0].get_text(" ", strip=True)[:100]))
        canon = [l_ for l_ in soup.find_all("link", href=True)
                 if "canonical" in [r.lower() for r in (l_.get("rel") or [])]]
        if len(canon) != 1:
            can_f.append(Beleg(adr, 'link rel="canonical"', f"{len(canon)} Angaben statt genau einer"))
        else:
            ziel = canon[0]["href"].strip()
            if not ziel.startswith(("http://", "https://")):
                can_f.append(Beleg(adr, 'link rel="canonical"', f"{ziel} ist keine absolute Adresse"))
            elif host(ziel) != haupthost:
                can_f.append(Beleg(adr, 'link rel="canonical"', f"{ziel} zeigt auf einen anderen Host als {haupthost}"))
            else:
                can_ok.append(Beleg(adr, 'link rel="canonical"', ziel))
                if normalisieren(ziel) != adr:
                    can_h.append(Beleg(adr, 'link rel="canonical"', f"Zeigt auf eine andere Seite ({ziel})"))
        html = soup.find("html")
        lang = (html.get("lang") or "").strip() if html else ""
        if not lang:
            lang_f.append(Beleg(adr, "<html lang>", "Attribut lang fehlt"))
        else:
            lang_ok.append(Beleg(adr, "<html lang>", lang))
        bilder = soup.find_all("img")
        maengel_seite = 0
        for i, b in enumerate(bilder, start=1):
            quelle = b.get("src") or b.get("data-src") or f"Bild {i}"
            fehlt = []
            if not b.has_attr("alt"):
                fehlt.append("alt")
            if not (b.get("width") and b.get("height")):
                fehlt.append("width und height")
            if fehlt:
                maengel_seite += 1
                bild_f.append(Beleg(adr, f"<img src={quelle}>", "Es fehlt " + ", ".join(fehlt)))
            elif not b["alt"].strip():
                bild_h.append(Beleg(adr, f"<img src={quelle}>", "Leerer Alt-Text, nur für Schmuckbilder passend"))
        if bilder and not maengel_seite:
            bild_ok.append(Beleg(adr, "<img>", f"{len(bilder)} {'Bild' if len(bilder) == 1 else 'Bilder'} mit alt, width und height"))
        ni = _noindex(s)
        if k.modus == "demo":
            if ni:
                index_ok.append(Beleg(adr, ni.rsplit(" ", 2)[0] if ni.startswith("meta") else "X-Robots-Tag", ni))
            else:
                index_f.append(Beleg(adr, "meta robots und X-Robots-Tag", "Kein noindex, im Modus demo Pflicht"))
        else:
            if ni:
                index_f.append(Beleg(adr, ni.rsplit(" ", 2)[0] if ni.startswith("meta") else "X-Robots-Tag",
                                     f"{ni}, im Modus live verboten"))
            else:
                index_ok.append(Beleg(adr, "meta robots und X-Robots-Tag", "Kein noindex"))

    for t, adressen in titel_zu_seiten.items():
        if len(adressen) > 1:
            for a in adressen:
                titel_fehler.append(Beleg(a, "<title>", f"Titel {t} kommt auf {len(adressen)} Seiten vor"))
        else:
            titel_ok.append(Beleg(adressen[0], "<title>", t))

    erg.bewerten("Eigener Titel je Seite", titel_fehler, titel_ok)
    erg.bewerten("Meta-Beschreibung vorhanden", beschr_f, beschr_ok)
    erg.bewerten("Genau eine H1", h1_f, h1_ok)
    erg.bewerten("Canonical vorhanden", can_f, can_ok, can_h)
    erg.bewerten("lang-Attribut gesetzt", lang_f, lang_ok)
    erg.bewerten("Bilder mit Alt-Text und festen Maßen", bild_f, bild_ok, bild_h)
    erg.bewerten("noindex passend zum Modus " + k.modus, index_f, index_ok)

    # tote interne Links
    fehler, hinweise = [], []
    geprueft = 0
    for quelle, href, ziel in e.links:
        s = e.seite_zu(ziel)
        if s is None:
            continue
        geprueft += 1
        a = s.antwort
        if a.fehler or (a.status or 0) >= 400:
            fehler.append(Beleg(quelle, f'<a href="{href}">', f"Ziel {ziel} liefert {a.status or a.fehler}"))
    ungeprueft = {z for _, _, z in e.links if e.seite_zu(z) is None}
    if ungeprueft:
        hinweise.append(Beleg(k.hauptadresse, "Obergrenze oder Ausschluss",
                              f"{len(ungeprueft)} interne Linkziele nicht abgerufen, etwa {sorted(ungeprueft)[0]}"))
    ok = [Beleg(k.hauptadresse, "<a href>", f"{geprueft} interne Links auf {len(seiten)} Seiten geprüft")]
    erg.bewerten("Keine toten internen Links", fehler, ok, hinweise)

    # sitemap.xml
    fehler, ok, hinweise = [], [], []
    for adr, text in e.sitemap_fehler:
        fehler.append(Beleg(adr, "Sitemap", text))
    if e.sitemap_urls:
        fremde = [u for u in e.sitemap_urls if host(u) != haupthost]
        for u in fremde[:20]:
            fehler.append(Beleg(u, "Sitemap loc", f"Adresse liegt nicht auf {haupthost}"))
        tote = []
        for u in e.sitemap_urls:
            s = e.seite_zu(u)
            if s and (s.antwort.fehler or s.antwort.status != 200 or normalisieren(s.endadresse) != normalisieren(u)):
                tote.append((u, s))
        for u, s in tote:
            fehler.append(Beleg(u, "Sitemap loc", f"Liefert {s.antwort.status or s.antwort.fehler}"
                                f"{', leitet auf ' + s.endadresse + ' weiter' if s.endadresse != normalisieren(u) else ''}"))
        ok.append(Beleg(e.sitemaps[0].url if e.sitemaps else k.hauptadresse, "Sitemap",
                        f"{len(e.sitemap_urls)} Adressen gefunden"))
        if k.modus == "live" and fremde:
            hinweise.append(Beleg(k.hauptadresse, "Sitemap", "Sitemap verweist auf einen anderen Host, etwa die Demo"))
    elif not e.sitemap_fehler:
        fehler.append(Beleg(k.hauptadresse, "Sitemap", "Keine Adressen in der Sitemap"))
    erg.bewerten("sitemap.xml vorhanden und gültig", fehler, ok, hinweise)

    # robots.txt
    fehler, ok, hinweise = [], [], []
    r = e.robots
    if r is None or r.fehler or r.status != 200:
        fehler.append(Beleg(k.hauptadresse.rstrip("/") + "/robots.txt", "robots.txt",
                            f"Liefert {r.status if r else 'nichts'}{' ' + r.fehler if r and r.fehler else ''}"))
    else:
        sperrt = _robots_sperrt_alles(r.text)
        if k.modus == "live" and sperrt:
            fehler.append(Beleg(r.url, "User-agent * Disallow /", "Sperrt im Modus live alle Suchmaschinen aus"))
        elif sperrt:
            hinweise.append(Beleg(r.url, "User-agent * Disallow /",
                                  "Sperrt alle Suchmaschinen aus. Für die Demo passend, Suchmaschinen sehen dann aber das noindex nicht"))
        ok.append(Beleg(r.url, "robots.txt", f"Status 200, {len(r.text.splitlines())} Zeilen"))
        if "sitemap:" not in r.text.lower():
            hinweise.append(Beleg(r.url, "robots.txt", "Keine Zeile Sitemap"))
    erg.bewerten("robots.txt vorhanden", fehler, ok, hinweise)
    if e.nicht_geprueft:
        erg.hinweis(k.hauptadresse, "Obergrenze",
                    f"{len(e.nicht_geprueft)} Adressen wegen der Obergrenze von {k.max_seiten} Seiten nicht erfasst")
    return erg


if __name__ == "__main__":
    from lib.ablauf import einzeln
    einzeln(sys.modules[__name__])
