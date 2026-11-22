# Notebook Reparatur 24, Demo für ein Redesign

Dieses Repository enthält eine Vorschau für das Redesign des Webshops „Notebook Reparatur 24“, eines Shops für Notebook-Reparaturen und Ersatzteile. Die Demo zeigt Gestaltung, Aufbau und Bedienung der neuen Seite mit echten Artikeln, Preisen und Kennzahlen aus dem bisherigen Shop und von eBay.

Die Demo ist bewusst keine echte Seite.

* Alle Angaben zu Person, Anschrift und Kontakt sind Musterdaten (Max Mustermann, Musterstraße 1, 12345 Musterstadt).
* Suche, Filter, Sortierung, Warenkorb und Kasse funktionieren. Bestellungen und Anfragen werden nicht übertragen, der letzte Knopf der Kasse ist gesperrt.
* Alle Seiten tragen `noindex, nofollow`, die Datei `robots.txt` sperrt alle Suchmaschinen.
* Es gibt kein Tracking, keine Cookies und keine Inhalte von fremden Servern. Warenkorb und Einstellungen der Demo-Leiste speichert nur der Browser selbst (localStorage).
* Angaben, die der Inhaber noch liefern muss, stehen als Platzhalter in eckigen Klammern im Text, zum Beispiel `[Bearbeitungszeit]`.

Die Seite läuft unter https://nr24.kazas.dev/, unter https://officeknight.github.io/nr24/ und lokal. Alle Links sind relativ, deshalb funktioniert sie in jedem Unterordner.

## Aufbau

Die Seiten sind statisches HTML. Sie werden mit einem kleinen Python-Skript aus Vorlagen und Daten erzeugt und liegen danach fertig in der Repo-Wurzel. Erzeugte HTML-Dateien bitte nie direkt ändern, sondern immer die Quellen in `src/` und danach neu bauen.

```
.
├── index.html, 404.html, sitemap.xml   erzeugt, nicht von Hand ändern
├── ersatzteile/ notebook-reparatur/ …  erzeugte Seiten mit sprechenden Adressen
├── bildnachweise/                      erzeugte Seite mit Urheber und Lizenz aller Fotos
├── robots.txt                          sperrt alle Suchmaschinen (Demo)
├── CNAME                               eigene Domain für GitHub Pages
├── .nojekyll                           GitHub Pages liefert die Dateien unverändert aus
├── favicon.svg
├── BILDQUELLEN.md                      Herkunft und Lizenz aller Bilder
├── assets/
│   ├── css/style.css                   Gestaltung der Seite
│   ├── css/themen.css                  Farben der drei Designs A, B und C
│   ├── css/schriften.css               @font-face und die drei Schriftpaare
│   ├── fonts/                          Schriften als WOFF2, Lizenzen in LIZENZEN.md
│   ├── js/shop.js                      Suche, Filter, Sortierung, Warenkorb, Kasse, Formulare
│   ├── js/daten.js                     erzeugt, Artikeldaten für shop.js
│   ├── js/demo.js                      Demo-Leiste (nur für die Vorschau)
│   └── bilder/                         Bilder als WebP in mehreren Breiten
│       ├── fotos/                      freie Fotos (CC BY 2.0 und CC0)
│       ├── produkte/                   Produktfotos aus dem bisherigen Shop
│       └── kategorien/                 Bilder der Kategorien
└── src/
    ├── build.py                        Build und eingebaute Prüfung
    ├── platzhalter.py                  sammelt alle Platzhalter in eckigen Klammern
    ├── erzeugte-dateien.txt            Liste der erzeugten Dateien (vom Build gepflegt)
    ├── daten/artikel.json              Kategorien und Artikel
    ├── daten/seite.json                alle übrigen Texte, Kontaktdaten, Versand, Zahlarten, FAQ
    ├── daten/bilder-fotos.json         Bildliste der freien Fotos mit Urheber und Lizenz
    ├── daten/bilder-shop.json          Bildliste der Bilder aus dem bisherigen Shop
    ├── inhalte/*.html                  Rechtstexte (Impressum, AGB, Widerruf, Datenschutz, Versand)
    └── vorlagen/*.html                 Vorlagen der Seiten, base.html ist der gemeinsame Rahmen
```

## Befehle

Alle Befehle laufen in der Repo-Wurzel. Nötig ist nur Python ab Version 3.9, der Build verwendet ausschließlich die Standardbibliothek.

Seite bauen. Am Ende muss „Prüfung bestanden“ stehen.

```
python3 src/build.py
```

Seite lokal ansehen, danach im Browser http://localhost:8000/ öffnen.

```
python3 -m http.server 8000
```

