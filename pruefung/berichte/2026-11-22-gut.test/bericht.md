# Abnahmeprüfung https://gut.test/

Der Bericht prüft das Vorhandensein technischer und inhaltlicher Merkmale. Er ist keine Rechtsberatung.

| Angabe | Wert |
| --- | --- |
| Ziel | https://gut.test/ |
| Hauptadresse | https://gut.test/ |
| Modus | demo |
| Beginn | 2026-11-22T21:24:17+01:00 |
| Werkzeug | nr24-Abnahmepruefung 1.0.0 |
| HTTP-Abrufe | 27 |
| Erfasste HTML-Seiten | 11 |
| Gesamtergebnis | ✅ bestanden |

## Übersicht

| Nr. | Prüfung | Ergebnis |
| --- | --- | --- |
| 1 | [Adressen und Weiterleitungen](#p1) | ✅ bestanden |
| 2 | [TLS](#p2) | ✅ bestanden |
| 3 | [Sicherheitsheader und Cookies](#p3) | ✅ bestanden |
| 4 | [Vor Einwilligung](#p4) | ✅ bestanden |
| 5 | [Auffindbarkeit](#p5) | ✅ bestanden |
| 6 | [Strukturierte Daten](#p6) | ✅ bestanden |
| 7 | [Pflichtangaben](#p7) | ✅ bestanden |
| 8 | [Barrierefreiheit](#p8) | ✅ bestanden |
| 9 | [Leistung](#p9) | ✅ bestanden |
| 10 | [E-Mail-DNS](#p10) | ✅ bestanden |

<a id="p1"></a>

## 1. Adressen und Weiterleitungen

Ergebnis **bestanden**.

| Teilprüfung | Ergebnis |
| --- | --- |
| http leitet per 301 auf https um | ✅ bestanden |
| Eine Hauptadresse für alle Varianten | ✅ bestanden |
| Alte Adressen leiten per 301 weiter | ✅ bestanden |

### 1. http leitet per 301 auf https um

| Art | Adresse | Fundstelle | Befund |
| --- | --- | --- | --- |
| Beleg | http://gut.test/ | Location | 301 nach https://gut.test/ |
| Beleg | http://www.gut.test/ | Location | 301 nach https://gut.test/ |

### 1. Eine Hauptadresse für alle Varianten

| Art | Adresse | Fundstelle | Befund |
| --- | --- | --- | --- |
| Beleg | http://gut.test/ | Endadresse | Landet auf https://gut.test/ nach 1 Weiterleitung(en) |
| Beleg | http://www.gut.test/ | Endadresse | Landet auf https://gut.test/ nach 1 Weiterleitung(en) |
| Beleg | https://gut.test/ | Endadresse | Landet auf https://gut.test/ nach 0 Weiterleitung(en) |
| Beleg | https://www.gut.test/ | Endadresse | Landet auf https://gut.test/ nach 1 Weiterleitung(en) |

### 1. Alte Adressen leiten per 301 weiter

| Art | Adresse | Fundstelle | Befund |
| --- | --- | --- | --- |
| Beleg | https://gut.test/alt/displaykabel.html | CSV Zeile 2 | 301 nach https://gut.test/ersatzteile/displays/displaykabel-x72/, Ziel liefert 200 |
| Beleg | https://gut.test/shop/index.php | CSV Zeile 3 | 301 nach https://gut.test/, Ziel liefert 200 |
| Beleg | https://gut.test/alt/agb.html | CSV Zeile 4 | 301 nach https://gut.test/agb/, Ziel liefert 200 |

<a id="p2"></a>

## 2. TLS

Ergebnis **bestanden**.

| Teilprüfung | Ergebnis |
| --- | --- |
| Nur TLS 1.2 und 1.3 werden angenommen | ✅ bestanden |
| Zertifikat gilt noch mindestens 30 Tage | ✅ bestanden |

### 2. Nur TLS 1.2 und 1.3 werden angenommen

| Art | Adresse | Fundstelle | Befund |
| --- | --- | --- | --- |
| Beleg | https://gut.test/ | gut.test:443 TLS 1.0 | Abgelehnt (TLSV1_ALERT_PROTOCOL_VERSION) |
| Beleg | https://gut.test/ | gut.test:443 TLS 1.1 | Abgelehnt (TLSV1_ALERT_PROTOCOL_VERSION) |
| Beleg | https://gut.test/ | gut.test:443 TLS 1.2 | Angenommen. Handschlag mit TLSv1.2 und ECDHE-RSA-AES256-GCM-SHA384 |
| Beleg | https://gut.test/ | gut.test:443 TLS 1.3 | Angenommen. Handschlag mit TLSv1.3 und TLS_AES_256_GCM_SHA384 |

### 2. Zertifikat gilt noch mindestens 30 Tage

| Art | Adresse | Fundstelle | Befund |
| --- | --- | --- | --- |
| Beleg | https://gut.test/ | Zertifikat gut.test | Gültig bis Nov 22 20:24:16 2027 GMT, noch 365 Tage, ausgestellt von Beispiel Test-CA |
| Beleg | https://www.gut.test/ | Zertifikat www.gut.test | Gültig bis Nov 22 20:24:16 2027 GMT, noch 365 Tage, ausgestellt von Beispiel Test-CA |

<a id="p3"></a>

## 3. Sicherheitsheader und Cookies

Ergebnis **bestanden**.

| Teilprüfung | Ergebnis |
| --- | --- |
| HSTS gesetzt | ✅ bestanden |
| Content-Security-Policy gesetzt | ✅ bestanden |
| X-Content-Type-Options gesetzt | ✅ bestanden |
| Referrer-Policy gesetzt | ✅ bestanden |
| Permissions-Policy gesetzt | ✅ bestanden |
| Schutz gegen Einbetten gesetzt | ✅ bestanden |
| Cookies tragen Secure, HttpOnly und SameSite | ✅ bestanden |

### 3. HSTS gesetzt

| Art | Adresse | Fundstelle | Befund |
| --- | --- | --- | --- |
| Beleg | https://gut.test/ | Antwortheader Strict-Transport-Security | max-age=31536000; includeSubDomains (auf 11 von 11 Seiten) |

### 3. Content-Security-Policy gesetzt

| Art | Adresse | Fundstelle | Befund |
| --- | --- | --- | --- |
| Beleg | https://gut.test/ | Antwortheader Content-Security-Policy | default-src 'self'; img-src 'self' data:; style-src 'self'; script-src 'self'; font-src 'self'; connect-src 'self'; form-action 'self'; base-uri 'self'; object-src 'none'; frame-ancestors 'none' (auf 11 von 11 Seiten) |

### 3. X-Content-Type-Options gesetzt

| Art | Adresse | Fundstelle | Befund |
| --- | --- | --- | --- |
| Beleg | https://gut.test/ | Antwortheader X-Content-Type-Options | nosniff (auf 11 von 11 Seiten) |

### 3. Referrer-Policy gesetzt

| Art | Adresse | Fundstelle | Befund |
| --- | --- | --- | --- |
| Beleg | https://gut.test/ | Antwortheader Referrer-Policy | strict-origin-when-cross-origin (auf 11 von 11 Seiten) |

### 3. Permissions-Policy gesetzt

| Art | Adresse | Fundstelle | Befund |
| --- | --- | --- | --- |
| Beleg | https://gut.test/ | Antwortheader Permissions-Policy | camera=(), microphone=(), geolocation=(), payment=() (auf 11 von 11 Seiten) |

### 3. Schutz gegen Einbetten gesetzt

| Art | Adresse | Fundstelle | Befund |
| --- | --- | --- | --- |
| Beleg | https://gut.test/ | Antwortheader X-Frame-Options oder CSP frame-ancestors | CSP frame-ancestors 'none' (auf 11 von 11 Seiten) |

### 3. Cookies tragen Secure, HttpOnly und SameSite

| Art | Adresse | Fundstelle | Befund |
| --- | --- | --- | --- |
| Beleg | https://gut.test/ | Set-Cookie sitzung | Attribute secure, httponly, samesite=Lax |

### 3. Hinweise

| Adresse | Fundstelle | Hinweis |
| --- | --- | --- |
| https://gut.test/ | Umfang | Geprüft wurden Cookies aus Set-Cookie-Headern der Endantworten. Per Skript gesetzte Cookies stehen in Prüfung 4 |

<a id="p4"></a>

## 4. Vor Einwilligung

Ergebnis **bestanden**.

| Teilprüfung | Ergebnis |
| --- | --- |
| Keine Anfragen an fremde Hosts | ✅ bestanden |
| Nur technisch nötige Cookies | ✅ bestanden |

### 4. Keine Anfragen an fremde Hosts

| Art | Adresse | Fundstelle | Befund |
| --- | --- | --- | --- |
| Beleg | https://gut.test/ | Netzwerkanfragen | 3 Anfragen, alle an eigene Hosts |
| Beleg | https://gut.test/ersatzteile/ | Netzwerkanfragen | 3 Anfragen, alle an eigene Hosts |
| Beleg | https://gut.test/notebook-reparatur/ | Netzwerkanfragen | 3 Anfragen, alle an eigene Hosts |
| Beleg | https://gut.test/kasse/ | Netzwerkanfragen | 3 Anfragen, alle an eigene Hosts |
| Beleg | https://gut.test/ersatzteile/displays/displaykabel-x72/ | Netzwerkanfragen | 4 Anfragen, alle an eigene Hosts |
| Beleg | https://gut.test/impressum/ | Netzwerkanfragen | 3 Anfragen, alle an eigene Hosts |
| Beleg | https://gut.test/datenschutz/ | Netzwerkanfragen | 3 Anfragen, alle an eigene Hosts |
| Beleg | https://gut.test/agb/ | Netzwerkanfragen | 3 Anfragen, alle an eigene Hosts |
| Beleg | https://gut.test/widerruf/ | Netzwerkanfragen | 3 Anfragen, alle an eigene Hosts |
| Beleg | https://gut.test/widerruf/erklaeren/ | Netzwerkanfragen | 3 Anfragen, alle an eigene Hosts |
| Beleg | https://gut.test/ersatzteile/displays/ | Netzwerkanfragen | 3 Anfragen, alle an eigene Hosts |

### 4. Nur technisch nötige Cookies

| Art | Adresse | Fundstelle | Befund |
| --- | --- | --- | --- |
| Beleg | https://gut.test/ | Cookie sitzung auf gut.test | Steht auf der Liste technisch nötiger Cookies |
| Beleg | https://gut.test/ersatzteile/ | Cookie sitzung auf gut.test | Steht auf der Liste technisch nötiger Cookies |
| Beleg | https://gut.test/notebook-reparatur/ | Cookie sitzung auf gut.test | Steht auf der Liste technisch nötiger Cookies |
| Beleg | https://gut.test/kasse/ | Cookie sitzung auf gut.test | Steht auf der Liste technisch nötiger Cookies |
| Beleg | https://gut.test/ersatzteile/displays/displaykabel-x72/ | Cookie sitzung auf gut.test | Steht auf der Liste technisch nötiger Cookies |
| Beleg | https://gut.test/impressum/ | Cookie sitzung auf gut.test | Steht auf der Liste technisch nötiger Cookies |
| Beleg | https://gut.test/datenschutz/ | Cookie sitzung auf gut.test | Steht auf der Liste technisch nötiger Cookies |
| Beleg | https://gut.test/agb/ | Cookie sitzung auf gut.test | Steht auf der Liste technisch nötiger Cookies |
| Beleg | https://gut.test/widerruf/ | Cookie sitzung auf gut.test | Steht auf der Liste technisch nötiger Cookies |
| Beleg | https://gut.test/widerruf/erklaeren/ | Cookie sitzung auf gut.test | Steht auf der Liste technisch nötiger Cookies |
| Beleg | https://gut.test/ersatzteile/displays/ | Cookie sitzung auf gut.test | Steht auf der Liste technisch nötiger Cookies |

### 4. Hinweise

| Adresse | Fundstelle | Hinweis |
| --- | --- | --- |
| https://gut.test/ | Verfahren | Jede Seite wurde in einem neu gestarteten Chromium 157.0.8103.78 geladen, ohne Klick und ohne gespeicherte Daten. Erfasst wurde nach dem Laden und einer kurzen Wartezeit |

<a id="p5"></a>

## 5. Auffindbarkeit

Ergebnis **bestanden**.

| Teilprüfung | Ergebnis |
| --- | --- |
| Eigener Titel je Seite | ✅ bestanden |
| Meta-Beschreibung vorhanden | ✅ bestanden |
| Genau eine H1 | ✅ bestanden |
| Canonical vorhanden | ✅ bestanden |
| lang-Attribut gesetzt | ✅ bestanden |
| Bilder mit Alt-Text und festen Maßen | ✅ bestanden |
| noindex passend zum Modus demo | ✅ bestanden |
| Keine toten internen Links | ✅ bestanden |
| sitemap.xml vorhanden und gültig | ✅ bestanden |
| robots.txt vorhanden | ✅ bestanden |

### 5. Eigener Titel je Seite

| Art | Adresse | Fundstelle | Befund |
| --- | --- | --- | --- |
| Beleg | https://gut.test/ | <title> | Beispielshop für Notebook-Ersatzteile und Reparatur |
| Beleg | https://gut.test/ersatzteile/ | <title> | Ersatzteile für Notebooks im Überblick |
| Beleg | https://gut.test/notebook-reparatur/ | <title> | Notebook-Reparatur in der Werkstatt |
| Beleg | https://gut.test/kasse/ | <title> | Kasse und Bestellübersicht |
| Beleg | https://gut.test/ersatzteile/displays/displaykabel-x72/ | <title> | Displaykabel für Asus X72 kaufen |
| Beleg | https://gut.test/impressum/ | <title> | Impressum des Beispielshops |
| Beleg | https://gut.test/datenschutz/ | <title> | Datenschutzerklärung des Beispielshops |
| Beleg | https://gut.test/agb/ | <title> | Allgemeine Geschäftsbedingungen |
| Beleg | https://gut.test/widerruf/ | <title> | Widerrufsbelehrung des Beispielshops |
| Beleg | https://gut.test/widerruf/erklaeren/ | <title> | Vertrag online widerrufen |
| Beleg | https://gut.test/ersatzteile/displays/ | <title> | Displays und Displaykabel für Notebooks |

### 5. Meta-Beschreibung vorhanden

| Art | Adresse | Fundstelle | Befund |
| --- | --- | --- | --- |
| Beleg | https://gut.test/ | meta name="description" | 89 Zeichen |
| Beleg | https://gut.test/ersatzteile/ | meta name="description" | 57 Zeichen |
| Beleg | https://gut.test/notebook-reparatur/ | meta name="description" | 69 Zeichen |
| Beleg | https://gut.test/kasse/ | meta name="description" | 34 Zeichen |
| Beleg | https://gut.test/ersatzteile/displays/displaykabel-x72/ | meta name="description" | 89 Zeichen |
| Beleg | https://gut.test/impressum/ | meta name="description" | 40 Zeichen |
| Beleg | https://gut.test/datenschutz/ | meta name="description" | 46 Zeichen |
| Beleg | https://gut.test/agb/ | meta name="description" | 68 Zeichen |
| Beleg | https://gut.test/widerruf/ | meta name="description" | 44 Zeichen |
| Beleg | https://gut.test/widerruf/erklaeren/ | meta name="description" | 53 Zeichen |
| Beleg | https://gut.test/ersatzteile/displays/ | meta name="description" | 82 Zeichen |

### 5. Genau eine H1

| Art | Adresse | Fundstelle | Befund |
| --- | --- | --- | --- |
| Beleg | https://gut.test/ | <h1> | Notebook-Ersatzteile und Reparatur |
| Beleg | https://gut.test/ersatzteile/ | <h1> | Ersatzteile |
| Beleg | https://gut.test/notebook-reparatur/ | <h1> | Notebook-Reparatur |
| Beleg | https://gut.test/kasse/ | <h1> | Kasse |
| Beleg | https://gut.test/ersatzteile/displays/displaykabel-x72/ | <h1> | Displaykabel für Asus X72 |
| Beleg | https://gut.test/impressum/ | <h1> | Impressum |
| Beleg | https://gut.test/datenschutz/ | <h1> | Datenschutz |
| Beleg | https://gut.test/agb/ | <h1> | AGB |
| Beleg | https://gut.test/widerruf/ | <h1> | Widerrufsbelehrung |
| Beleg | https://gut.test/widerruf/erklaeren/ | <h1> | Vertrag widerrufen |
| Beleg | https://gut.test/ersatzteile/displays/ | <h1> | Displays und Displaykabel |

### 5. Canonical vorhanden

| Art | Adresse | Fundstelle | Befund |
| --- | --- | --- | --- |
| Beleg | https://gut.test/ | link rel="canonical" | https://gut.test/ |
| Beleg | https://gut.test/ersatzteile/ | link rel="canonical" | https://gut.test/ersatzteile/ |
| Beleg | https://gut.test/notebook-reparatur/ | link rel="canonical" | https://gut.test/notebook-reparatur/ |
| Beleg | https://gut.test/kasse/ | link rel="canonical" | https://gut.test/kasse/ |
| Beleg | https://gut.test/ersatzteile/displays/displaykabel-x72/ | link rel="canonical" | https://gut.test/ersatzteile/displays/displaykabel-x72/ |
| Beleg | https://gut.test/impressum/ | link rel="canonical" | https://gut.test/impressum/ |
| Beleg | https://gut.test/datenschutz/ | link rel="canonical" | https://gut.test/datenschutz/ |
| Beleg | https://gut.test/agb/ | link rel="canonical" | https://gut.test/agb/ |
| Beleg | https://gut.test/widerruf/ | link rel="canonical" | https://gut.test/widerruf/ |
| Beleg | https://gut.test/widerruf/erklaeren/ | link rel="canonical" | https://gut.test/widerruf/erklaeren/ |
| Beleg | https://gut.test/ersatzteile/displays/ | link rel="canonical" | https://gut.test/ersatzteile/displays/ |

### 5. lang-Attribut gesetzt

| Art | Adresse | Fundstelle | Befund |
| --- | --- | --- | --- |
| Beleg | https://gut.test/ | <html lang> | de |
| Beleg | https://gut.test/ersatzteile/ | <html lang> | de |
| Beleg | https://gut.test/notebook-reparatur/ | <html lang> | de |
| Beleg | https://gut.test/kasse/ | <html lang> | de |
| Beleg | https://gut.test/ersatzteile/displays/displaykabel-x72/ | <html lang> | de |
| Beleg | https://gut.test/impressum/ | <html lang> | de |
| Beleg | https://gut.test/datenschutz/ | <html lang> | de |
| Beleg | https://gut.test/agb/ | <html lang> | de |
| Beleg | https://gut.test/widerruf/ | <html lang> | de |
| Beleg | https://gut.test/widerruf/erklaeren/ | <html lang> | de |
| Beleg | https://gut.test/ersatzteile/displays/ | <html lang> | de |

### 5. Bilder mit Alt-Text und festen Maßen

| Art | Adresse | Fundstelle | Befund |
| --- | --- | --- | --- |
| Beleg | https://gut.test/ | <img> | 1 Bild mit alt, width und height |
| Beleg | https://gut.test/ersatzteile/ | <img> | 1 Bild mit alt, width und height |
| Beleg | https://gut.test/notebook-reparatur/ | <img> | 1 Bild mit alt, width und height |
| Beleg | https://gut.test/kasse/ | <img> | 1 Bild mit alt, width und height |
| Beleg | https://gut.test/ersatzteile/displays/displaykabel-x72/ | <img> | 2 Bilder mit alt, width und height |
| Beleg | https://gut.test/impressum/ | <img> | 1 Bild mit alt, width und height |
| Beleg | https://gut.test/datenschutz/ | <img> | 1 Bild mit alt, width und height |
| Beleg | https://gut.test/agb/ | <img> | 1 Bild mit alt, width und height |
| Beleg | https://gut.test/widerruf/ | <img> | 1 Bild mit alt, width und height |
| Beleg | https://gut.test/widerruf/erklaeren/ | <img> | 1 Bild mit alt, width und height |
| Beleg | https://gut.test/ersatzteile/displays/ | <img> | 1 Bild mit alt, width und height |

### 5. noindex passend zum Modus demo

| Art | Adresse | Fundstelle | Befund |
| --- | --- | --- | --- |
| Beleg | https://gut.test/ | meta robots | meta robots noindex, nofollow |
| Beleg | https://gut.test/ersatzteile/ | meta robots | meta robots noindex, nofollow |
| Beleg | https://gut.test/notebook-reparatur/ | meta robots | meta robots noindex, nofollow |
| Beleg | https://gut.test/kasse/ | meta robots | meta robots noindex, nofollow |
| Beleg | https://gut.test/ersatzteile/displays/displaykabel-x72/ | meta robots | meta robots noindex, nofollow |
| Beleg | https://gut.test/impressum/ | meta robots | meta robots noindex, nofollow |
| Beleg | https://gut.test/datenschutz/ | meta robots | meta robots noindex, nofollow |
| Beleg | https://gut.test/agb/ | meta robots | meta robots noindex, nofollow |
| Beleg | https://gut.test/widerruf/ | meta robots | meta robots noindex, nofollow |
| Beleg | https://gut.test/widerruf/erklaeren/ | meta robots | meta robots noindex, nofollow |
| Beleg | https://gut.test/ersatzteile/displays/ | meta robots | meta robots noindex, nofollow |

### 5. Keine toten internen Links

| Art | Adresse | Fundstelle | Befund |
| --- | --- | --- | --- |
| Beleg | https://gut.test/ | <a href> | 106 interne Links auf 11 Seiten geprüft |

### 5. sitemap.xml vorhanden und gültig

| Art | Adresse | Fundstelle | Befund |
| --- | --- | --- | --- |
| Beleg | https://gut.test/sitemap.xml | Sitemap | 10 Adressen gefunden |

### 5. robots.txt vorhanden

| Art | Adresse | Fundstelle | Befund |
| --- | --- | --- | --- |
| Beleg | https://gut.test/robots.txt | robots.txt | Status 200, 4 Zeilen |
| Hinweis | https://gut.test/robots.txt | User-agent * Disallow / | Sperrt alle Suchmaschinen aus. Für die Demo passend, Suchmaschinen sehen dann aber das noindex nicht |

<a id="p6"></a>

## 6. Strukturierte Daten

Ergebnis **bestanden**.

| Teilprüfung | Ergebnis |
| --- | --- |
| JSON-LD lesbar | ✅ bestanden |
| Artikelseiten mit Product, Preis, Währung und Verfügbarkeit | ✅ bestanden |
| Artikelseiten mit BreadcrumbList | ✅ bestanden |
| FAQ-Bereiche mit FAQPage | ✅ bestanden |
| Startseite mit Firmendaten | ✅ bestanden |

### 6. JSON-LD lesbar

| Art | Adresse | Fundstelle | Befund |
| --- | --- | --- | --- |
| Beleg | https://gut.test/ | script application/ld+json | Lesbar, Typen ComputerStore, PostalAddress |
| Beleg | https://gut.test/ersatzteile/ | script application/ld+json | Lesbar, Typen BreadcrumbList, ListItem |
| Beleg | https://gut.test/notebook-reparatur/ | script application/ld+json | Lesbar, Typen Answer, BreadcrumbList, FAQPage, ListItem, Question |
| Beleg | https://gut.test/ersatzteile/displays/displaykabel-x72/ | script application/ld+json | Lesbar, Typen BreadcrumbList, ListItem, Offer, Product |
| Beleg | https://gut.test/ersatzteile/displays/ | script application/ld+json | Lesbar, Typen BreadcrumbList, ListItem |

### 6. Artikelseiten mit Product, Preis, Währung und Verfügbarkeit

| Art | Adresse | Fundstelle | Befund |
| --- | --- | --- | --- |
| Beleg | https://gut.test/ersatzteile/displays/displaykabel-x72/ | Product Displaykabel für Asus X72 | Preis 11.90 EUR, InStock |

### 6. Artikelseiten mit BreadcrumbList

| Art | Adresse | Fundstelle | Befund |
| --- | --- | --- | --- |
| Beleg | https://gut.test/ersatzteile/displays/displaykabel-x72/ | JSON-LD BreadcrumbList | 4 Stufen |

### 6. FAQ-Bereiche mit FAQPage

| Art | Adresse | Fundstelle | Befund |
| --- | --- | --- | --- |
| Beleg | https://gut.test/notebook-reparatur/ | JSON-LD FAQPage | 2 Fragen mit Antwort |

### 6. Startseite mit Firmendaten

| Art | Adresse | Fundstelle | Befund |
| --- | --- | --- | --- |
| Beleg | https://gut.test/ | JSON-LD ComputerStore | Beispielshop Notebookteile mit address, telephone, email |

<a id="p7"></a>

## 7. Pflichtangaben

Ergebnis **bestanden**.

| Teilprüfung | Ergebnis |
| --- | --- |
| Impressum von jeder Seite erreichbar | ✅ bestanden |
| Datenschutz von jeder Seite erreichbar | ✅ bestanden |
| AGB von jeder Seite erreichbar | ✅ bestanden |
| Widerruf von jeder Seite erreichbar | ✅ bestanden |
| Widerrufsfunktion auffindbar | ✅ bestanden |
| Preise mit Hinweis auf Mehrwertsteuer und Versand | ✅ bestanden |
| Bestellknopf eindeutig beschriftet | ✅ bestanden |

### 7. Impressum von jeder Seite erreichbar

| Art | Adresse | Fundstelle | Befund |
| --- | --- | --- | --- |
| Beleg | https://gut.test/impressum/ | Link Impressum | Von 11 von 11 Seiten verlinkt, Status 200 |

### 7. Datenschutz von jeder Seite erreichbar

| Art | Adresse | Fundstelle | Befund |
| --- | --- | --- | --- |
| Beleg | https://gut.test/datenschutz/ | Link Datenschutz | Von 11 von 11 Seiten verlinkt, Status 200 |

### 7. AGB von jeder Seite erreichbar

| Art | Adresse | Fundstelle | Befund |
| --- | --- | --- | --- |
| Beleg | https://gut.test/agb/ | Link AGB | Von 11 von 11 Seiten verlinkt, Status 200 |

### 7. Widerruf von jeder Seite erreichbar

| Art | Adresse | Fundstelle | Befund |
| --- | --- | --- | --- |
| Beleg | https://gut.test/widerruf/ | Link Widerruf | Von 10 von 11 Seiten verlinkt, Status 200 |
| Beleg | https://gut.test/widerruf/erklaeren/ | Link Widerruf | Von 1 von 11 Seiten verlinkt, Status 200 |

### 7. Widerrufsfunktion auffindbar

| Art | Adresse | Fundstelle | Befund |
| --- | --- | --- | --- |
| Beleg | https://gut.test/ | <a> Vertrag widerrufen | Element zur Widerrufsfunktion gefunden |
| Beleg | https://gut.test/ersatzteile/ | <a> Vertrag widerrufen | Element zur Widerrufsfunktion gefunden |
| Beleg | https://gut.test/notebook-reparatur/ | <a> Vertrag widerrufen | Element zur Widerrufsfunktion gefunden |
| Beleg | https://gut.test/kasse/ | <a> Vertrag widerrufen | Element zur Widerrufsfunktion gefunden |
| Beleg | https://gut.test/ersatzteile/displays/displaykabel-x72/ | <a> Vertrag widerrufen | Element zur Widerrufsfunktion gefunden |
| Beleg | https://gut.test/impressum/ | <a> Vertrag widerrufen | Element zur Widerrufsfunktion gefunden |
| Beleg | https://gut.test/datenschutz/ | <a> Vertrag widerrufen | Element zur Widerrufsfunktion gefunden |
| Beleg | https://gut.test/agb/ | <a> Vertrag widerrufen | Element zur Widerrufsfunktion gefunden |
| Beleg | https://gut.test/widerruf/ | <a> Vertrag widerrufen | Element zur Widerrufsfunktion gefunden |
| Beleg | https://gut.test/widerruf/erklaeren/ | <button> Widerruf bestätigen | Element zur Widerrufsfunktion gefunden |
| Beleg | https://gut.test/ersatzteile/displays/ | <a> Vertrag widerrufen | Element zur Widerrufsfunktion gefunden |

### 7. Preise mit Hinweis auf Mehrwertsteuer und Versand

| Art | Adresse | Fundstelle | Befund |
| --- | --- | --- | --- |
| Beleg | https://gut.test/ | Preis 11,90 € | 1 Preise, Hinweis inkl. MwSt und zzgl. Versand |
| Beleg | https://gut.test/notebook-reparatur/ | Preis 29,00 € | 2 Preise, Hinweis inkl. MwSt und zzgl. Versand |
| Beleg | https://gut.test/kasse/ | Preis 11,90 € | 2 Preise, Hinweis inkl. MwSt und zzgl. Versand |
| Beleg | https://gut.test/ersatzteile/displays/displaykabel-x72/ | Preis 11,90 € | 1 Preise, Hinweis inkl. MwSt und zzgl. Versand |
| Beleg | https://gut.test/agb/ | Preis 4,90 € | 1 Preise, Hinweis inkl. MwSt und Versandkosten |
| Beleg | https://gut.test/ersatzteile/displays/ | Preis 11,90 € | 1 Preise, Hinweis inkl. MwSt und zzgl. Versand |

### 7. Bestellknopf eindeutig beschriftet

| Art | Adresse | Fundstelle | Befund |
| --- | --- | --- | --- |
| Beleg | https://gut.test/kasse/ | Knopf Zahlungspflichtig bestellen | Beschriftung eindeutig |

### 7. Hinweise

| Adresse | Fundstelle | Hinweis |
| --- | --- | --- |
| https://gut.test/ | Umfang | Geprüft wird nur das Vorhandensein, nicht die inhaltliche oder rechtliche Richtigkeit |

<a id="p8"></a>

## 8. Barrierefreiheit

Ergebnis **bestanden**.

| Teilprüfung | Ergebnis |
| --- | --- |
| axe-core WCAG 2.2 A und AA | ✅ bestanden |
| Zoomen am Handy nicht gesperrt | ✅ bestanden |

### 8. axe-core WCAG 2.2 A und AA

| Art | Adresse | Fundstelle | Befund |
| --- | --- | --- | --- |
| Beleg | https://gut.test/ | axe-core | Keine Verstöße |
| Beleg | https://gut.test/ersatzteile/ | axe-core | Keine Verstöße |
| Beleg | https://gut.test/notebook-reparatur/ | axe-core | Keine Verstöße |
| Beleg | https://gut.test/kasse/ | axe-core | Keine Verstöße |
| Beleg | https://gut.test/ersatzteile/displays/displaykabel-x72/ | axe-core | Keine Verstöße |
| Beleg | https://gut.test/impressum/ | axe-core | Keine Verstöße |
| Beleg | https://gut.test/datenschutz/ | axe-core | Keine Verstöße |
| Beleg | https://gut.test/agb/ | axe-core | Keine Verstöße |
| Beleg | https://gut.test/widerruf/ | axe-core | Keine Verstöße |
| Beleg | https://gut.test/widerruf/erklaeren/ | axe-core | Keine Verstöße |
| Beleg | https://gut.test/ersatzteile/displays/ | axe-core | Keine Verstöße |

### 8. Zoomen am Handy nicht gesperrt

| Art | Adresse | Fundstelle | Befund |
| --- | --- | --- | --- |
| Beleg | https://gut.test/ | meta name="viewport" | width=device-width, initial-scale=1 |
| Beleg | https://gut.test/ersatzteile/ | meta name="viewport" | width=device-width, initial-scale=1 |
| Beleg | https://gut.test/notebook-reparatur/ | meta name="viewport" | width=device-width, initial-scale=1 |
| Beleg | https://gut.test/kasse/ | meta name="viewport" | width=device-width, initial-scale=1 |
| Beleg | https://gut.test/ersatzteile/displays/displaykabel-x72/ | meta name="viewport" | width=device-width, initial-scale=1 |
| Beleg | https://gut.test/impressum/ | meta name="viewport" | width=device-width, initial-scale=1 |
| Beleg | https://gut.test/datenschutz/ | meta name="viewport" | width=device-width, initial-scale=1 |
| Beleg | https://gut.test/agb/ | meta name="viewport" | width=device-width, initial-scale=1 |
| Beleg | https://gut.test/widerruf/ | meta name="viewport" | width=device-width, initial-scale=1 |
| Beleg | https://gut.test/widerruf/erklaeren/ | meta name="viewport" | width=device-width, initial-scale=1 |
| Beleg | https://gut.test/ersatzteile/displays/ | meta name="viewport" | width=device-width, initial-scale=1 |

### 8. Hinweise

| Adresse | Fundstelle | Hinweis |
| --- | --- | --- |
| https://gut.test/ | Werkzeug | axe-core 4.14.0 mit den Regelgruppen wcag2a, wcag2aa, wcag21a, wcag21aa, wcag22a, wcag22aa. Automatische Tests finden nur einen Teil der Barrieren, eine Prüfung von Hand bleibt nötig |

<a id="p9"></a>

## 9. Leistung

Ergebnis **bestanden**.

| Teilprüfung | Ergebnis |
| --- | --- |
| Übertragene Daten je Seite unter 0,5 MB | ✅ bestanden |
| Größte Dateien | ✅ bestanden |

### 9. Übertragene Daten je Seite unter 0,5 MB

| Art | Adresse | Fundstelle | Befund |
| --- | --- | --- | --- |
| Beleg | https://gut.test/ | Übertragene Daten | 0,005 MB in 3 Anfragen, größte Datei https://gut.test/ mit 0,003 MB |
| Beleg | https://gut.test/ersatzteile/ | Übertragene Daten | 0,005 MB in 3 Anfragen, größte Datei https://gut.test/ersatzteile/ mit 0,002 MB |
| Beleg | https://gut.test/notebook-reparatur/ | Übertragene Daten | 0,005 MB in 3 Anfragen, größte Datei https://gut.test/notebook-reparatur/ mit 0,003 MB |
| Beleg | https://gut.test/kasse/ | Übertragene Daten | 0,005 MB in 3 Anfragen, größte Datei https://gut.test/kasse/ mit 0,002 MB |
| Beleg | https://gut.test/ersatzteile/displays/displaykabel-x72/ | Übertragene Daten | 0,007 MB in 4 Anfragen, größte Datei https://gut.test/ersatzteile/displays/displaykabel-x72/ mit 0,004 MB |
| Beleg | https://gut.test/impressum/ | Übertragene Daten | 0,004 MB in 3 Anfragen, größte Datei https://gut.test/impressum/ mit 0,002 MB |
| Beleg | https://gut.test/datenschutz/ | Übertragene Daten | 0,004 MB in 3 Anfragen, größte Datei https://gut.test/datenschutz/ mit 0,002 MB |
| Beleg | https://gut.test/agb/ | Übertragene Daten | 0,004 MB in 3 Anfragen, größte Datei https://gut.test/agb/ mit 0,002 MB |
| Beleg | https://gut.test/widerruf/ | Übertragene Daten | 0,004 MB in 3 Anfragen, größte Datei https://gut.test/widerruf/ mit 0,002 MB |
| Beleg | https://gut.test/widerruf/erklaeren/ | Übertragene Daten | 0,004 MB in 3 Anfragen, größte Datei https://gut.test/widerruf/erklaeren/ mit 0,002 MB |
| Beleg | https://gut.test/ersatzteile/displays/ | Übertragene Daten | 0,005 MB in 3 Anfragen, größte Datei https://gut.test/ersatzteile/displays/ mit 0,003 MB |

### 9. Größte Dateien

| Art | Adresse | Fundstelle | Befund |
| --- | --- | --- | --- |
| Beleg | https://gut.test/ersatzteile/displays/displaykabel-x72/ | Datei https://gut.test/ersatzteile/displays/displaykabel-x72/ | 0,004 MB |
| Beleg | https://gut.test/notebook-reparatur/ | Datei https://gut.test/notebook-reparatur/ | 0,003 MB |
| Beleg | https://gut.test/ | Datei https://gut.test/ | 0,003 MB |
| Beleg | https://gut.test/ersatzteile/displays/ | Datei https://gut.test/ersatzteile/displays/ | 0,003 MB |
| Beleg | https://gut.test/ersatzteile/ | Datei https://gut.test/ersatzteile/ | 0,002 MB |
| Beleg | https://gut.test/kasse/ | Datei https://gut.test/kasse/ | 0,002 MB |
| Beleg | https://gut.test/widerruf/erklaeren/ | Datei https://gut.test/widerruf/erklaeren/ | 0,002 MB |
| Beleg | https://gut.test/widerruf/ | Datei https://gut.test/widerruf/ | 0,002 MB |
| Beleg | https://gut.test/agb/ | Datei https://gut.test/agb/ | 0,002 MB |
| Beleg | https://gut.test/impressum/ | Datei https://gut.test/impressum/ | 0,002 MB |

### 9. Hinweise

| Adresse | Fundstelle | Hinweis |
| --- | --- | --- |
| https://gut.test/ | Zahl der Anfragen | Je Seite zwischen 3 und 4, im Mittel 3,1 |
| https://gut.test/ | Messung | Gezählt werden Header und Inhalt jeder Antwort beim ersten Laden ohne Zwischenspeicher. Die Grenze beträgt 500000 Byte |
| https://gut.test/ | Lighthouse | Lighthouse ist nicht installiert und wurde deshalb nicht ausgeführt |

<a id="p10"></a>

## 10. E-Mail-DNS

Ergebnis **bestanden**.

| Teilprüfung | Ergebnis |
| --- | --- |
| SPF endet auf -all oder ~all | ✅ bestanden |
| DMARC vorhanden | ✅ bestanden |
| DKIM unter dem angegebenen Selektor | ✅ bestanden |

### 10. SPF endet auf -all oder ~all

| Art | Adresse | Fundstelle | Befund |
| --- | --- | --- | --- |
| Beleg | gut.test | TXT gut.test | v=spf1 mx -all |

### 10. DMARC vorhanden

| Art | Adresse | Fundstelle | Befund |
| --- | --- | --- | --- |
| Beleg | gut.test | TXT _dmarc.gut.test | v=DMARC1; p=reject; rua=mailto:dmarc@gut.test |

### 10. DKIM unter dem angegebenen Selektor

| Art | Adresse | Fundstelle | Befund |
| --- | --- | --- | --- |
| Beleg | gut.test | TXT mail._domainkey.gut.test | Öffentlicher Schlüssel mit 58 Zeichen |

### 10. Hinweise

| Adresse | Fundstelle | Hinweis |
| --- | --- | --- |
| gut.test | Abfrage | Domain gut.test, abgefragt über Nameserver 127.0.0.1:5353 |
