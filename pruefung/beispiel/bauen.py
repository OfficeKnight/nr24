#!/usr/bin/env python3
"""Erzeugt die statischen Beispielseiten in beispiel/gut/ und beispiel/schlecht/.

{{HOST}} ersetzt der Testserver beim Ausliefern durch den abgefragten Hauptnamen.
"""
import json
from pathlib import Path

HIER = Path(__file__).resolve().parent

# ---------------------------------------------------------------- Variante gut

KOPF = """<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>{titel}</title>
<meta name="description" content="{beschreibung}">
<link rel="canonical" href="https://{{{{HOST}}}}{pfad}">
<link rel="stylesheet" href="/assets/style.css">
{jsonld}</head>
<body>
<a class="sprung" href="#inhalt">Zum Inhalt springen</a>
<header class="kopf">
<a class="logo" href="/"><img src="/assets/logo.svg" alt="Beispielshop Startseite" width="160" height="40"></a>
<nav aria-label="Hauptnavigation">
<ul>
<li><a href="/ersatzteile/">Ersatzteile</a></li>
<li><a href="/notebook-reparatur/">Reparatur</a></li>
<li><a href="/kasse/">Kasse</a></li>
</ul>
</nav>
</header>
<main id="inhalt">
"""

FUSS = """</main>
<footer class="fuss">
<nav aria-label="Rechtliches">
<ul>
<li><a href="/impressum/">Impressum</a></li>
<li><a href="/datenschutz/">Datenschutz</a></li>
<li><a href="/agb/">AGB</a></li>
<li><a href="/widerruf/">Widerrufsbelehrung</a></li>
<li><a href="/widerruf/erklaeren/">Vertrag widerrufen</a></li>
</ul>
</nav>
<p>Alle Preise inkl. MwSt., zzgl. Versandkosten.</p>
</footer>
</body>
</html>
"""


def jsonld(*objekte) -> str:
    return "".join('<script type="application/ld+json">\n' + json.dumps(o, ensure_ascii=False, indent=1)
                   + "\n</script>\n" for o in objekte)


FIRMA = {"@context": "https://schema.org", "@type": "ComputerStore", "name": "Beispielshop Notebookteile",
         "url": "https://{{HOST}}/", "telephone": "+49 1234 567890", "email": "info@{{HOST}}",
         "address": {"@type": "PostalAddress", "streetAddress": "Musterstraße 1", "postalCode": "12345",
                     "addressLocality": "Musterstadt", "addressCountry": "DE"}}

PRODUKT = {"@context": "https://schema.org", "@type": "Product", "name": "Displaykabel für Asus X72",
           "sku": "b1", "image": "https://{{HOST}}/assets/displaykabel.svg",
           "offers": {"@type": "Offer", "price": "11.90", "priceCurrency": "EUR",
                      "availability": "https://schema.org/InStock", "url": "https://{{HOST}}/ersatzteile/displays/displaykabel-x72/"}}


def brotkrumen(*stufen) -> dict:
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i, "name": n, "item": "https://{{HOST}}" + p}
        for i, (n, p) in enumerate(stufen, 1)]}


FAQ = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
    {"@type": "Question", "name": "Wie lange dauert eine Reparatur?",
     "acceptedAnswer": {"@type": "Answer", "text": "Meist drei bis fünf Werktage nach Eingang."}},
    {"@type": "Question", "name": "Was kostet die Diagnose?",
     "acceptedAnswer": {"@type": "Answer", "text": "Die Diagnose kostet 29,00 € inkl. MwSt."}}]}