Die Seite nicht direkt als Datei öffnen, sonst blockiert die Sicherheitsrichtlinie (Content Security Policy) Skripte und Bilder.

Platzhalter auflisten, die noch gefüllt werden müssen.

```
python3 src/platzhalter.py
python3 src/platzhalter.py --markdown
```

### Prüfungen

Der Build prüft bei jedem Lauf alle erzeugten Seiten. Er meldet unter anderem fehlende Dateien und Bilder, Links ins Leere, absolute Links (fremde Links sind nur auf der Seite Bildnachweise erlaubt und brauchen dort `rel="noopener"`), fehlendes `noindex`, fehlende oder doppelte Title und Descriptions, mehr oder weniger als eine H1, doppelte IDs sowie Gedankenstriche im Text. Mit `--nachsichtig` werden fehlende Dateien anderer Teile nur als Warnung gemeldet, mit `--still` werden Warnungen nur gezählt.

Für weitergehende Prüfungen eignen sich diese Werkzeuge.

* HTML-Validierung mit dem Nu Html Checker (npm-Paket `vnu-jar`, benötigt Java). Die erzeugten Seiten sind ohne Fehler. Hinweise zur Content Security Policy bei der Prüfung als lokale Datei sind zu erwarten, weil eine Datei keinen eigenen Ursprung hat.

  ```
  java -jar node_modules/vnu-jar/build/dist/vnu.jar --skip-non-html .
  ```

* Barrierefreiheit mit axe-core, zum Beispiel über Playwright im laufenden lokalen Server.
* Funktionstest von Suche, Filter, Warenkorb und Kasse im Browser, auf dem Handy und mit der Tastatur.

## Daten pflegen

### Artikel

Artikel stehen in `src/daten/artikel.json` in der Liste `artikel`. Jeder Artikel hat eine eindeutige `id` (zum Beispiel `a18`), einen `slug` für die Adresse, die `kategorie` (einer der Slugs aus `kategorien`), die `art` (`ware` oder `reparatur`), `name`, `hersteller`, `modelle`, `teilenummer`, `preis` in Euro als Zahl, `zustand`, `verfuegbar`, `lieferzeit`, einen Satz `kurz`, die `beschreibung` als HTML, `merkmale` als Liste aus Paaren und `bilder`. Die Adresse ergibt sich aus Kategorie und Slug, also zum Beispiel `ersatzteile/displays/<slug>/`.

Am einfachsten kopieren Sie einen ähnlichen Artikel, ändern `id`, `slug` und die Texte und bauen neu. Seite, Kategorieliste, Suche, Sitemap und strukturierte Daten werden dabei automatisch ergänzt. Ein entfernter Artikel verschwindet beim nächsten Build mitsamt seiner Seite.

Bei Reparaturen, deren Preis nur Diagnose und Kostenvoranschlag abdeckt, setzen Sie zusätzlich `preis_label` (zum Beispiel `Diagnose`) und `preis_hinweis`. Dann steht der Zusatz vor dem Preis in Listen und auf der Artikelseite.

### Texte

Alle Texte der Startseite, der Reparaturseiten, der FAQ, des Ablaufs, der Kontaktdaten, der Versandarten und Zahlarten stehen in `src/daten/seite.json`. Die Rechtstexte stehen als HTML-Abschnitte in `src/inhalte/`. Für alle Texte gelten dieselben Regeln wie für die bisherigen Inhalte, also die Anrede mit „Sie“, keine Gedankenstriche und keine Sätze, die mit einem Doppelpunkt eingeleitet werden.

### Bilder

Bilder liegen als WebP in `assets/bilder/<ordner>/<name>-<breite>.webp`, zum Beispiel `assets/bilder/produkte/displaykabel-asus-x72-1-400.webp`. Damit der Build ein Bild findet, braucht es einen Eintrag in einer der Bildlisten `src/daten/bilder-*.json` mit dem Schlüssel `<ordner>/<name>`, den vorhandenen Breiten und der Größe der breitesten Datei.

```json
"produkte/displaykabel-asus-x72-1": {"breiten": [400, 800], "w": 800, "h": 600}
```

Im Artikel verweisen Sie darauf mit `"bilder": [{"datei": "produkte/displaykabel-asus-x72-1", "alt": "Beschreibung des Bildes"}]`. Der Build setzt Breite, Höhe, `srcset` und Lazy Loading selbst.

WebP-Dateien erzeugen Sie zum Beispiel mit Python und Pillow (`pip install Pillow`). Das Beispiel passt ein Foto mit weißem Rand in das Format 4 zu 3 ein und speichert es in zwei Breiten ohne Metadaten.

