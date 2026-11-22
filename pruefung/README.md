# Abnahmeprüfung für den Onlineshop

Dieses Werkzeug prüft eine Shopadresse automatisch gegen die Abnahmeanforderungen für Notebook Reparatur 24. Es ist für die Demo unter https://nr24.kazas.dev gedacht und später für die echte Seite. Jede Prüfung endet mit „bestanden“, „nicht bestanden“ oder „nicht prüfbar“ und nennt Belege mit Adresse und Fundstelle.

Das Werkzeug prüft das Vorhandensein technischer und inhaltlicher Merkmale. Es ersetzt keine Rechtsberatung und keine Prüfung von Hand.

## Was geprüft wird

| Nr. | Prüfung | Inhalt |
| --- | --- | --- |
| 1 | Adressen und Weiterleitungen | http leitet per 301 auf https um, alle Varianten mit und ohne www landen auf einer Hauptadresse, alte Adressen aus einer CSV leiten per 301 auf ein Ziel mit Status 200 |
| 2 | TLS | TLS 1.0 und 1.1 werden abgelehnt, TLS 1.2 oder 1.3 wird angenommen, das Zertifikat gilt noch mindestens 30 Tage |
| 3 | Sicherheitsheader und Cookies | HSTS, Content-Security-Policy, X-Content-Type-Options, Referrer-Policy, Permissions-Policy, Schutz gegen Einbetten, Cookies mit Secure, HttpOnly und SameSite |
| 4 | Vor Einwilligung | Jede Seite in einem frisch gestarteten Chromium ohne Klick, keine Anfrage an fremde Hosts, nur technisch nötige Cookies, alle Funde werden aufgelistet |
| 5 | Auffindbarkeit | Eigener Titel, Meta-Beschreibung, genau eine H1, Canonical, lang, Bilder mit alt und festen Maßen, keine toten internen Links, sitemap.xml, robots.txt, noindex passend zum Modus |
| 6 | Strukturierte Daten | JSON-LD lesbar, Artikelseiten mit Product (Name, Preis, Währung, Verfügbarkeit) und BreadcrumbList, FAQ-Bereiche mit FAQPage, Startseite mit Firmendaten |
| 7 | Pflichtangaben | Impressum, Datenschutz, AGB und Widerruf von jeder Seite verlinkt, Widerrufsfunktion auffindbar, Preise mit Hinweis auf Mehrwertsteuer und Versand, Bestellknopf eindeutig beschriftet |
| 8 | Barrierefreiheit | axe-core mit WCAG 2.2 Stufe A und AA, Zoomen am Handy nicht gesperrt |
| 9 | Leistung | Übertragene Daten je Seite unter 0,5 MB, Zahl der Anfragen, größte Dateien, Lighthouse nur falls installiert |
| 10 | E-Mail-DNS | SPF endet auf -all oder ~all, DMARC vorhanden, DKIM unter dem angegebenen Selektor |

Im Modus `demo` muss jede Seite noindex tragen, im Modus `live` darf keine Seite es tragen.

## Rücksicht auf den Server

* Es gibt nur lesende Abrufe mit GET und HEAD. Formulare werden nie abgesendet, Logins finden nicht statt.
* Zwischen zwei Abrufen liegt mindestens eine Sekunde. Kleinere Werte für `--pause` werden auf eine Sekunde angehoben. Im Browserlauf gilt die Pause zwischen zwei Seitenaufrufen.
* Erfasst werden höchstens 200 Seiten. robots.txt und Sitemaps zählen mit. Die Einträge einer Weiterleitungsliste sind ausdrücklich bestellt und werden zusätzlich abgerufen.
* Links mit Mustern wie logout, login, konto oder add-to-cart werden nicht abgerufen (Schlüssel `ausschliessen` in `einstellungen.json`).
* robots.txt wird gelesen und bewertet, aber nicht befolgt, denn die Demo sperrt alle Pfade und eine Abnahme muss die Seiten trotzdem sehen. Das Werkzeug meldet sich mit dem Benutzeragenten `nr24-Abnahmepruefung/1.0`.

## Einrichtung