GUT = {
    "/": ("Beispielshop für Notebook-Ersatzteile und Reparatur",
          "Ersatzteile für Notebooks und Reparaturen aus der Werkstatt. Geprüfte Teile mit Rechnung.",
          [FIRMA],
          """<h1>Notebook-Ersatzteile und Reparatur</h1>
<p>Geprüfte Ersatzteile und Reparaturen aus unserer Werkstatt.</p>
<h2>Beliebte Teile</h2>
<ul class="liste">
<li><a href="/ersatzteile/displays/displaykabel-x72/">Displaykabel für Asus X72</a> für 11,90 €</li>
</ul>
<p class="klein">Preise inkl. MwSt., zzgl. Versandkosten.</p>
"""),
    "/ersatzteile/": ("Ersatzteile für Notebooks im Überblick",
                      "Alle Kategorien für Notebook-Ersatzteile auf einen Blick.",
                      [brotkrumen(("Startseite", "/"), ("Ersatzteile", "/ersatzteile/"))],
                      """<h1>Ersatzteile</h1>
<ul class="liste">
<li><a href="/ersatzteile/displays/">Displays und Displaykabel</a></li>
</ul>
"""),
    "/ersatzteile/displays/": ("Displays und Displaykabel für Notebooks",
                               "Displays und Displaykabel für viele Notebookmodelle, geprüft und sofort lieferbar.",
                               [brotkrumen(("Startseite", "/"), ("Ersatzteile", "/ersatzteile/"),
                                           ("Displays", "/ersatzteile/displays/"))],
                               """<h1>Displays und Displaykabel</h1>
<ul class="liste">
<li><a href="/ersatzteile/displays/displaykabel-x72/">Displaykabel für Asus X72</a> für 11,90 €</li>
</ul>
<p class="klein">Preise inkl. MwSt., zzgl. Versandkosten.</p>
"""),
    "/ersatzteile/displays/displaykabel-x72/": (
        "Displaykabel für Asus X72 kaufen",
        "Originales Displaykabel für die Asus X72, gebraucht und getestet, für 11,90 € inkl. MwSt.",
        [PRODUKT, brotkrumen(("Startseite", "/"), ("Ersatzteile", "/ersatzteile/"),
                             ("Displays", "/ersatzteile/displays/"),
                             ("Displaykabel für Asus X72", "/ersatzteile/displays/displaykabel-x72/"))],
        """<nav aria-label="Brotkrumen" class="krumen"><a href="/">Startseite</a> / <a href="/ersatzteile/">Ersatzteile</a> / <a href="/ersatzteile/displays/">Displays</a></nav>
<h1>Displaykabel für Asus X72</h1>
<img src="/assets/displaykabel.svg" alt="Displaykabel mit zwei Steckern" width="320" height="200">
<p class="preis">11,90 €</p>
<p class="klein">inkl. MwSt., zzgl. <a href="/agb/">Versandkosten</a></p>
<p>Gebraucht, geprüft, sofort lieferbar.</p>
"""),
    "/notebook-reparatur/": ("Notebook-Reparatur in der Werkstatt",
                             "Reparatur von Notebooks mit Diagnose, Kostenvoranschlag und Garantie.",
                             [FAQ, brotkrumen(("Startseite", "/"), ("Reparatur", "/notebook-reparatur/"))],
                             """<h1>Notebook-Reparatur</h1>
<p>Diagnose für 29,00 € inkl. MwSt.</p>
<h2>Häufige Fragen</h2>
<details><summary>Wie lange dauert eine Reparatur?</summary><p>Meist drei bis fünf Werktage nach Eingang.</p></details>
<details><summary>Was kostet die Diagnose?</summary><p>Die Diagnose kostet 29,00 € inkl. MwSt.</p></details>
"""),
    "/kasse/": ("Kasse und Bestellübersicht",
                "Bestellung prüfen und abschließen.",
                [],
                """<h1>Kasse</h1>
<form method="post" action="/kasse/">
<p><label for="name">Name</label><br><input id="name" name="name" autocomplete="name" required></p>
<p><label for="email">E-Mail</label><br><input id="email" name="email" type="email" autocomplete="email" required></p>
<p>Displaykabel für Asus X72, 11,90 € inkl. MwSt., zzgl. Versandkosten 4,90 €</p>
<p><button type="submit">Zahlungspflichtig bestellen</button></p>
</form>
"""),
    "/impressum/": ("Impressum des Beispielshops", "Anbieterkennzeichnung des Beispielshops.", [],
                    "<h1>Impressum</h1>\n<p>Beispielshop Notebookteile, Musterstraße 1, 12345 Musterstadt.</p>\n"),
    "/datenschutz/": ("Datenschutzerklärung des Beispielshops", "Informationen zum Datenschutz im Beispielshop.", [],
                      "<h1>Datenschutz</h1>\n<p>Wir setzen nur technisch nötige Cookies.</p>\n"),
    "/agb/": ("Allgemeine Geschäftsbedingungen", "Allgemeine Geschäftsbedingungen und Versandkosten des Beispielshops.", [],
              "<h1>AGB</h1>\n<p>Versandkosten innerhalb Deutschlands 4,90 €.</p>\n"),
    "/widerruf/": ("Widerrufsbelehrung des Beispielshops", "Widerrufsrecht und Muster-Widerrufsformular.", [],
                   "<h1>Widerrufsbelehrung</h1>\n<p>Sie können den Vertrag binnen vierzehn Tagen widerrufen.</p>\n"),
    "/widerruf/erklaeren/": ("Vertrag online widerrufen", "Hier erklären Sie den Widerruf Ihres Vertrags online.", [],
                             """<h1>Vertrag widerrufen</h1>
<form method="post" action="/widerruf/erklaeren/">
<p><label for="bestellnummer">Bestellnummer</label><br><input id="bestellnummer" name="bestellnummer" required></p>
<p><button type="submit">Widerruf bestätigen</button></p>
</form>
"""),
}

