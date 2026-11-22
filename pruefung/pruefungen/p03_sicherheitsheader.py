"""Prüfung 3. Sicherheitsheader und Cookie-Attribute."""
if __name__ == "__main__":
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    import lib.start  # noqa: F401

import re

from lib.kern import Beleg, Ergebnis, NichtPruefbar

NUMMER = 3
TITEL = "Sicherheitsheader und Cookies"

FELD = {"HSTS": "Strict-Transport-Security", "Schutz gegen Einbetten": "X-Frame-Options oder CSP frame-ancestors"}
SICHERE_REFERRER = {"no-referrer", "same-origin", "strict-origin", "strict-origin-when-cross-origin",
                    "origin", "origin-when-cross-origin"}


def _meta_csp(seite) -> str | None:
    for m in seite.soup.find_all("meta"):
        if (m.get("http-equiv") or "").lower() == "content-security-policy":
            return m.get("content") or ""
    return None


def _pruefe_seite(seite, mindestalter: int) -> dict:
    """Gibt je Header (fehler, text) zurück."""
    h = seite.antwort.headers
    r = {}
    hsts = h.get("strict-transport-security")
    if not hsts:
        r["HSTS"] = (True, "Header Strict-Transport-Security fehlt")
    else:
        m = re.search(r"max-age\s*=\s*\"?(\d+)", hsts, re.I)
        alter = int(m.group(1)) if m else 0
        if alter < mindestalter:
            r["HSTS"] = (True, f"max-age={alter} ist kleiner als {mindestalter}")
        else:
            r["HSTS"] = (False, hsts)
    csp = h.get("content-security-policy")
    meta = _meta_csp(seite)
    if csp:
        r["Content-Security-Policy"] = (False, csp)
    elif meta is not None:
        r["Content-Security-Policy"] = (False, f"nur als meta-Element gesetzt ({meta})")
    elif h.get("content-security-policy-report-only"):
        r["Content-Security-Policy"] = (True, "Nur Content-Security-Policy-Report-Only gesetzt, das schützt nicht")
    else:
        r["Content-Security-Policy"] = (True, "Header Content-Security-Policy fehlt")
    xcto = h.get("x-content-type-options", "")
    r["X-Content-Type-Options"] = (xcto.strip().lower() != "nosniff",
                                   xcto or "Header X-Content-Type-Options fehlt")
    rp = h.get("referrer-policy", "")
    werte = [w.strip().lower() for w in rp.split(",") if w.strip()]
    if not werte:
        r["Referrer-Policy"] = (True, "Header Referrer-Policy fehlt")
    elif werte[-1] not in SICHERE_REFERRER:
        r["Referrer-Policy"] = (True, f"Wert {rp} gibt vollständige Adressen an fremde Seiten weiter")
    else:
        r["Referrer-Policy"] = (False, rp)
    pp = h.get("permissions-policy")
    r["Permissions-Policy"] = (not pp, pp or "Header Permissions-Policy fehlt")
    xfo = h.get("x-frame-options", "").strip().upper()
    fa = re.search(r"frame-ancestors\s+([^;]+)", csp or "", re.I)
    if fa:
        r["Schutz gegen Einbetten"] = (False, f"CSP frame-ancestors {fa.group(1).strip()}")
    elif xfo in ("DENY", "SAMEORIGIN"):
        r["Schutz gegen Einbetten"] = (False, f"X-Frame-Options {xfo}")
    else:
        r["Schutz gegen Einbetten"] = (True, "Weder X-Frame-Options noch CSP frame-ancestors im Header")
    return r


def _cookie_lesen(kopf: str) -> dict:
    teile = [t.strip() for t in kopf.split(";")]
    name, _, wert = teile[0].partition("=")
    attr = {}
    for t in teile[1:]:
        k, _, v = t.partition("=")
        attr[k.strip().lower()] = v.strip()
    return {"name": name.strip(), "attr": attr}