Benötigt werden Python ab 3.10, Node.js ab 18 und OpenSSL. Alle Befehle laufen im Wurzelverzeichnis des Repos.

```bash
python3 -m venv pruefung/.venv
```

```bash
pruefung/.venv/bin/pip install -r pruefung/requirements.txt
```

```bash
cd pruefung && npm ci
```

Falls auf dem Rechner noch kein passender Chromium für Playwright 1.63.0 liegt, holt ihn dieser Befehl.

```bash
cd pruefung && npx playwright install chromium
```

`pruefen.py` und jedes Prüfmodul wechseln von selbst in die venv unter `pruefung/.venv`, wenn sie mit dem Systempython gestartet werden. Die Versionen sind in `requirements.txt` und in `package.json` mit `package-lock.json` fest vorgegeben.

Lighthouse ist nicht Teil der festen Abhängigkeiten. Liegt ein Befehl `lighthouse` im Suchpfad oder unter `pruefung/node_modules/.bin`, läuft er in Prüfung 9 für die Startseite mit, sonst steht im Bericht ein Hinweis.

## Aufruf

```bash
python3 pruefung/pruefen.py --ziel https://nr24.kazas.dev --modus demo
```

Mit alter Adressliste und DKIM-Selektor für die echte Seite.

```bash
python3 pruefung/pruefen.py --ziel https://www.example.de --modus live --weiterleitungen alt.csv --dkim-selektor default
```

Die CSV trennt mit Semikolon. Die Kopfzeile `url_alt;url_neu` ist erlaubt, Adressen ohne Host gelten für die Hauptadresse.

```text
url_alt;url_neu
/shop/displaykabel-x72.html;/ersatzteile/displays/displaykabel-x72/
https://alter-shop.de/agb.php;https://www.example.de/agb/
```

Nur einzelne Prüfungen über den Hauptaufruf.

```bash
python3 pruefung/pruefen.py --ziel https://nr24.kazas.dev --modus demo --nur 3,5,7
```

Jede Prüfung ist ein eigenes Modul und lässt sich auch direkt starten. Der Bericht heißt dann `pruefung-NN.md` und `pruefung-NN.json`.

```bash
python3 pruefung/pruefungen/p03_sicherheitsheader.py --ziel https://nr24.kazas.dev --modus demo
```

| Modul | Prüfung |
| --- | --- |
| `pruefungen/p01_adressen.py` | 1 Adressen und Weiterleitungen |
| `pruefungen/p02_tls.py` | 2 TLS |
| `pruefungen/p03_sicherheitsheader.py` | 3 Sicherheitsheader und Cookies |
| `pruefungen/p04_einwilligung.py` | 4 Vor Einwilligung |
| `pruefungen/p05_auffindbarkeit.py` | 5 Auffindbarkeit |
| `pruefungen/p06_strukturdaten.py` | 6 Strukturierte Daten |
| `pruefungen/p07_pflichtangaben.py` | 7 Pflichtangaben |
| `pruefungen/p08_barrierefreiheit.py` | 8 Barrierefreiheit |
| `pruefungen/p09_leistung.py` | 9 Leistung |
| `pruefungen/p10_email_dns.py` | 10 E-Mail-DNS |

### Optionen

| Option | Bedeutung |
| --- | --- |
| `--ziel` | Adresse des Shops, ohne Schema wird https angenommen |
| `--modus demo` oder `--modus live` | Erwartung an noindex und robots.txt |
| `--weiterleitungen datei.csv` | Alte Adressen mit `url_alt;url_neu` |
| `--dkim-selektor name` | DKIM-Selektor, ohne ihn ist der DKIM-Teil nicht prüfbar |
| `--mail-domain` | Domain für SPF, DMARC und DKIM, Vorgabe ist der Host ohne www |
| `--nur 1,4` | Nur diese Prüfungen ausführen |
| `--einstellungen datei.json` | Eigene Grenzwerte und Muster, fehlende Schlüssel kommen aus `einstellungen.json` |
| `--berichte ordner` | Anderer Ablageort für Berichte |
| `--pause` | Pause in Sekunden, mindestens 1 |
| `--max-seiten` | Höchstzahl erfasster Seiten, höchstens 200 |
| `--aufloesen host=ip` | Host fest auf eine Adresse auflösen und ohne Proxy abrufen, mehrfach möglich, nützlich vor einer DNS-Umstellung |
| `--ca-datei ca.pem` | Zusätzliche Zertifizierungsstelle, etwa für einen Testserver. Der Browserlauf ignoriert dann Zertifikatsfehler, die Zertifikatsprüfung selbst übernimmt Prüfung 2 |
| `--dns-server ip:port` | Nameserver für Prüfung 10, etwa der autoritative Server des Anbieters |
| `--dns-ueber-https` | Prüfung 10 über DNS über HTTPS (Adresse unter `doh_adresse` in `einstellungen.json`) |
| `--streng` | Rückgabewert 3, wenn nichts fehlschlug, aber etwas nicht prüfbar war |