```python
from PIL import Image, ImageOps

quelle = Image.open("foto.jpg").convert("RGB")
quelle = ImageOps.exif_transpose(quelle)
for breite in (400, 800):
    hoehe = breite * 3 // 4
    bild = ImageOps.pad(quelle, (breite, hoehe), color="white")
    bild.save(f"assets/bilder/produkte/mein-artikel-1-{breite}.webp", "WEBP", quality=80)
```

Für große Fotos im Format 3 zu 2 (Ordner `fotos/`) gelten die Breiten 480, 960 und 1600 Pixel. Statt `ImageOps.pad` passt `ImageOps.fit` das Foto durch Beschneiden ein. Erzeugen Sie keine Breite, für die das Original hochgerechnet werden müsste.

Bei Fotos fremder Urheber gehören in `src/daten/bilder-fotos.json` zusätzlich `motiv`, `titel`, `urheber`, `quelle_url`, `lizenz`, `lizenz_url` und `plattform`. Daraus entsteht die Seite `bildnachweise/`. Tragen Sie das Foto außerdem in `BILDQUELLEN.md` ein. Verwenden Sie nur Fotos mit geklärten Rechten, keine Bilder aus Bildagenturen und keine Bilder mit Wasserzeichen.

## Designs und Schriften

Die Demo-Leiste oben auf jeder Seite schaltet zwischen drei Designs, drei Schriften und der Markierung der Platzhalter um. Die Einstellungen lassen sich frei kombinieren, wirken sofort und bleiben beim Seitenwechsel erhalten (gespeichert im localStorage des Browsers).

| Einstellung | Wert | Bedeutung |
|---|---|---|
| Design | `a` | Werkstattgrün (Vorgabe) |
| Design | `b` | Hell und neutral |
| Design | `c` | Dunkel |
| Schrift | `1` | Space Grotesk und Inter (Vorgabe) |
| Schrift | `2` | Inter |
| Schrift | `3` | IBM Plex Sans |

Die Farben jedes Designs stehen in `assets/css/themen.css`, die Schriften in `assets/css/schriften.css`. Alle Schriften liegen lokal in `assets/fonts/`. Die gewählte Kombination wird für den echten Betrieb über die Attribute `data-design` und `data-schrift` am `html`-Element in `src/vorlagen/base.html` fest eingestellt.

## Demo-Leiste entfernen und echten Betrieb vorbereiten

Die Demo-Leiste entfernen Sie mit einer Zeile.

1. In `src/vorlagen/base.html` die Zeile `<script src="{{ root }}assets/js/demo.js"></script>` löschen.
2. Neu bauen mit `python3 src/build.py`.
3. Wer möchte, löscht danach auch `assets/js/demo.js`.

Für den echten Betrieb sind außerdem diese Schritte nötig.

* Den Demo-Hinweis im Fuß entfernen. Er steht in `src/vorlagen/base.html` (Absatz `fuss__demo`) und der Text in `src/daten/seite.json` unter `shop.demo_hinweis`.
* In `src/vorlagen/base.html` die Zeile `<meta name="robots" content="noindex, nofollow">` entfernen und in `src/build.py` die Prüfung auf `noindex` abschalten.
* `robots.txt` freigeben, zum Beispiel mit `Allow: /` und einem Verweis auf die Sitemap.
* Alle Musterdaten durch die echten Angaben ersetzen (`shop` in `src/daten/seite.json` und die Rechtstexte in `src/inhalte/`) und alle Platzhalter aus der Liste unten füllen.
* Die Rechtstexte rechtlich prüfen lassen. Es sind Mustertexte.
* Bestellung, Kasse und Formulare an ein echtes Shopsystem oder einen Formulardienst anbinden. In der Demo prüfen die Formulare nur die Eingaben.
* `shop.basis_url` in `src/daten/seite.json` auf die echte Adresse setzen, sie wird für Canonical, Sitemap und strukturierte Daten verwendet.

## Platzhalter

Diese Platzhalter muss der Inhaber füllen. Die Liste ist mit `python3 src/platzhalter.py --markdown` aus den Quellen erzeugt. Bei Änderungen an den Texten bitte neu erzeugen. Mit „Platzhalter markieren“ in der Demo-Leiste werden alle Platzhalter auf der Seite hervorgehoben.