STIL = """body{font-family:system-ui,sans-serif;color:#1a1a1a;background:#fff;margin:0;line-height:1.5}
a{color:#0b4f9c;text-decoration:underline}
.sprung{position:absolute;left:-9999px}.sprung:focus{left:1rem;top:1rem}
.kopf,.fuss,main{max-width:60rem;margin:0 auto;padding:1rem}
.kopf ul,.fuss ul{list-style:none;display:flex;flex-wrap:wrap;gap:1rem;padding:0;margin:0}
.kopf li a,.fuss li a,.liste a,.krumen a,.logo{display:inline-block;padding:.4rem .2rem;min-height:24px}
.preis{font-size:1.5rem;font-weight:700}.klein{font-size:.95rem;color:#333}
button{font:inherit;padding:.6rem 1rem;background:#0b4f9c;color:#fff;border:0;border-radius:4px}
input{font:inherit;padding:.4rem}
"""

LOGO = """<svg xmlns="http://www.w3.org/2000/svg" width="160" height="40" viewBox="0 0 160 40"><rect width="160" height="40" fill="#0b4f9c"/><text x="10" y="26" font-family="sans-serif" font-size="16" fill="#fff">Beispielshop</text></svg>
"""
BILD = """<svg xmlns="http://www.w3.org/2000/svg" width="320" height="200" viewBox="0 0 320 200"><rect width="320" height="200" fill="#eef"/><path d="M20 100 H300" stroke="#333" stroke-width="8"/><rect x="10" y="85" width="30" height="30" fill="#555"/><rect x="280" y="85" width="30" height="30" fill="#555"/></svg>
"""


def gut_bauen() -> None:
    wurzel = HIER / "gut"
    for pfad, (titel, beschreibung, objekte, inhalt) in GUT.items():
        ziel = wurzel / pfad.lstrip("/") / "index.html"
        ziel.parent.mkdir(parents=True, exist_ok=True)
        ziel.write_text(KOPF.format(titel=titel, beschreibung=beschreibung, pfad=pfad, jsonld=jsonld(*objekte))
                        + inhalt + FUSS, encoding="utf-8")
    (wurzel / "404.html").write_text(
        KOPF.format(titel="Seite nicht gefunden", beschreibung="Diese Seite gibt es nicht.", pfad="/404.html", jsonld="")
        + "<h1>Seite nicht gefunden</h1>\n" + FUSS, encoding="utf-8")
    (wurzel / "assets").mkdir(exist_ok=True)
    (wurzel / "assets" / "style.css").write_text(STIL, encoding="utf-8")
    (wurzel / "assets" / "logo.svg").write_text(LOGO, encoding="utf-8")
    (wurzel / "assets" / "displaykabel.svg").write_text(BILD, encoding="utf-8")
    (wurzel / "robots.txt").write_text("User-agent: *\nDisallow: /\n\nSitemap: https://{{HOST}}/sitemap.xml\n",
                                       encoding="utf-8")
    (wurzel / "robots-live.txt").write_text("User-agent: *\nDisallow: /kasse/\n\nSitemap: https://{{HOST}}/sitemap.xml\n",
                                            encoding="utf-8")
    eintraege = "".join(f"  <url><loc>https://{{{{HOST}}}}{p}</loc></url>\n" for p in GUT if p != "/kasse/")
    (wurzel / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + eintraege + "</urlset>\n", encoding="utf-8")


