# Abnahmeprüfung https://schlecht.test/

Der Bericht prüft das Vorhandensein technischer und inhaltlicher Merkmale. Er ist keine Rechtsberatung.

| Angabe | Wert |
| --- | --- |
| Ziel | https://schlecht.test/ |
| Hauptadresse | https://schlecht.test/ |
| Modus | demo |
| Beginn | 2026-11-22T21:25:14+01:00 |
| Werkzeug | nr24-Abnahmepruefung 1.0.0 |
| HTTP-Abrufe | 19 |
| Erfasste HTML-Seiten | 5 |
| Gesamtergebnis | ❌ nicht bestanden |

## Übersicht

| Nr. | Prüfung | Ergebnis |
| --- | --- | --- |
| 1 | [Adressen und Weiterleitungen](#p1) | ❌ nicht bestanden |
| 2 | [TLS](#p2) | ❌ nicht bestanden |
| 3 | [Sicherheitsheader und Cookies](#p3) | ❌ nicht bestanden |
| 4 | [Vor Einwilligung](#p4) | ❌ nicht bestanden |
| 5 | [Auffindbarkeit](#p5) | ❌ nicht bestanden |
| 6 | [Strukturierte Daten](#p6) | ❌ nicht bestanden |
| 7 | [Pflichtangaben](#p7) | ❌ nicht bestanden |
| 8 | [Barrierefreiheit](#p8) | ❌ nicht bestanden |
| 9 | [Leistung](#p9) | ❌ nicht bestanden |
| 10 | [E-Mail-DNS](#p10) | ❌ nicht bestanden |

<a id="p1"></a>

## 1. Adressen und Weiterleitungen

Ergebnis **nicht bestanden**.

| Teilprüfung | Ergebnis |
| --- | --- |
| http leitet per 301 auf https um | ❌ nicht bestanden |
| Eine Hauptadresse für alle Varianten | ❌ nicht bestanden |
| Alte Adressen leiten per 301 weiter | ❌ nicht bestanden |

### 1. http leitet per 301 auf https um

| Art | Adresse | Fundstelle | Befund |
| --- | --- | --- | --- |
| Fehler | http://schlecht.test/ | Statuscode erster Antwort | Status 302 statt 301 |
| Fehler | http://www.schlecht.test/ | Statuscode erster Antwort | Status 302 statt 301 |

### 1. Eine Hauptadresse für alle Varianten

| Art | Adresse | Fundstelle | Befund |
| --- | --- | --- | --- |
| Fehler | http://schlecht.test/ | Weiterleitungskette | Zwischenschritt ohne 301, Kette http://schlecht.test/ (302) nach https://schlecht.test/ (200) |
| Fehler | http://www.schlecht.test/ | Endadresse | Endet auf https://www.schlecht.test/ statt auf https://schlecht.test/, Kette http://www.schlecht.test/ (302) nach https://www.schlecht.test/ (200) |
| Fehler | https://www.schlecht.test/ | Endadresse | Endet auf https://www.schlecht.test/ statt auf https://schlecht.test/, Kette https://www.schlecht.test/ (200) |
| Beleg | https://schlecht.test/ | Endadresse | Landet auf https://schlecht.test/ nach 0 Weiterleitung(en) |

### 1. Alte Adressen leiten per 301 weiter

| Art | Adresse | Fundstelle | Befund |
| --- | --- | --- | --- |
| Fehler | https://schlecht.test/alt/displaykabel.html | CSV Zeile 2 | Status 302 statt 301 |
| Fehler | https://schlecht.test/alt/agb.html | CSV Zeile 3 | Ziel https://schlecht.test/agb/ liefert 404 |

<a id="p2"></a>

## 2. TLS

Ergebnis **nicht bestanden**.

| Teilprüfung | Ergebnis |
| --- | --- |
| Nur TLS 1.2 und 1.3 werden angenommen | ❌ nicht bestanden |
| Zertifikat gilt noch mindestens 30 Tage | ❌ nicht bestanden |

### 2. Nur TLS 1.2 und 1.3 werden angenommen

| Art | Adresse | Fundstelle | Befund |
| --- | --- | --- | --- |
| Fehler | https://schlecht.test/ | schlecht.test:443 TLS 1.0 | Veraltete Version wird angenommen. Handschlag mit TLSv1 und ECDHE-RSA-AES256-SHA |
| Fehler | https://schlecht.test/ | schlecht.test:443 TLS 1.1 | Veraltete Version wird angenommen. Handschlag mit TLSv1.1 und ECDHE-RSA-AES256-SHA |
| Beleg | https://schlecht.test/ | schlecht.test:443 TLS 1.2 | Angenommen. Handschlag mit TLSv1.2 und ECDHE-RSA-AES256-GCM-SHA384 |
| Beleg | https://schlecht.test/ | schlecht.test:443 TLS 1.3 | Angenommen. Handschlag mit TLSv1.3 und TLS_AES_256_GCM_SHA384 |

### 2. Zertifikat gilt noch mindestens 30 Tage

| Art | Adresse | Fundstelle | Befund |
| --- | --- | --- | --- |
| Fehler | https://schlecht.test/ | Zertifikat schlecht.test | Gültig bis Dec  2 20:24:16 2026 GMT, noch 10 Tage, ausgestellt von Beispiel Test-CA, weniger als 30 Tage |
| Fehler | https://www.schlecht.test/ | Zertifikat www.schlecht.test | Gültig bis Dec  2 20:24:16 2026 GMT, noch 10 Tage, ausgestellt von Beispiel Test-CA, weniger als 30 Tage |

<a id="p3"></a>

## 3. Sicherheitsheader und Cookies

Ergebnis **nicht bestanden**.

| Teilprüfung | Ergebnis |
| --- | --- |
| HSTS gesetzt | ❌ nicht bestanden |
| Content-Security-Policy gesetzt | ❌ nicht bestanden |
| X-Content-Type-Options gesetzt | ❌ nicht bestanden |
| Referrer-Policy gesetzt | ❌ nicht bestanden |
| Permissions-Policy gesetzt | ❌ nicht bestanden |
| Schutz gegen Einbetten gesetzt | ❌ nicht bestanden |
| Cookies tragen Secure, HttpOnly und SameSite | ❌ nicht bestanden |

### 3. HSTS gesetzt

| Art | Adresse | Fundstelle | Befund |
| --- | --- | --- | --- |
| Fehler | https://schlecht.test/ | Antwortheader Strict-Transport-Security | Header Strict-Transport-Security fehlt |
| Fehler | https://schlecht.test/ersatzteile/displays/kabel/ | Antwortheader Strict-Transport-Security | Header Strict-Transport-Security fehlt |
| Fehler | https://schlecht.test/impressum/ | Antwortheader Strict-Transport-Security | Header Strict-Transport-Security fehlt |
| Fehler | https://schlecht.test/datenschutz/ | Antwortheader Strict-Transport-Security | Header Strict-Transport-Security fehlt |
| Fehler | https://schlecht.test/kasse/ | Antwortheader Strict-Transport-Security | Header Strict-Transport-Security fehlt |

### 3. Content-Security-Policy gesetzt

| Art | Adresse | Fundstelle | Befund |
| --- | --- | --- | --- |
| Fehler | https://schlecht.test/ | Antwortheader Content-Security-Policy | Header Content-Security-Policy fehlt |
| Fehler | https://schlecht.test/ersatzteile/displays/kabel/ | Antwortheader Content-Security-Policy | Header Content-Security-Policy fehlt |
| Fehler | https://schlecht.test/impressum/ | Antwortheader Content-Security-Policy | Header Content-Security-Policy fehlt |
| Fehler | https://schlecht.test/datenschutz/ | Antwortheader Content-Security-Policy | Header Content-Security-Policy fehlt |
| Fehler | https://schlecht.test/kasse/ | Antwortheader Content-Security-Policy | Header Content-Security-Policy fehlt |

### 3. X-Content-Type-Options gesetzt

| Art | Adresse | Fundstelle | Befund |
| --- | --- | --- | --- |
| Fehler | https://schlecht.test/ | Antwortheader X-Content-Type-Options | Header X-Content-Type-Options fehlt |
| Fehler | https://schlecht.test/ersatzteile/displays/kabel/ | Antwortheader X-Content-Type-Options | Header X-Content-Type-Options fehlt |
| Fehler | https://schlecht.test/impressum/ | Antwortheader X-Content-Type-Options | Header X-Content-Type-Options fehlt |
| Fehler | https://schlecht.test/datenschutz/ | Antwortheader X-Content-Type-Options | Header X-Content-Type-Options fehlt |
| Fehler | https://schlecht.test/kasse/ | Antwortheader X-Content-Type-Options | Header X-Content-Type-Options fehlt |

### 3. Referrer-Policy gesetzt

| Art | Adresse | Fundstelle | Befund |
| --- | --- | --- | --- |
| Fehler | https://schlecht.test/ | Antwortheader Referrer-Policy | Header Referrer-Policy fehlt |
| Fehler | https://schlecht.test/ersatzteile/displays/kabel/ | Antwortheader Referrer-Policy | Header Referrer-Policy fehlt |
| Fehler | https://schlecht.test/impressum/ | Antwortheader Referrer-Policy | Header Referrer-Policy fehlt |
| Fehler | https://schlecht.test/datenschutz/ | Antwortheader Referrer-Policy | Header Referrer-Policy fehlt |
| Fehler | https://schlecht.test/kasse/ | Antwortheader Referrer-Policy | Header Referrer-Policy fehlt |

### 3. Permissions-Policy gesetzt

| Art | Adresse | Fundstelle | Befund |
| --- | --- | --- | --- |
| Fehler | https://schlecht.test/ | Antwortheader Permissions-Policy | Header Permissions-Policy fehlt |
| Fehler | https://schlecht.test/ersatzteile/displays/kabel/ | Antwortheader Permissions-Policy | Header Permissions-Policy fehlt |
| Fehler | https://schlecht.test/impressum/ | Antwortheader Permissions-Policy | Header Permissions-Policy fehlt |
| Fehler | https://schlecht.test/datenschutz/ | Antwortheader Permissions-Policy | Header Permissions-Policy fehlt |
| Fehler | https://schlecht.test/kasse/ | Antwortheader Permissions-Policy | Header Permissions-Policy fehlt |

### 3. Schutz gegen Einbetten gesetzt

| Art | Adresse | Fundstelle | Befund |
| --- | --- | --- | --- |
| Fehler | https://schlecht.test/ | Antwortheader X-Frame-Options oder CSP frame-ancestors | Weder X-Frame-Options noch CSP frame-ancestors im Header |
| Fehler | https://schlecht.test/ersatzteile/displays/kabel/ | Antwortheader X-Frame-Options oder CSP frame-ancestors | Weder X-Frame-Options noch CSP frame-ancestors im Header |
| Fehler | https://schlecht.test/impressum/ | Antwortheader X-Frame-Options oder CSP frame-ancestors | Weder X-Frame-Options noch CSP frame-ancestors im Header |
| Fehler | https://schlecht.test/datenschutz/ | Antwortheader X-Frame-Options oder CSP frame-ancestors | Weder X-Frame-Options noch CSP frame-ancestors im Header |
| Fehler | https://schlecht.test/kasse/ | Antwortheader X-Frame-Options oder CSP frame-ancestors | Weder X-Frame-Options noch CSP frame-ancestors im Header |

### 3. Cookies tragen Secure, HttpOnly und SameSite

| Art | Adresse | Fundstelle | Befund |
| --- | --- | --- | --- |
| Fehler | https://schlecht.test/ | Set-Cookie sitzung | Secure fehlt, SameSite fehlt, HttpOnly fehlt bei einem Sitzungs- oder Anmeldecookie |
| Fehler | https://schlecht.test/ | Set-Cookie werbung_id | Secure fehlt, SameSite fehlt |
| Hinweis | https://schlecht.test/ | Set-Cookie werbung_id | Ohne HttpOnly, für Skripte lesbar. Bitte prüfen, ob das nötig ist |

### 3. Hinweise

| Adresse | Fundstelle | Hinweis |
| --- | --- | --- |
| https://schlecht.test/ | Umfang | Geprüft wurden Cookies aus Set-Cookie-Headern der Endantworten. Per Skript gesetzte Cookies stehen in Prüfung 4 |

<a id="p4"></a>

## 4. Vor Einwilligung

Ergebnis **nicht bestanden**.

| Teilprüfung | Ergebnis |
| --- | --- |
| Keine Anfragen an fremde Hosts | ❌ nicht bestanden |
| Nur technisch nötige Cookies | ❌ nicht bestanden |

### 4. Keine Anfragen an fremde Hosts

| Art | Adresse | Fundstelle | Befund |
| --- | --- | --- | --- |
| Fehler | https://schlecht.test/ | Anfrage script an drittanbieter.test | GET https://drittanbieter.test/tracker.js |
| Fehler | https://schlecht.test/ | Anfrage fetch an drittanbieter.test | GET https://drittanbieter.test/pixel.gif |
| Beleg | https://schlecht.test/ersatzteile/displays/kabel/ | Netzwerkanfragen | 3 Anfragen, alle an eigene Hosts |
| Beleg | https://schlecht.test/impressum/ | Netzwerkanfragen | 2 Anfragen, alle an eigene Hosts |
| Beleg | https://schlecht.test/datenschutz/ | Netzwerkanfragen | 2 Anfragen, alle an eigene Hosts |
| Beleg | https://schlecht.test/kasse/ | Netzwerkanfragen | 2 Anfragen, alle an eigene Hosts |

### 4. Nur technisch nötige Cookies

| Art | Adresse | Fundstelle | Befund |
| --- | --- | --- | --- |
| Fehler | https://schlecht.test/ | Cookie werbung_id auf schlecht.test | Nicht als technisch nötig eingestuft, gesetzt ohne Einwilligung |
| Fehler | https://schlecht.test/ | Cookie dritt_id auf drittanbieter.test | Cookie eines fremden Hosts vor Einwilligung |
| Fehler | https://schlecht.test/ | Cookie _verfolgung auf schlecht.test | Nicht als technisch nötig eingestuft, gesetzt ohne Einwilligung |
| Fehler | https://schlecht.test/ersatzteile/displays/kabel/ | Cookie werbung_id auf schlecht.test | Nicht als technisch nötig eingestuft, gesetzt ohne Einwilligung |
| Fehler | https://schlecht.test/impressum/ | Cookie werbung_id auf schlecht.test | Nicht als technisch nötig eingestuft, gesetzt ohne Einwilligung |
| Fehler | https://schlecht.test/datenschutz/ | Cookie werbung_id auf schlecht.test | Nicht als technisch nötig eingestuft, gesetzt ohne Einwilligung |
| Fehler | https://schlecht.test/kasse/ | Cookie werbung_id auf schlecht.test | Nicht als technisch nötig eingestuft, gesetzt ohne Einwilligung |
| Beleg | https://schlecht.test/ | Cookie sitzung auf schlecht.test | Steht auf der Liste technisch nötiger Cookies |
| Beleg | https://schlecht.test/ersatzteile/displays/kabel/ | Cookie sitzung auf schlecht.test | Steht auf der Liste technisch nötiger Cookies |
| Beleg | https://schlecht.test/impressum/ | Cookie sitzung auf schlecht.test | Steht auf der Liste technisch nötiger Cookies |
| Beleg | https://schlecht.test/datenschutz/ | Cookie sitzung auf schlecht.test | Steht auf der Liste technisch nötiger Cookies |
| Beleg | https://schlecht.test/kasse/ | Cookie sitzung auf schlecht.test | Steht auf der Liste technisch nötiger Cookies |

### 4. Hinweise

| Adresse | Fundstelle | Hinweis |
| --- | --- | --- |
| https://schlecht.test/ | Verfahren | Jede Seite wurde in einem neu gestarteten Chromium 157.0.8103.78 geladen, ohne Klick und ohne gespeicherte Daten. Erfasst wurde nach dem Laden und einer kurzen Wartezeit |

<a id="p5"></a>

## 5. Auffindbarkeit

Ergebnis **nicht bestanden**.

| Teilprüfung | Ergebnis |
| --- | --- |
| Eigener Titel je Seite | ❌ nicht bestanden |
| Meta-Beschreibung vorhanden | ❌ nicht bestanden |
| Genau eine H1 | ❌ nicht bestanden |
| Canonical vorhanden | ❌ nicht bestanden |
| lang-Attribut gesetzt | ❌ nicht bestanden |
| Bilder mit Alt-Text und festen Maßen | ❌ nicht bestanden |
| noindex passend zum Modus demo | ❌ nicht bestanden |
| Keine toten internen Links | ❌ nicht bestanden |
| sitemap.xml vorhanden und gültig | ❌ nicht bestanden |
| robots.txt vorhanden | ❌ nicht bestanden |

### 5. Eigener Titel je Seite

| Art | Adresse | Fundstelle | Befund |
| --- | --- | --- | --- |
| Fehler | https://schlecht.test/ | <title> | Titel Shop kommt auf 2 Seiten vor |
| Fehler | https://schlecht.test/ersatzteile/displays/kabel/ | <title> | Titel Shop kommt auf 2 Seiten vor |
| Beleg | https://schlecht.test/impressum/ | <title> | Impressum |
| Beleg | https://schlecht.test/datenschutz/ | <title> | Datenschutz |
| Beleg | https://schlecht.test/kasse/ | <title> | Kasse |

### 5. Meta-Beschreibung vorhanden

| Art | Adresse | Fundstelle | Befund |
| --- | --- | --- | --- |
| Fehler | https://schlecht.test/ | meta name="description" | Fehlt oder ist leer |
| Beleg | https://schlecht.test/ersatzteile/displays/kabel/ | meta name="description" | 12 Zeichen |
| Beleg | https://schlecht.test/impressum/ | meta name="description" | 9 Zeichen |
| Beleg | https://schlecht.test/datenschutz/ | meta name="description" | 11 Zeichen |
| Beleg | https://schlecht.test/kasse/ | meta name="description" | 5 Zeichen |

### 5. Genau eine H1

| Art | Adresse | Fundstelle | Befund |
| --- | --- | --- | --- |
| Fehler | https://schlecht.test/ | <h1> | 2 Überschriften erster Ebene (Willkommen und Notebook-Ersatzteile) |
| Beleg | https://schlecht.test/ersatzteile/displays/kabel/ | <h1> | Displaykabel für Asus X72 |
| Beleg | https://schlecht.test/impressum/ | <h1> | Impressum |
| Beleg | https://schlecht.test/datenschutz/ | <h1> | Datenschutz |
| Beleg | https://schlecht.test/kasse/ | <h1> | Kasse |

### 5. Canonical vorhanden

| Art | Adresse | Fundstelle | Befund |
| --- | --- | --- | --- |
| Fehler | https://schlecht.test/ | link rel="canonical" | 0 Angaben statt genau einer |
| Fehler | https://schlecht.test/ersatzteile/displays/kabel/ | link rel="canonical" | /ersatzteile/displays/kabel/ ist keine absolute Adresse |
| Fehler | https://schlecht.test/impressum/ | link rel="canonical" | https://andere-domain.example/impressum/ zeigt auf einen anderen Host als schlecht.test |
| Beleg | https://schlecht.test/datenschutz/ | link rel="canonical" | https://schlecht.test/datenschutz/ |
| Beleg | https://schlecht.test/kasse/ | link rel="canonical" | https://schlecht.test/kasse/ |

### 5. lang-Attribut gesetzt

| Art | Adresse | Fundstelle | Befund |
| --- | --- | --- | --- |
| Fehler | https://schlecht.test/ | <html lang> | Attribut lang fehlt |
| Beleg | https://schlecht.test/ersatzteile/displays/kabel/ | <html lang> | de |
| Beleg | https://schlecht.test/impressum/ | <html lang> | de |
| Beleg | https://schlecht.test/datenschutz/ | <html lang> | de |
| Beleg | https://schlecht.test/kasse/ | <html lang> | de |

### 5. Bilder mit Alt-Text und festen Maßen

| Art | Adresse | Fundstelle | Befund |
| --- | --- | --- | --- |
| Fehler | https://schlecht.test/ | <img src=/assets/kabel.svg> | Es fehlt alt, width und height |
| Fehler | https://schlecht.test/ersatzteile/displays/kabel/ | <img src=/assets/kabel.svg> | Es fehlt width und height |

### 5. noindex passend zum Modus demo

| Art | Adresse | Fundstelle | Befund |
| --- | --- | --- | --- |
| Fehler | https://schlecht.test/ | meta robots und X-Robots-Tag | Kein noindex, im Modus demo Pflicht |
| Beleg | https://schlecht.test/ersatzteile/displays/kabel/ | meta robots | meta robots noindex, nofollow |
| Beleg | https://schlecht.test/impressum/ | meta robots | meta robots noindex, nofollow |
| Beleg | https://schlecht.test/datenschutz/ | meta robots | meta robots noindex, nofollow |
| Beleg | https://schlecht.test/kasse/ | meta robots | meta robots noindex, nofollow |

### 5. Keine toten internen Links

| Art | Adresse | Fundstelle | Befund |
| --- | --- | --- | --- |
| Fehler | https://schlecht.test/ | <a href="/gibt-es-nicht/"> | Ziel https://schlecht.test/gibt-es-nicht/ liefert 404 |
| Beleg | https://schlecht.test/ | <a href> | 14 interne Links auf 5 Seiten geprüft |

### 5. sitemap.xml vorhanden und gültig

| Art | Adresse | Fundstelle | Befund |
| --- | --- | --- | --- |
| Fehler | https://schlecht.test/sitemap.xml | Sitemap | Status 404 |

### 5. robots.txt vorhanden

| Art | Adresse | Fundstelle | Befund |
| --- | --- | --- | --- |
| Fehler | https://schlecht.test/robots.txt | robots.txt | Liefert 404 |

<a id="p6"></a>

## 6. Strukturierte Daten

Ergebnis **nicht bestanden**.

| Teilprüfung | Ergebnis |
| --- | --- |
| JSON-LD lesbar | ❌ nicht bestanden |
| Artikelseiten mit Product, Preis, Währung und Verfügbarkeit | ❌ nicht bestanden |
| Artikelseiten mit BreadcrumbList | ❌ nicht bestanden |
| FAQ-Bereiche mit FAQPage | ❌ nicht bestanden |
| Startseite mit Firmendaten | ❌ nicht bestanden |

### 6. JSON-LD lesbar

| Art | Adresse | Fundstelle | Befund |
| --- | --- | --- | --- |
| Fehler | https://schlecht.test/ | script application/ld+json Nr. 1 | JSON nicht lesbar in Zeile 2, Spalte 84 (Illegal trailing comma before end of object) |

### 6. Artikelseiten mit Product, Preis, Währung und Verfügbarkeit

| Art | Adresse | Fundstelle | Befund |
| --- | --- | --- | --- |
| Fehler | https://schlecht.test/ersatzteile/displays/kabel/ | JSON-LD Product | Artikelseite (Pfad passt zu ^/ersatzteile/[^/]+/[^/]+/$) ohne Product |

### 6. Artikelseiten mit BreadcrumbList

| Art | Adresse | Fundstelle | Befund |
| --- | --- | --- | --- |
| Fehler | https://schlecht.test/ersatzteile/displays/kabel/ | JSON-LD BreadcrumbList | Artikelseite ohne BreadcrumbList |

### 6. FAQ-Bereiche mit FAQPage

| Art | Adresse | Fundstelle | Befund |
| --- | --- | --- | --- |
| Fehler | https://schlecht.test/ | Überschrift FAQ | FAQ-Bereich ohne FAQPage |

### 6. Startseite mit Firmendaten

| Art | Adresse | Fundstelle | Befund |
| --- | --- | --- | --- |
| Fehler | https://schlecht.test/ | JSON-LD | Keine Firmendaten (Organization, LocalBusiness oder Store) |

<a id="p7"></a>

## 7. Pflichtangaben

Ergebnis **nicht bestanden**.

| Teilprüfung | Ergebnis |
| --- | --- |
| Impressum von jeder Seite erreichbar | ✅ bestanden |
| Datenschutz von jeder Seite erreichbar | ✅ bestanden |
| AGB von jeder Seite erreichbar | ❌ nicht bestanden |
| Widerruf von jeder Seite erreichbar | ❌ nicht bestanden |
| Widerrufsfunktion auffindbar | ❌ nicht bestanden |
| Preise mit Hinweis auf Mehrwertsteuer und Versand | ❌ nicht bestanden |
| Bestellknopf eindeutig beschriftet | ❌ nicht bestanden |

### 7. Impressum von jeder Seite erreichbar

| Art | Adresse | Fundstelle | Befund |
| --- | --- | --- | --- |
| Beleg | https://schlecht.test/impressum/ | Link Impressum | Von 5 von 5 Seiten verlinkt, Status 200 |

### 7. Datenschutz von jeder Seite erreichbar

| Art | Adresse | Fundstelle | Befund |
| --- | --- | --- | --- |
| Beleg | https://schlecht.test/datenschutz/ | Link Datenschutz | Von 5 von 5 Seiten verlinkt, Status 200 |

### 7. AGB von jeder Seite erreichbar

| Art | Adresse | Fundstelle | Befund |
| --- | --- | --- | --- |
| Fehler | https://schlecht.test/ | Link AGB | Kein Link auf dieser Seite gefunden |
| Fehler | https://schlecht.test/ersatzteile/displays/kabel/ | Link AGB | Kein Link auf dieser Seite gefunden |
| Fehler | https://schlecht.test/impressum/ | Link AGB | Kein Link auf dieser Seite gefunden |
| Fehler | https://schlecht.test/datenschutz/ | Link AGB | Kein Link auf dieser Seite gefunden |
| Fehler | https://schlecht.test/kasse/ | Link AGB | Kein Link auf dieser Seite gefunden |

### 7. Widerruf von jeder Seite erreichbar

| Art | Adresse | Fundstelle | Befund |
| --- | --- | --- | --- |
| Fehler | https://schlecht.test/ | Link Widerruf | Kein Link auf dieser Seite gefunden |
| Fehler | https://schlecht.test/ersatzteile/displays/kabel/ | Link Widerruf | Kein Link auf dieser Seite gefunden |
| Fehler | https://schlecht.test/impressum/ | Link Widerruf | Kein Link auf dieser Seite gefunden |
| Fehler | https://schlecht.test/datenschutz/ | Link Widerruf | Kein Link auf dieser Seite gefunden |
| Fehler | https://schlecht.test/kasse/ | Link Widerruf | Kein Link auf dieser Seite gefunden |

### 7. Widerrufsfunktion auffindbar

| Art | Adresse | Fundstelle | Befund |
| --- | --- | --- | --- |
| Fehler | https://schlecht.test/ | Links und Knöpfe | Auf 5 Seiten kein Link oder Knopf wie Vertrag widerrufen gefunden |

### 7. Preise mit Hinweis auf Mehrwertsteuer und Versand

| Art | Adresse | Fundstelle | Befund |
| --- | --- | --- | --- |
| Fehler | https://schlecht.test/ | Preis 19,90 € | Kein Hinweis auf Mehrwertsteuer und Versandkosten |
| Fehler | https://schlecht.test/ersatzteile/displays/kabel/ | Preis 11,90 € | Kein Hinweis auf Versandkosten |

### 7. Bestellknopf eindeutig beschriftet

| Art | Adresse | Fundstelle | Befund |
| --- | --- | --- | --- |
| Fehler | https://schlecht.test/kasse/ | Knopf Bestellen | Beschriftung nicht eindeutig, etwa zahlungspflichtig bestellen |

### 7. Hinweise

| Adresse | Fundstelle | Hinweis |
| --- | --- | --- |
| https://schlecht.test/ | Umfang | Geprüft wird nur das Vorhandensein, nicht die inhaltliche oder rechtliche Richtigkeit |

<a id="p8"></a>

## 8. Barrierefreiheit

Ergebnis **nicht bestanden**.

| Teilprüfung | Ergebnis |
| --- | --- |
| axe-core WCAG 2.2 A und AA | ❌ nicht bestanden |
| Zoomen am Handy nicht gesperrt | ❌ nicht bestanden |

### 8. axe-core WCAG 2.2 A und AA

| Art | Adresse | Fundstelle | Befund |
| --- | --- | --- | --- |
| Fehler | https://schlecht.test/ | color-contrast (serious) .blass | Elements must meet minimum color contrast ratio thresholds. <p class="blass">Displaykabel für Asus X72 für 19,90 €</p> |
| Fehler | https://schlecht.test/ | html-has-lang (serious) html | <html> element must have a lang attribute. <html> |
| Fehler | https://schlecht.test/ | image-alt (critical) img | Images must have alternative text. <img src="/assets/kabel.svg"> |
| Fehler | https://schlecht.test/ | meta-viewport (moderate) meta[name="viewport"] | Zooming and scaling must not be disabled. <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no"> |
| Beleg | https://schlecht.test/ersatzteile/displays/kabel/ | axe-core | Keine Verstöße |
| Beleg | https://schlecht.test/impressum/ | axe-core | Keine Verstöße |
| Beleg | https://schlecht.test/datenschutz/ | axe-core | Keine Verstöße |
| Beleg | https://schlecht.test/kasse/ | axe-core | Keine Verstöße |

### 8. Zoomen am Handy nicht gesperrt

| Art | Adresse | Fundstelle | Befund |
| --- | --- | --- | --- |
| Fehler | https://schlecht.test/ | meta name="viewport" | Zoomen gesperrt durch user-scalable=no |
| Beleg | https://schlecht.test/ersatzteile/displays/kabel/ | meta name="viewport" | width=device-width, initial-scale=1 |
| Beleg | https://schlecht.test/impressum/ | meta name="viewport" | width=device-width, initial-scale=1 |
| Beleg | https://schlecht.test/datenschutz/ | meta name="viewport" | width=device-width, initial-scale=1 |
| Beleg | https://schlecht.test/kasse/ | meta name="viewport" | width=device-width, initial-scale=1 |

### 8. Hinweise

| Adresse | Fundstelle | Hinweis |
| --- | --- | --- |
| https://schlecht.test/ | Werkzeug | axe-core 4.14.0 mit den Regelgruppen wcag2a, wcag2aa, wcag21a, wcag21aa, wcag22a, wcag22aa. Automatische Tests finden nur einen Teil der Barrieren, eine Prüfung von Hand bleibt nötig |

<a id="p9"></a>

## 9. Leistung

Ergebnis **nicht bestanden**.

| Teilprüfung | Ergebnis |
| --- | --- |
| Übertragene Daten je Seite unter 0,5 MB | ❌ nicht bestanden |
| Größte Dateien | ✅ bestanden |

### 9. Übertragene Daten je Seite unter 0,5 MB

| Art | Adresse | Fundstelle | Befund |
| --- | --- | --- | --- |
| Fehler | https://schlecht.test/ | Übertragene Daten | 0,603 MB in 6 Anfragen, größte Datei https://schlecht.test/assets/gross.js mit 0,600 MB, Grenze 0,500 MB |
| Beleg | https://schlecht.test/ersatzteile/displays/kabel/ | Übertragene Daten | 0,002 MB in 3 Anfragen, größte Datei https://schlecht.test/ersatzteile/displays/kabel/ mit 0,001 MB |
| Beleg | https://schlecht.test/impressum/ | Übertragene Daten | 0,001 MB in 2 Anfragen, größte Datei https://schlecht.test/impressum/ mit 0,001 MB |
| Beleg | https://schlecht.test/datenschutz/ | Übertragene Daten | 0,001 MB in 2 Anfragen, größte Datei https://schlecht.test/datenschutz/ mit 0,001 MB |
| Beleg | https://schlecht.test/kasse/ | Übertragene Daten | 0,001 MB in 2 Anfragen, größte Datei https://schlecht.test/kasse/ mit 0,001 MB |

### 9. Größte Dateien

| Art | Adresse | Fundstelle | Befund |
| --- | --- | --- | --- |
| Beleg | https://schlecht.test/ | Datei https://schlecht.test/assets/gross.js | 0,600 MB |
| Beleg | https://schlecht.test/ | Datei https://schlecht.test/ | 0,001 MB |
| Beleg | https://schlecht.test/kasse/ | Datei https://schlecht.test/kasse/ | 0,001 MB |
| Beleg | https://schlecht.test/ersatzteile/displays/kabel/ | Datei https://schlecht.test/ersatzteile/displays/kabel/ | 0,001 MB |
| Beleg | https://schlecht.test/impressum/ | Datei https://schlecht.test/impressum/ | 0,001 MB |
| Beleg | https://schlecht.test/datenschutz/ | Datei https://schlecht.test/datenschutz/ | 0,001 MB |
| Beleg | https://schlecht.test/ | Datei https://schlecht.test/assets/kabel.svg | 0,001 MB |
| Beleg | https://schlecht.test/ | Datei https://drittanbieter.test/tracker.js | 0,000 MB |
| Beleg | https://schlecht.test/ | Datei https://schlecht.test/assets/style.css | 0,000 MB |
| Beleg | https://schlecht.test/ | Datei https://drittanbieter.test/pixel.gif | 0,000 MB |

### 9. Hinweise

| Adresse | Fundstelle | Hinweis |
| --- | --- | --- |
| https://schlecht.test/ | Zahl der Anfragen | Je Seite zwischen 2 und 6, im Mittel 3,0 |
| https://schlecht.test/ | Messung | Gezählt werden Header und Inhalt jeder Antwort beim ersten Laden ohne Zwischenspeicher. Die Grenze beträgt 500000 Byte |
| https://schlecht.test/ | Lighthouse | Lighthouse ist nicht installiert und wurde deshalb nicht ausgeführt |

<a id="p10"></a>

## 10. E-Mail-DNS

Ergebnis **nicht bestanden**.

| Teilprüfung | Ergebnis |
| --- | --- |
| SPF endet auf -all oder ~all | ❌ nicht bestanden |
| DMARC vorhanden | ❌ nicht bestanden |
| DKIM unter dem angegebenen Selektor | ❌ nicht bestanden |

### 10. SPF endet auf -all oder ~all

| Art | Adresse | Fundstelle | Befund |
| --- | --- | --- | --- |
| Fehler | schlecht.test | TXT schlecht.test | v=spf1 a mx +all endet auf +all statt auf -all oder ~all |

### 10. DMARC vorhanden

| Art | Adresse | Fundstelle | Befund |
| --- | --- | --- | --- |
| Fehler | schlecht.test | TXT _dmarc.schlecht.test | Kein Eintrag mit v=DMARC1 |

### 10. DKIM unter dem angegebenen Selektor

| Art | Adresse | Fundstelle | Befund |
| --- | --- | --- | --- |
| Fehler | schlecht.test | TXT mail._domainkey.schlecht.test | Schlüssel p= ist leer, der Schlüssel ist widerrufen |

### 10. Hinweise

| Adresse | Fundstelle | Hinweis |
| --- | --- | --- |
| schlecht.test | Abfrage | Domain schlecht.test, abgefragt über Nameserver 127.0.0.1:5353 |