| Platzhalter | Anzahl | Fundstellen (Auswahl) |
|---|---|---|
| `[1 bis 14 Werktage]` | 2 | `src/daten/seite.json`, `src/inhalte/agb.html` |
| `[2 bis 3 Werktagen]` | 2 | `src/daten/seite.json`, `src/inhalte/agb.html` |
| `[3 bis 5 Werktagen]` | 3 | `src/daten/seite.json`, `src/inhalte/agb.html`, `src/inhalte/versand-und-zahlung.html` |
| `[7 Tagen]` | 1 | `src/inhalte/agb.html` |
| `[abgedeckte Fehlerbilder]` | 3 | `src/daten/artikel.json` |
| `[angezeigte Spannungen]` | 1 | `src/daten/artikel.json` |
| `[Anrechnung des Diagnosepreises]` | 2 | `src/daten/artikel.json` |
| `[Antwortzeit]` | 3 | `src/daten/seite.json` |
| `[Ausstattung der Werkstatt]` | 1 | `src/daten/seite.json` |
| `[Bearbeitungszeit]` | 28 | `src/daten/artikel.json`, `src/daten/seite.json` |
| `[DIMM oder SO-DIMM]` | 2 | `src/daten/artikel.json` |
| `[Frist]` | 1 | `src/inhalte/agb.html` |
| `[Gründungsjahr]` | 1 | `src/daten/seite.json` |
| `[Hersteller]` | 2 | `src/daten/artikel.json` |
| `[Inhalt]` | 2 | `src/daten/artikel.json` |
| `[Kurzvorstellung des Inhabers mit Ausbildung und Erfahrung]` | 1 | `src/daten/seite.json` |
| `[Leistungsumfang im Detail]` | 6 | `src/daten/artikel.json` |
| `[Lieferumfang]` | 3 | `src/daten/artikel.json` |
| `[Lieferzeit]` | 8 | `src/daten/artikel.json` |
| `[Modelljahre und Platinennummern]` | 1 | `src/daten/artikel.json` |
| `[nach Vereinbarung]` | 1 | `src/daten/seite.json` |
| `[Nutzungsrecht für diese Bilder bestätigen oder eigene Fotos einsetzen]` | 1 | `src/daten/seite.json` |
| `[Ort der Widerrufsfunktion]` | 1 | `src/inhalte/widerruf.html` |
| `[Regelung bei abgelehntem Kostenvoranschlag]` | 2 | `src/daten/artikel.json` |
| `[Regelung bei nicht reparierbaren Geräten]` | 6 | `src/daten/artikel.json` |
| `[Regelung zur Anrechnung des Diagnosepreises auf die Reparatur]` | 1 | `src/inhalte/agb.html` |
| `[Typbezeichnung]` | 2 | `src/daten/artikel.json` |
| `[Uhrzeiten]` | 1 | `src/daten/seite.json` |
| `[unterstützte Varianten der PlayStation 4]` | 1 | `src/daten/artikel.json` |
| `[USt-IdNr.]` | 2 | `src/daten/seite.json`, `src/inhalte/impressum.html` |
| `[zuständige Datenschutz-Aufsichtsbehörde]` | 1 | `src/inhalte/datenschutz.html` |

## Veröffentlichung über GitHub Pages

Das Repository wird direkt aus der Repo-Wurzel veröffentlicht, ein eigener Build-Schritt auf GitHub ist nicht nötig. Die erzeugten Dateien werden deshalb mit eingecheckt.

1. Änderungen in `src/` vornehmen und mit `python3 src/build.py` neu bauen.
2. Quellen und erzeugte Dateien gemeinsam committen und pushen.
3. In den Einstellungen des Repositorys unter Pages als Quelle „Deploy from a branch“ mit dem gewünschten Branch und dem Ordner `/ (root)` wählen.
4. Die Datei `CNAME` enthält die eigene Domain `nr24.kazas.dev`. Beim DNS-Anbieter muss dafür ein CNAME-Eintrag auf `officeknight.github.io` zeigen. Ohne eigene Domain die Datei `CNAME` löschen, dann ist die Seite unter https://officeknight.github.io/nr24/ erreichbar.
5. Die leere Datei `.nojekyll` sorgt dafür, dass GitHub Pages alle Dateien unverändert ausliefert.

Weil alle Links relativ sind, funktioniert die Seite unter der eigenen Domain, im Unterordner `/nr24/` und lokal gleichermaßen.

## Lizenzen

* Herkunft, Urheber und Lizenz aller Fotos und Bilder stehen in [BILDQUELLEN.md](BILDQUELLEN.md) und auf der Seite `bildnachweise/`. Neun Fotos stehen unter CC BY 2.0 und verlangen eine Namensnennung, zwei Fotos stehen unter CC0. Die Produktfotos stammen aus dem bisherigen Shop.
* Die Schriften stehen unter der SIL Open Font License 1.1, Einzelheiten in [assets/fonts/LIZENZEN.md](assets/fonts/LIZENZEN.md).
* Texte, Gestaltung und Code dieser Demo wurden für Notebook Reparatur 24 erstellt.
