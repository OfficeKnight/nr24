# Abnahmeprüfung https://nr24.kazas.dev/

Der Bericht prüft das Vorhandensein technischer und inhaltlicher Merkmale. Er ist keine Rechtsberatung.

| Angabe | Wert |
| --- | --- |
| Ziel | https://nr24.kazas.dev/ |
| Hauptadresse | nicht ermittelt |
| Modus | demo |
| Beginn | 2026-11-22T21:27:12+01:00 |
| Werkzeug | nr24-Abnahmepruefung 1.0.0 |
| HTTP-Abrufe | 5 |
| Erfasste HTML-Seiten | 0 |
| Gesamtergebnis | ❌ nicht bestanden |

## Übersicht

| Nr. | Prüfung | Ergebnis |
| --- | --- | --- |
| 1 | [Adressen und Weiterleitungen](#p1) | ⚠️ nicht prüfbar |
| 2 | [TLS](#p2) | ⚠️ nicht prüfbar |
| 3 | [Sicherheitsheader und Cookies](#p3) | ⚠️ nicht prüfbar |
| 4 | [Vor Einwilligung](#p4) | ⚠️ nicht prüfbar |
| 5 | [Auffindbarkeit](#p5) | ⚠️ nicht prüfbar |
| 6 | [Strukturierte Daten](#p6) | ⚠️ nicht prüfbar |
| 7 | [Pflichtangaben](#p7) | ⚠️ nicht prüfbar |
| 8 | [Barrierefreiheit](#p8) | ⚠️ nicht prüfbar |
| 9 | [Leistung](#p9) | ⚠️ nicht prüfbar |
| 10 | [E-Mail-DNS](#p10) | ❌ nicht bestanden |

<a id="p1"></a>

## 1. Adressen und Weiterleitungen

Ergebnis **nicht prüfbar**.

| Teilprüfung | Ergebnis |
| --- | --- |
| http leitet per 301 auf https um | ⚠️ nicht prüfbar |
| Eine Hauptadresse für alle Varianten | ⚠️ nicht prüfbar |

### 1. http leitet per 301 auf https um

| Art | Adresse | Fundstelle | Befund |
| --- | --- | --- | --- |
| Hinweis | http://nr24.kazas.dev/ | Erster Abruf | Verbindung fehlgeschlagen (Name nicht auflösbar) |
| Hinweis | http://www.nr24.kazas.dev/ | DNS | Variante hat keinen DNS-Eintrag, im Modus demo nur ein Hinweis |

### 1. Eine Hauptadresse für alle Varianten

| Art | Adresse | Fundstelle | Befund |
| --- | --- | --- | --- |
| Hinweis | https://nr24.kazas.dev/ | Startseite | Startseite nicht erreichbar, https://nr24.kazas.dev/ liefert Verbindung fehlgeschlagen (Proxy verweigert die Verbindung mit Status 502) |

### 1. Hinweise

| Adresse | Fundstelle | Hinweis |
| --- | --- | --- |
| https://nr24.kazas.dev/ | Weiterleitungsliste | Keine Datei mit --weiterleitungen angegeben, alte Adressen wurden nicht geprüft |

<a id="p2"></a>

## 2. TLS

Ergebnis **nicht prüfbar**.

| Teilprüfung | Ergebnis |
| --- | --- |
| Nur TLS 1.2 und 1.3 werden angenommen | ⚠️ nicht prüfbar |
| Zertifikat gilt noch mindestens 30 Tage | ⚠️ nicht prüfbar |

### 2. Nur TLS 1.2 und 1.3 werden angenommen

| Art | Adresse | Fundstelle | Befund |
| --- | --- | --- | --- |
| Hinweis | https://nr24.kazas.dev/ | Verbindung | Ausgehende Verbindungen laufen über den Proxy http://127.0.0.1:33161. Ein Proxy kann TLS neu aufbauen, dann würde der Proxy statt des Servers geprüft. Bitte ohne Proxy ausführen. |

### 2. Zertifikat gilt noch mindestens 30 Tage

| Art | Adresse | Fundstelle | Befund |
| --- | --- | --- | --- |
| Hinweis | https://nr24.kazas.dev/ | Verbindung | Ausgehende Verbindungen laufen über den Proxy http://127.0.0.1:33161. Ein Proxy kann TLS neu aufbauen, dann würde der Proxy statt des Servers geprüft. Bitte ohne Proxy ausführen. |

<a id="p3"></a>

## 3. Sicherheitsheader und Cookies

Ergebnis **nicht prüfbar**.

| Teilprüfung | Ergebnis |
| --- | --- |
| Voraussetzung | ⚠️ nicht prüfbar |

### 3. Voraussetzung

| Art | Adresse | Fundstelle | Befund |
| --- | --- | --- | --- |
| Hinweis | https://nr24.kazas.dev/ | Prüflauf | Startseite nicht erreichbar, https://nr24.kazas.dev/ liefert Verbindung fehlgeschlagen (Proxy verweigert die Verbindung mit Status 502) |

<a id="p4"></a>

## 4. Vor Einwilligung

Ergebnis **nicht prüfbar**.

| Teilprüfung | Ergebnis |
| --- | --- |
| Voraussetzung | ⚠️ nicht prüfbar |

### 4. Voraussetzung

| Art | Adresse | Fundstelle | Befund |
| --- | --- | --- | --- |
| Hinweis | https://nr24.kazas.dev/ | Prüflauf | Startseite nicht erreichbar, https://nr24.kazas.dev/ liefert Verbindung fehlgeschlagen (Proxy verweigert die Verbindung mit Status 502) |

<a id="p5"></a>

## 5. Auffindbarkeit

Ergebnis **nicht prüfbar**.

| Teilprüfung | Ergebnis |
| --- | --- |
| Voraussetzung | ⚠️ nicht prüfbar |

### 5. Voraussetzung

| Art | Adresse | Fundstelle | Befund |
| --- | --- | --- | --- |
| Hinweis | https://nr24.kazas.dev/ | Prüflauf | Startseite nicht erreichbar, https://nr24.kazas.dev/ liefert Verbindung fehlgeschlagen (Proxy verweigert die Verbindung mit Status 502) |

<a id="p6"></a>

## 6. Strukturierte Daten

Ergebnis **nicht prüfbar**.

| Teilprüfung | Ergebnis |
| --- | --- |
| Voraussetzung | ⚠️ nicht prüfbar |

### 6. Voraussetzung

| Art | Adresse | Fundstelle | Befund |
| --- | --- | --- | --- |
| Hinweis | https://nr24.kazas.dev/ | Prüflauf | Startseite nicht erreichbar, https://nr24.kazas.dev/ liefert Verbindung fehlgeschlagen (Proxy verweigert die Verbindung mit Status 502) |

<a id="p7"></a>

## 7. Pflichtangaben

Ergebnis **nicht prüfbar**.

| Teilprüfung | Ergebnis |
| --- | --- |
| Voraussetzung | ⚠️ nicht prüfbar |

### 7. Voraussetzung

| Art | Adresse | Fundstelle | Befund |
| --- | --- | --- | --- |
| Hinweis | https://nr24.kazas.dev/ | Prüflauf | Startseite nicht erreichbar, https://nr24.kazas.dev/ liefert Verbindung fehlgeschlagen (Proxy verweigert die Verbindung mit Status 502) |

<a id="p8"></a>

## 8. Barrierefreiheit

Ergebnis **nicht prüfbar**.

| Teilprüfung | Ergebnis |
| --- | --- |
| Voraussetzung | ⚠️ nicht prüfbar |

### 8. Voraussetzung

| Art | Adresse | Fundstelle | Befund |
| --- | --- | --- | --- |
| Hinweis | https://nr24.kazas.dev/ | Prüflauf | Startseite nicht erreichbar, https://nr24.kazas.dev/ liefert Verbindung fehlgeschlagen (Proxy verweigert die Verbindung mit Status 502) |

<a id="p9"></a>

## 9. Leistung

Ergebnis **nicht prüfbar**.

| Teilprüfung | Ergebnis |
| --- | --- |
| Voraussetzung | ⚠️ nicht prüfbar |

### 9. Voraussetzung

| Art | Adresse | Fundstelle | Befund |
| --- | --- | --- | --- |
| Hinweis | https://nr24.kazas.dev/ | Prüflauf | Startseite nicht erreichbar, https://nr24.kazas.dev/ liefert Verbindung fehlgeschlagen (Proxy verweigert die Verbindung mit Status 502) |

<a id="p10"></a>

## 10. E-Mail-DNS

Ergebnis **nicht bestanden**.

| Teilprüfung | Ergebnis |
| --- | --- |
| SPF endet auf -all oder ~all | ❌ nicht bestanden |
| DMARC vorhanden | ✅ bestanden |
| DKIM unter dem angegebenen Selektor | ⚠️ nicht prüfbar |

### 10. SPF endet auf -all oder ~all

| Art | Adresse | Fundstelle | Befund |
| --- | --- | --- | --- |
| Fehler | nr24.kazas.dev | TXT nr24.kazas.dev | Domain existiert nicht |

### 10. DMARC vorhanden

| Art | Adresse | Fundstelle | Befund |
| --- | --- | --- | --- |
| Beleg | nr24.kazas.dev | TXT _dmarc.kazas.dev | v=DMARC1; p=none; |
| Hinweis | nr24.kazas.dev | TXT _dmarc.kazas.dev | Gilt über die Organisationsdomain kazas.dev |
| Hinweis | nr24.kazas.dev | TXT _dmarc.kazas.dev | Richtlinie none beobachtet nur und schützt nicht vor Fälschungen |

### 10. DKIM unter dem angegebenen Selektor

| Art | Adresse | Fundstelle | Befund |
| --- | --- | --- | --- |
| Hinweis | nr24.kazas.dev | --dkim-selektor | Kein Selektor angegeben. Den Selektor nennt der E-Mail-Anbieter, etwa in einer Kopfzeile DKIM-Signature mit s= |

### 10. Hinweise

| Adresse | Fundstelle | Hinweis |
| --- | --- | --- |
| nr24.kazas.dev | Abfrage | Domain nr24.kazas.dev, abgefragt über DNS über HTTPS (https://dns.google/resolve) |
