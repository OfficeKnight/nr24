"""Startet den Browserteil (Node, Playwright, axe-core) und liest dessen Ergebnis."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from .netz import aufloesung

WURZEL = Path(__file__).resolve().parents[1]
SKRIPT = WURZEL / "browser" / "erfassen.mjs"


class BrowserNichtVerfuegbar(Exception):
    pass


def browser_erfassen(kontext, urls: list) -> dict:
    node = shutil.which("node")
    if not node:
        raise BrowserNichtVerfuegbar("Node.js ist nicht installiert.")
    if not (WURZEL / "node_modules" / "playwright").exists() or not (WURZEL / "node_modules" / "axe-core").exists():
        raise BrowserNichtVerfuegbar("Playwright oder axe-core fehlen, bitte in pruefung/ npm ci ausführen.")
    eingabe = {
        "urls": urls,
        "pause_ms": int(kontext.pause * 1000),
        "wartezeit_ms": kontext.einstellungen.get("browser_wartezeit_ms", 2000),
        "aufloesen": aufloesung(),
        "https_fehler_ignorieren": bool(kontext.ca_datei),
        "axe_tags": kontext.einstellungen.get("axe_tags"),
    }
    with tempfile.TemporaryDirectory(prefix="abnahme-browser-") as tmp:
        ein = Path(tmp) / "eingabe.json"
        aus = Path(tmp) / "ausgabe.json"
        ein.write_text(json.dumps(eingabe), encoding="utf-8")
        lauf = subprocess.run([node, str(SKRIPT), str(ein), str(aus)], cwd=str(WURZEL),
                              stdout=subprocess.PIPE, stderr=sys.stderr, text=True,
                              timeout=60 * 60)
        if lauf.returncode != 0 or not aus.exists():
            raise BrowserNichtVerfuegbar(f"Browserlauf beendet mit Rückgabewert {lauf.returncode}.")
        return json.loads(aus.read_text(encoding="utf-8"))
