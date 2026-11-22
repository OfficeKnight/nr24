"""Schreibt Berichte als Markdown und als JSON."""
from __future__ import annotations

import json
from pathlib import Path

from .kern import BESTANDEN, NICHT_BESTANDEN, NICHT_PRUEFBAR, gesamtstatus

MAX_ZEILEN_MD = 40
SYMBOL = {BESTANDEN: "✅ bestanden", NICHT_BESTANDEN: "❌ nicht bestanden", NICHT_PRUEFBAR: "⚠️ nicht prüfbar"}
ART = {"fehler": "Fehler", "hinweis": "Hinweis", "ok": "Beleg"}


def verzeichnis(kontext) -> Path:
    datum = kontext.beginn.strftime("%Y-%m-%d")
    return kontext.berichte / f"{datum}-{kontext.zielhost}"


def _zelle(text) -> str:
    t = str(text if text is not None else "").replace("\n", " ").replace("|", "\\|").strip()
    return t[:300] + (" …" if len(t) > 300 else "")


def daten(kontext, ergebnisse: list) -> dict:
    from .kontext import VERSION
    try:
        haupt = kontext.hauptadresse
    except Exception:
        haupt = None
    erfasst = len(kontext._erfassung.html_seiten()) if kontext._erfassung else 0
    return {
        "werkzeug": f"nr24-Abnahmepruefung {VERSION}",
        "ziel": kontext.ziel,
        "hauptadresse": haupt,
        "modus": kontext.modus,
        "beginn": kontext.beginn.isoformat(timespec="seconds"),
        "abrufe": kontext.abrufer.anzahl,
        "erfasste_html_seiten": erfasst,
        "gesamtergebnis": gesamtstatus(ergebnisse),
        "pruefungen": [e.als_dict() for e in ergebnisse],
    }


def markdown(d: dict) -> str:
    z = []
    z.append(f"# Abnahmeprüfung {d['ziel']}")
    z.append("")
    z.append("Der Bericht prüft das Vorhandensein technischer und inhaltlicher Merkmale. "
             "Er ist keine Rechtsberatung.")
    z.append("")
    z.append("| Angabe | Wert |")
    z.append("| --- | --- |")
    for k, v in (("Ziel", d["ziel"]), ("Hauptadresse", d["hauptadresse"] or "nicht ermittelt"),
                 ("Modus", d["modus"]), ("Beginn", d["beginn"]), ("Werkzeug", d["werkzeug"]),
                 ("HTTP-Abrufe", d["abrufe"]), ("Erfasste HTML-Seiten", d["erfasste_html_seiten"]),
                 ("Gesamtergebnis", SYMBOL[d["gesamtergebnis"]])):
        z.append(f"| {k} | {_zelle(v)} |")
    z.append("")
    z.append("## Übersicht")
    z.append("")
    z.append("| Nr. | Prüfung | Ergebnis |")
    z.append("| --- | --- | --- |")
    for p in d["pruefungen"]:
        z.append(f"| {p['nummer']} | [{p['titel']}](#p{p['nummer']}) | {SYMBOL[p['status']]} |")
    for p in d["pruefungen"]:
        z.append("")
        z.append(f'<a id="p{p["nummer"]}"></a>')
        z.append("")
        z.append(f"## {p['nummer']}. {p['titel']}")
        z.append("")
        z.append(f"Ergebnis **{p['status']}**.")
        z.append("")
        z.append("| Teilprüfung | Ergebnis |")
        z.append("| --- | --- |")
        for t in p["teilpruefungen"]:
            z.append(f"| {_zelle(t['name'])} | {SYMBOL[t['status']]} |")
        for t in p["teilpruefungen"]:
            if not t["belege"]:
                continue
            z.append("")
            z.append(f"### {p['nummer']}. {t['name']}")
            z.append("")
            z.append("| Art | Adresse | Fundstelle | Befund |")
            z.append("| --- | --- | --- | --- |")
            for b in t["belege"][:MAX_ZEILEN_MD]:
                z.append(f"| {ART.get(b['art'], b['art'])} | {_zelle(b['adresse'])} | "
                         f"{_zelle(b['fundstelle'])} | {_zelle(b['befund'])} |")
            if len(t["belege"]) > MAX_ZEILEN_MD:
                z.append("")
                z.append(f"Weitere {len(t['belege']) - MAX_ZEILEN_MD} Belege stehen in der JSON-Datei.")
        if p["hinweise"]:
            z.append("")
            z.append(f"### {p['nummer']}. Hinweise")
            z.append("")
            z.append("| Adresse | Fundstelle | Hinweis |")
            z.append("| --- | --- | --- |")
            for b in p["hinweise"][:MAX_ZEILEN_MD]:
                z.append(f"| {_zelle(b['adresse'])} | {_zelle(b['fundstelle'])} | {_zelle(b['befund'])} |")
    z.append("")
    return "\n".join(z)


def schreiben(kontext, ergebnisse: list, name: str = "bericht") -> Path:
    ziel = verzeichnis(kontext)
    ziel.mkdir(parents=True, exist_ok=True)
    d = daten(kontext, ergebnisse)
    (ziel / f"{name}.json").write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (ziel / f"{name}.md").write_text(markdown(d), encoding="utf-8")
    return ziel