# ----------------------------------------------------------- Variante schlecht

SCHLECHT = {
    "/": """<!doctype html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">
<title>Shop</title>
<link rel="stylesheet" href="/assets/style.css">
<script src="https://drittanbieter.test/tracker.js"></script>
<script type="application/ld+json">
{ "@context": "https://schema.org", "@type": "Organization", "name": "Beispielshop", }
</script>
</head>
<body>
<h1>Willkommen</h1>
<h1>Notebook-Ersatzteile</h1>
<img src="/assets/kabel.svg">
<script src="/assets/gross.js"></script>
<p class="blass">Displaykabel für Asus X72 für 19,90 €</p>
<p><a href="/ersatzteile/displays/kabel/">Zum Kabel</a> und <a href="/gibt-es-nicht/">Sonderangebote</a></p>
<h2>FAQ</h2>
<p>Wie lange dauert eine Reparatur? Etwa eine Woche.</p>
<p><input name="suche" placeholder="Suche"></p>
<footer><a href="/impressum/">Impressum</a> <a href="/datenschutz/">Datenschutz</a> <a href="/kasse/">Kasse</a></footer>
</body>
</html>
""",
    "/ersatzteile/displays/kabel/": """<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>Shop</title>
<meta name="description" content="Displaykabel">
<link rel="canonical" href="/ersatzteile/displays/kabel/">
<link rel="stylesheet" href="/assets/style.css">
</head>
<body>
<main>
<h1>Displaykabel für Asus X72</h1>
<img src="/assets/kabel.svg" alt="Displaykabel">
<p>11,90 € inkl. MwSt.</p>
<p><a href="/">Startseite</a> <a href="/impressum/">Impressum</a> <a href="/datenschutz/">Datenschutz</a></p>
</main>
</body>
</html>
""",
    "/kasse/": """<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>Kasse</title>
<meta name="description" content="Kasse">
<link rel="canonical" href="https://{{HOST}}/kasse/">
<link rel="stylesheet" href="/assets/style.css">
</head>
<body>
<main>
<h1>Kasse</h1>
<form method="post" action="/kasse/">
<p><label for="name">Name</label> <input id="name" name="name"></p>
<p><button type="submit">Bestellen</button></p>
</form>
<p><a href="/impressum/">Impressum</a> <a href="/datenschutz/">Datenschutz</a></p>
</main>
</body>
</html>
""",
    "/impressum/": """<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>Impressum</title>
<meta name="description" content="Impressum">
<link rel="canonical" href="https://andere-domain.example/impressum/">
<link rel="stylesheet" href="/assets/style.css">
</head>
<body>
<main>
<h1>Impressum</h1>
<p>Beispielshop, Musterstraße 1, 12345 Musterstadt.</p>
<p><a href="/">Startseite</a> <a href="/datenschutz/">Datenschutz</a></p>
</main>
</body>
</html>
""",
    "/datenschutz/": """<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>Datenschutz</title>
<meta name="description" content="Datenschutz">
<link rel="canonical" href="https://{{HOST}}/datenschutz/">
<link rel="stylesheet" href="/assets/style.css">
</head>
<body>
<main>
<h1>Datenschutz</h1>
<p>Wir verwenden Werbecookies.</p>
<p><a href="/">Startseite</a> <a href="/impressum/">Impressum</a></p>
</main>
</body>
</html>
""",
}

STIL_SCHLECHT = """body{font-family:sans-serif;color:#222;background:#fff}
.blass{color:#c8c8c8}
a{color:#222;text-decoration:none}
"""


def schlecht_bauen() -> None:
    wurzel = HIER / "schlecht"
    for pfad, html in SCHLECHT.items():
        ziel = wurzel / pfad.lstrip("/") / "index.html"
        ziel.parent.mkdir(parents=True, exist_ok=True)
        ziel.write_text(html, encoding="utf-8")
    (wurzel / "assets").mkdir(exist_ok=True)
    (wurzel / "assets" / "style.css").write_text(STIL_SCHLECHT, encoding="utf-8")
    (wurzel / "assets" / "kabel.svg").write_text(BILD, encoding="utf-8")


if __name__ == "__main__":
    gut_bauen()
    schlecht_bauen()
    print("Beispielseiten erzeugt")
