"""Prüfung 10. SPF, DMARC und DKIM im DNS."""
if __name__ == "__main__":
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    import lib.start  # noqa: F401

import re

from lib.dnsabfrage import FEHLER, NXDOMAIN, OK
from lib.kern import Beleg, Ergebnis

NUMMER = 10
TITEL = "E-Mail-DNS"


def _organisationsdomain(domain: str) -> str:
    """Einfache Näherung mit den letzten zwei Bestandteilen. Für Endungen wie co.uk ungenau."""
    teile = domain.split(".")
    return ".".join(teile[-2:]) if len(teile) > 2 else domain


def _spf_pruefen(k, domain: str, tiefe: int = 0):
    """Gibt (fehler, ok, unpruefbar) als Listen von Belegen zurück."""
    a = k.resolver.txt(domain)
    fund = f"TXT {domain}"
    if a.zustand == FEHLER:
        return [], [], [Beleg(domain, fund, f"Abfrage fehlgeschlagen ({a.fehler})")]
    spf = [t for t in a.eintraege if t.lower().startswith("v=spf1")]
    if not spf:
        grund = "Domain existiert nicht" if a.zustand == NXDOMAIN else "Kein Eintrag mit v=spf1"
        return [Beleg(domain, fund, grund)], [], []
    if len(spf) > 1:
        return [Beleg(domain, fund, f"{len(spf)} SPF-Einträge, erlaubt ist genau einer")], [], []
    eintrag = spf[0]
    teile = eintrag.split()
    letzter = teile[-1].lower()
    weiter = [t for t in teile if t.lower().startswith("redirect=")]
    if re.fullmatch(r"[-~]all", letzter):
        return [], [Beleg(domain, fund, eintrag)], []
    if re.fullmatch(r"[+?]?all", letzter):
        return [Beleg(domain, fund, f"{eintrag} endet auf {letzter} statt auf -all oder ~all")], [], []
    if weiter and tiefe < 3 and not any(t.lower().endswith("all") for t in teile):
        ziel = weiter[0].split("=", 1)[1]
        f, o, u = _spf_pruefen(k, ziel, tiefe + 1)
        if f:
            return f, o, u
        return [], [Beleg(domain, fund, f"{eintrag} verweist auf {ziel}")] + o, u
    return [Beleg(domain, fund, f"{eintrag} endet nicht auf -all oder ~all")], [], []


def pruefen(k) -> Ergebnis:
    erg = Ergebnis(NUMMER, TITEL)
    d = k.mail_domain
    erg.hinweis(d, "Abfrage", f"Domain {d}, abgefragt über {k.resolver.beschreibung}")

    f, o, u = _spf_pruefen(k, d)
    erg.bewerten("SPF endet auf -all oder ~all", f, o, None, u)

    # DMARC
    fehler, ok, hinweise, unpruefbar = [], [], [], []
    namen = [f"_dmarc.{d}"]
    org = _organisationsdomain(d)
    if org != d:
        namen.append(f"_dmarc.{org}")
    gefunden = None
    for name in namen:
        a = k.resolver.txt(name)
        if a.zustand == FEHLER:
            unpruefbar.append(Beleg(d, f"TXT {name}", f"Abfrage fehlgeschlagen ({a.fehler})"))
            break
        dmarc = [t for t in a.eintraege if t.replace(" ", "").lower().startswith("v=dmarc1")]
        if dmarc:
            gefunden = (name, dmarc)
            break
    if gefunden:
        name, dmarc = gefunden
        eintrag = dmarc[0]
        tags = {t.split("=", 1)[0].strip().lower(): t.split("=", 1)[1].strip()
                for t in eintrag.split(";") if "=" in t}
        if len(dmarc) > 1:
            fehler.append(Beleg(d, f"TXT {name}", f"{len(dmarc)} DMARC-Einträge, erlaubt ist genau einer"))
        elif "p" not in tags:
            fehler.append(Beleg(d, f"TXT {name}", f"{eintrag} ohne Richtlinie p"))
        else:
            ok.append(Beleg(d, f"TXT {name}", eintrag))
            richtlinie = tags.get("sp", tags["p"]) if name != f"_dmarc.{d}" else tags["p"]
            if name != f"_dmarc.{d}":
                hinweise.append(Beleg(d, f"TXT {name}", f"Gilt über die Organisationsdomain {org}"))
            if richtlinie.lower() == "none":
                hinweise.append(Beleg(d, f"TXT {name}", "Richtlinie none beobachtet nur und schützt nicht vor Fälschungen"))
    elif not unpruefbar:
        fehler.append(Beleg(d, " und ".join(f"TXT {n}" for n in namen), "Kein Eintrag mit v=DMARC1"))
    erg.bewerten("DMARC vorhanden", fehler, ok, hinweise, unpruefbar)

    # DKIM
    if not k.dkim_selektor:
        erg.nicht_pruefbar("DKIM unter dem angegebenen Selektor", d, "--dkim-selektor",
                           "Kein Selektor angegeben. Den Selektor nennt der E-Mail-Anbieter, etwa in einer Kopfzeile DKIM-Signature mit s=")
        return erg
    name = f"{k.dkim_selektor}._domainkey.{d}"
    a = k.resolver.txt(name)
    if a.zustand == FEHLER:
        erg.nicht_pruefbar("DKIM unter dem angegebenen Selektor", d, f"TXT {name}", f"Abfrage fehlgeschlagen ({a.fehler})")
        return erg
    fehler, ok = [], []
    if a.zustand != OK:
        fehler.append(Beleg(d, f"TXT {name}", "Kein Eintrag gefunden"))
    else:
        eintrag = " ".join(a.eintraege)
        m = re.search(r"(?:^|;)\s*p=([^;]*)", eintrag)
        if not m:
            fehler.append(Beleg(d, f"TXT {name}", f"Kein Schlüssel p= im Eintrag ({eintrag[:80]})"))
        elif not m.group(1).strip():
            fehler.append(Beleg(d, f"TXT {name}", "Schlüssel p= ist leer, der Schlüssel ist widerrufen"))
        else:
            ok.append(Beleg(d, f"TXT {name}", f"Öffentlicher Schlüssel mit {len(m.group(1).strip())} Zeichen"))
    erg.bewerten("DKIM unter dem angegebenen Selektor", fehler, ok)
    return erg


if __name__ == "__main__":
    from lib.ablauf import einzeln
    einzeln(sys.modules[__name__])