## Ergebnis

Der Bericht liegt unter `pruefung/berichte/<datum>-<host>/` als `bericht.md` und `bericht.json`. Jede Prüfung besteht aus Teilprüfungen mit eigenem Ergebnis. Jeder Beleg nennt Art (Fehler, Hinweis oder Beleg), Adresse, Fundstelle und Befund. Der Markdown-Bericht zeigt je Teilprüfung höchstens 40 Belege, die JSON-Datei enthält alle.

Eine Prüfung ist nicht bestanden, sobald eine Teilprüfung nicht besteht. Sie ist nicht prüfbar, wenn nichts fehlschlug, aber eine Teilprüfung nicht durchführbar war. Hinweise ändern das Ergebnis nicht.

| Rückgabewert | Bedeutung |
| --- | --- |
| 0 | Keine Prüfung ist nicht bestanden |
| 1 | Mindestens eine Prüfung ist nicht bestanden |
| 2 | Aufruf fehlerhaft |
| 3 | Nur mit `--streng`, mindestens eine Prüfung war nicht prüfbar |

## Einstellungen

`einstellungen.json` enthält alle Grenzwerte und Muster. Die wichtigsten Schlüssel sind diese.

| Schlüssel | Vorgabe | Zweck |
| --- | --- | --- |
| `max_bytes_je_seite` | 500000 | Grenze für Prüfung 9, 0,5 MB als 500 000 Byte |
| `zertifikat_mindesttage` | 30 | Restlaufzeit des Zertifikats |
| `hsts_mindestalter_sekunden` | 15552000 | Mindestwert für max-age, das sind 180 Tage |
| `noetige_cookies` | Sitzung, CSRF, Warenkorb, Einwilligung | Reguläre Ausdrücke für Cookies, die vor einer Einwilligung erlaubt sind |
| `eigene_hosts` | leer | Weitere Hosts, die als eigene gelten, etwa ein eigener Bilderserver |
| `artikel_muster` | `^/ersatzteile/[^/]+/[^/]+/$` | Pfade von Artikelseiten für Prüfung 6, passend zur Demo |
| `ausschliessen` | Login, Logout, Konto, Warenkorbaktionen | Adressen, die nie abgerufen werden |
| `axe_tags` | wcag2a bis wcag22aa | Regelgruppen für axe-core |

Eine Seite gilt als Artikelseite, wenn sie Product in JSON-LD trägt, `og:type` product setzt oder ihr Pfad zu `artikel_muster` passt.

## Test mit der Beispielseite

Unter `pruefung/beispiel/` liegt eine kleine Beispielseite in zwei Fassungen. `gut/` erfüllt alle Anforderungen, `schlecht/` verletzt jede Prüfung absichtlich. Der Testserver `server.py` liefert sie unter erfundenen Hostnamen aus, `dns_server.py` beantwortet die TXT-Abfragen für SPF, DMARC und DKIM.

| Host | Inhalt | Adresse |
| --- | --- | --- |
| gut.test | Fassung gut mit noindex, Modus demo | 127.0.0.1 |
| live.test | Fassung gut ohne noindex und mit offener robots.txt, Modus live | 127.0.0.1 |
| schlecht.test | Fassung schlecht, dazu TLS 1.0 und ein Zertifikat mit 10 Tagen Laufzeit | 127.0.0.2 |
| drittanbieter.test | Fremder Host mit Skript und Cookie, eingebunden von schlecht.test | 127.0.0.1 |

