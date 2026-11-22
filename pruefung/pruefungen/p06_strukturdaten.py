"""Prüfung 6. Strukturierte Daten in JSON-LD."""
if __name__ == "__main__":
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    import lib.start  # noqa: F401

import json
import re

from lib.adressen import normalisieren, pfad
from lib.kern import Beleg, Ergebnis, NichtPruefbar

NUMMER = 6
TITEL = "Strukturierte Daten"

FAQ_MUSTER = re.compile(r"(?i)\b(faq|häufige[n]?\s+fragen|häufig\s+gestellte\s+fragen|fragen\s+und\s+antworten)\b")
FIRMENTYPEN = {"Organization", "Corporation", "LocalBusiness", "Store", "OnlineStore", "OnlineBusiness",
               "ElectronicsStore", "ComputerStore", "ProfessionalService", "HomeAndConstructionBusiness"}
VERFUEGBAR = {"InStock", "OutOfStock", "PreOrder", "BackOrder", "Discontinued", "InStoreOnly", "LimitedAvailability",
              "OnlineOnly", "PreSale", "SoldOut", "Reserved", "MadeToOrder"}


def _typen(obj) -> set:
    t = obj.get("@type", [])
    t = t if isinstance(t, list) else [t]
    return {str(x).split("/")[-1].split(":")[-1] for x in t}


def _alle_objekte(daten):
    """Liefert alle Objekte mit @type, auch verschachtelte und aus @graph."""
    stapel = [daten]
    while stapel:
        o = stapel.pop()
        if isinstance(o, list):
            stapel.extend(o)
        elif isinstance(o, dict):
            if "@type" in o:
                yield o
            for v in o.values():
                if isinstance(v, (list, dict)):
                    stapel.append(v)


def json_ld(seite):
    """Gibt (objekte, fehler) zurück."""
    objekte, fehler = [], []
    for i, skript in enumerate(seite.soup.find_all("script", type=re.compile(r"application/ld\+json", re.I)), 1):
        roh = skript.string or skript.get_text() or ""
        try:
            objekte.extend(_alle_objekte(json.loads(roh)))
        except json.JSONDecodeError as e:
            fehler.append((i, f"JSON nicht lesbar in Zeile {e.lineno}, Spalte {e.colno} ({e.msg})"))
    return objekte, fehler


def _preis_ok(wert) -> bool:
    if isinstance(wert, (int, float)):
        return True
    return bool(re.fullmatch(r"\d+(\.\d+)?", str(wert).strip()))


def _product_pruefen(p) -> list:
    maengel = []
    if not str(p.get("name", "")).strip():
        maengel.append("name fehlt")
    angebote = p.get("offers")
    angebote = angebote if isinstance(angebote, list) else [angebote] if angebote else []
    if not angebote:
        return maengel + ["offers fehlt, damit fehlen Preis, Währung und Verfügbarkeit"]
    for o in angebote:
        if not isinstance(o, dict):
            maengel.append("offers ist kein Objekt")
            continue
        preis = o.get("price", o.get("lowPrice"))
        if preis is None and isinstance(o.get("priceSpecification"), dict):
            preis = o["priceSpecification"].get("price")
        if preis is None:
            maengel.append("offers.price fehlt")
        elif not _preis_ok(preis):
            maengel.append(f"offers.price {preis} ist keine Zahl mit Punkt als Dezimaltrenner")
        if not str(o.get("priceCurrency", "")).strip():
            maengel.append("offers.priceCurrency fehlt")
        verf = str(o.get("availability", "")).split("/")[-1]
        if not verf:
            maengel.append("offers.availability fehlt")
        elif verf not in VERFUEGBAR:
            maengel.append(f"offers.availability {o.get('availability')} ist kein schema.org-Wert")
    return maengel


def ist_artikelseite(seite, objekte, muster) -> str | None:
    if any("Product" in _typen(o) for o in objekte):
        return "Product in JSON-LD"
    for m in seite.soup.find_all("meta"):
        if (m.get("property") or "").lower() == "og:type" and (m.get("content") or "").lower() in ("product", "og:product"):
            return "og:type product"
    p = pfad(seite.endadresse)
    for m in muster:
        if m.search(p):
            return f"Pfad passt zu {m.pattern}"
    return None


def hat_faq(seite) -> str | None:
    for h in seite.soup.find_all(["h1", "h2", "h3", "h4", "summary"]):
        t = h.get_text(" ", strip=True)
        if FAQ_MUSTER.search(t):
            return t[:80]
    return None