def pruefen(k) -> Ergebnis:
    erg = Ergebnis(NUMMER, TITEL)
    e = k.erfassung()
    seiten = e.html_seiten()
    if not seiten:
        raise NichtPruefbar("Keine erreichbare HTML-Seite gefunden.")
    mindestalter = int(k.einstellungen.get("hsts_mindestalter_sekunden", 15552000))
    befunde = {s.endadresse: _pruefe_seite(s, mindestalter) for s in seiten}
    for kopf in ("HSTS", "Content-Security-Policy", "X-Content-Type-Options", "Referrer-Policy",
                 "Permissions-Policy", "Schutz gegen Einbetten"):
        fehler, ok, hinweise = [], [], []
        werte = {}
        for adr, r in befunde.items():
            ist_fehler, text = r[kopf]
            if ist_fehler:
                fehler.append(Beleg(adr, f"Antwortheader {FELD.get(kopf, kopf)}", text))
            else:
                werte.setdefault(text, []).append(adr)
        for text, adressen in werte.items():
            ok.append(Beleg(adressen[0], f"Antwortheader {FELD.get(kopf, kopf)}",
                            f"{text} (auf {len(adressen)} von {len(seiten)} Seiten)"))
            if kopf == "Content-Security-Policy":
                if text.startswith("nur als meta"):
                    hinweise.append(Beleg(adressen[0], "meta http-equiv",
                                          "CSP nur im HTML, frame-ancestors und Berichte wirken dort nicht"))
                if "'unsafe-inline'" in text and "script-src" in text and \
                        re.search(r"script-src[^;]*'unsafe-inline'", text):
                    hinweise.append(Beleg(adressen[0], "script-src", "Erlaubt Inline-Skripte mit unsafe-inline"))
        erg.bewerten(f"{kopf} gesetzt", fehler, ok, hinweise)

    # Cookies aus Set-Cookie
    pflicht = re.compile(k.einstellungen.get("httponly_pflicht_muster", "(?i)sess"))
    ausnahme = re.compile(k.einstellungen.get("httponly_ausnahmen_muster", "(?i)csrf"))
    gesehen = {}
    antworten = [(s.endadresse, s.antwort) for s in e.seiten.values()]
    if e.robots:
        antworten.append((e.robots.url, e.robots))
    antworten += [(a.url, a) for a in e.sitemaps]
    for adr, a in antworten:
        for kopf in a.set_cookies:
            c = _cookie_lesen(kopf)
            gesehen.setdefault(c["name"], (adr, c, kopf))
    fehler, ok, hinweise = [], [], []
    for name, (adr, c, kopf) in sorted(gesehen.items()):
        attr = c["attr"]
        fund = f"Set-Cookie {name}"
        maengel = []
        if "secure" not in attr:
            maengel.append("Secure fehlt")
        same = attr.get("samesite", "").lower()
        if not same:
            maengel.append("SameSite fehlt")
        elif same not in ("lax", "strict", "none"):
            maengel.append(f"SameSite={attr.get('samesite')} ist ungültig")
        elif same == "none" and "secure" not in attr:
            maengel.append("SameSite=None ohne Secure")
        if "httponly" not in attr:
            if pflicht.search(name) and not ausnahme.search(name):
                maengel.append("HttpOnly fehlt bei einem Sitzungs- oder Anmeldecookie")
            else:
                hinweise.append(Beleg(adr, fund, "Ohne HttpOnly, für Skripte lesbar. Bitte prüfen, ob das nötig ist"))
        if maengel:
            fehler.append(Beleg(adr, fund, ", ".join(maengel)))
        else:
            ok.append(Beleg(adr, fund, "Attribute " + ", ".join(
                f"{a}={v}" if v else a for a, v in attr.items() if a in ("secure", "httponly", "samesite"))))
    if not gesehen:
        ok.append(Beleg(k.hauptadresse, "Set-Cookie", f"Keine Cookies in {len(antworten)} Antworten gesetzt"))
    erg.bewerten("Cookies tragen Secure, HttpOnly und SameSite", fehler, ok, hinweise)
    erg.hinweis(k.hauptadresse, "Umfang",
                "Geprüft wurden Cookies aus Set-Cookie-Headern der Endantworten. Per Skript gesetzte Cookies stehen in Prüfung 4")
    return erg


if __name__ == "__main__":
    from lib.ablauf import einzeln
    einzeln(sys.modules[__name__])