schlecht.test liegt auf einer eigenen Adresse, weil OpenSSL die erlaubten TLS-Versionen festlegt, bevor der Server über SNI das Zertifikat wählt.

Der Testlauf erzeugt Seiten und Zertifikate neu, startet beide Server, führt vier Prüfläufe und einen Einzelaufruf aus und vergleicht jedes Ergebnis mit der Erwartung. Er braucht Rechte für die Ports 80 und 443.

```bash
sudo python3 pruefung/beispiel/testen.py
```

| Lauf | Erwartung |
| --- | --- |
| gut.test im Modus demo | alle zehn Prüfungen bestanden, Rückgabewert 0 |
| schlecht.test im Modus demo | alle zehn Prüfungen nicht bestanden, Rückgabewert 1 |
| live.test im Modus live | alle zehn Prüfungen bestanden, Rückgabewert 0 |
| gut.test im Modus live | Prüfung 5 nicht bestanden wegen noindex und robots.txt, Rückgabewert 1 |
| Prüfung 3 einzeln für gut.test | bestanden, eigener Bericht `pruefung-03` |

Die Berichte der ersten drei Läufe liegen unter `pruefung/berichte/`. Ein einzelner Lauf gegen die Beispielseite sieht so aus, wenn die Server bereits laufen.

```bash
python3 pruefung/pruefen.py --ziel https://gut.test --modus demo --weiterleitungen pruefung/beispiel/weiterleitungen-gut.csv --dkim-selektor mail --aufloesen gut.test=127.0.0.1 --aufloesen www.gut.test=127.0.0.1 --ca-datei pruefung/beispiel/zertifikate/ca.crt --dns-server 127.0.0.1:5353
```

## Grenzen

* Prüfung 2 baut eine direkte TCP-Verbindung zum Server auf. Läuft der Verkehr über einen Proxy, der TLS neu aufbaut, würde sonst der Proxy geprüft. Das Werkzeug meldet in diesem Fall „nicht prüfbar“. Ob der Prüfrechner TLS 1.0 überhaupt anbieten kann, hängt von seiner OpenSSL-Version ab, sonst steht dort ebenfalls „nicht prüfbar“.
* Cookies prüft Prüfung 3 nur aus Set-Cookie-Headern der Endantworten. Cookies, die erst ein Skript setzt, erfasst Prüfung 4.
* Ob ein Cookie technisch nötig ist, entscheidet die Liste `noetige_cookies`. Die Liste ist eine Vorgabe und muss zum echten Shop passen.
* Prüfung 4 erfasst den Zustand nach dem Laden, nach Netzwerkruhe und zwei weiteren Sekunden. Spätere Anfragen, etwa nach Scrollen, sieht sie nicht.
* Prüfung 7 sucht Preise, Hinweise und Knöpfe im Seitentext. Ob der Hinweis bei jedem Preis steht, bewertet sie nicht. Den Bestellknopf findet sie nur, wenn die Kasse ohne Warenkorb und ohne Anmeldung im HTML steht, sonst lautet das Ergebnis „nicht prüfbar“.
* axe-core findet nur einen Teil der Barrieren. Unklare Stellen stehen als Hinweis im Bericht.
* Bilder gelten nur mit den Attributen width und height als fest bemessen. Maße allein aus CSS erkennt das Werkzeug nicht.
* DMARC wird bei fehlendem Eintrag an der Organisationsdomain gesucht, die das Werkzeug vereinfacht aus den letzten zwei Namensteilen bildet. Für Endungen wie co.uk ist das ungenau.

## Aufbau

| Pfad | Inhalt |
| --- | --- |
| `pruefen.py` | Hauptaufruf |
| `pruefungen/` | Ein Modul je Prüfung |
| `lib/` | Abruf mit Pause, Erfassung der Seiten, Browseranbindung, DNS, Bericht |
| `browser/erfassen.mjs` | Browserteil mit Playwright und axe-core |
| `einstellungen.json` | Grenzwerte und Muster |
| `beispiel/` | Beispielseiten, Testserver, DNS-Testserver und Testlauf |
| `berichte/` | Erzeugte Berichte |