def pruefen(k) -> Ergebnis:
    erg = Ergebnis(NUMMER, TITEL)
    seiten = k.erfassung().html_seiten()
    if not seiten:
        raise NichtPruefbar("Keine erreichbare HTML-Seite gefunden.")
    muster = [re.compile(m) for m in k.einstellungen.get("artikel_muster", [])]
    lesbar_f, lesbar_ok = [], []
    art_f, art_ok = [], []
    bc_f, bc_ok = [], []
    faq_f, faq_ok = [], []
    start_f, start_ok = [], []
    haupt = normalisieren(k.hauptadresse)
    start_gefunden = False

    for s in seiten:
        adr = s.endadresse
        objekte, fehler = json_ld(s)
        for nr, text in fehler:
            lesbar_f.append(Beleg(adr, f"script application/ld+json Nr. {nr}", text))
        if objekte and not fehler:
            lesbar_ok.append(Beleg(adr, "script application/ld+json",
                                   "Lesbar, Typen " + ", ".join(sorted(set().union(*(_typen(o) for o in objekte))))))
        typen = set().union(*(_typen(o) for o in objekte)) if objekte else set()

        grund = ist_artikelseite(s, objekte, muster)
        if grund:
            produkte = [o for o in objekte if "Product" in _typen(o)]
            if not produkte:
                art_f.append(Beleg(adr, "JSON-LD Product", f"Artikelseite ({grund}) ohne Product"))
            for p in produkte:
                maengel = _product_pruefen(p)
                if maengel:
                    art_f.append(Beleg(adr, f"Product {p.get('name', '')}".strip(), ", ".join(maengel)))
                else:
                    o = p["offers"][0] if isinstance(p["offers"], list) else p["offers"]
                    art_ok.append(Beleg(adr, f"Product {p.get('name')}",
                                        f"Preis {o.get('price', o.get('lowPrice'))} {o.get('priceCurrency')}, "
                                        f"{str(o.get('availability')).split('/')[-1]}"))
            bcs = [o for o in objekte if "BreadcrumbList" in _typen(o)]
            if not bcs:
                bc_f.append(Beleg(adr, "JSON-LD BreadcrumbList", "Artikelseite ohne BreadcrumbList"))
            elif not any(isinstance(b.get("itemListElement"), list) and b["itemListElement"] for b in bcs):
                bc_f.append(Beleg(adr, "JSON-LD BreadcrumbList", "itemListElement fehlt oder ist leer"))
            else:
                bc_ok.append(Beleg(adr, "JSON-LD BreadcrumbList",
                                   f"{len(bcs[0]['itemListElement'])} Stufen"))

        faq = hat_faq(s)
        if faq:
            faqs = [o for o in objekte if "FAQPage" in _typen(o)]
            if not faqs:
                faq_f.append(Beleg(adr, f"Überschrift {faq}", "FAQ-Bereich ohne FAQPage"))
            else:
                fragen = faqs[0].get("mainEntity") or []
                fragen = fragen if isinstance(fragen, list) else [fragen]
                gute = [f for f in fragen if isinstance(f, dict) and "Question" in _typen(f)
                        and f.get("name") and f.get("acceptedAnswer")]
                if not gute:
                    faq_f.append(Beleg(adr, "JSON-LD FAQPage", "mainEntity ohne Question mit acceptedAnswer"))
                else:
                    faq_ok.append(Beleg(adr, "JSON-LD FAQPage", f"{len(gute)} Fragen mit Antwort"))
        elif "FAQPage" in typen:
            faq_ok.append(Beleg(adr, "JSON-LD FAQPage", "FAQPage vorhanden"))

        if adr == haupt:
            start_gefunden = True
            firmen = [o for o in objekte if _typen(o) & FIRMENTYPEN
                      or any(t.endswith(("Store", "Business")) for t in _typen(o))]
            if not firmen:
                start_f.append(Beleg(adr, "JSON-LD", "Keine Firmendaten (Organization, LocalBusiness oder Store)"))
            else:
                f = firmen[0]
                kontakt = [x for x in ("address", "telephone", "email") if f.get(x)]
                if not f.get("name"):
                    start_f.append(Beleg(adr, f"JSON-LD {', '.join(sorted(_typen(f)))}", "name fehlt"))
                elif not kontakt:
                    start_f.append(Beleg(adr, f"JSON-LD {', '.join(sorted(_typen(f)))}",
                                         "Weder address noch telephone noch email angegeben"))
                else:
                    start_ok.append(Beleg(adr, f"JSON-LD {', '.join(sorted(_typen(f)))}",
                                          f"{f.get('name')} mit {', '.join(kontakt)}"))
    if not start_gefunden:
        start_f.append(Beleg(haupt, "Startseite", "Startseite nicht unter den erfassten Seiten"))

    erg.bewerten("JSON-LD lesbar", lesbar_f, lesbar_ok)
    if art_f or art_ok:
        erg.bewerten("Artikelseiten mit Product, Preis, Währung und Verfügbarkeit", art_f, art_ok)
        erg.bewerten("Artikelseiten mit BreadcrumbList", bc_f, bc_ok)
    else:
        erg.nicht_pruefbar("Artikelseiten mit Product, Preis, Währung und Verfügbarkeit", haupt, "Erkennung",
                           "Keine Artikelseite erkannt. Muster in einstellungen.json unter artikel_muster anpassen")
    if faq_f or faq_ok:
        erg.bewerten("FAQ-Bereiche mit FAQPage", faq_f, faq_ok)
    else:
        erg.teil("FAQ-Bereiche mit FAQPage", "bestanden",
                 [Beleg(haupt, "Überschriften", "Kein FAQ-Bereich gefunden, daher nichts zu verlangen", "ok")])
    erg.bewerten("Startseite mit Firmendaten", start_f, start_ok)
    return erg


if __name__ == "__main__":
    from lib.ablauf import einzeln
    einzeln(sys.modules[__name__])
