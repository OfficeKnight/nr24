"""Gemeinsame Datentypen für alle Prüfungen."""
from __future__ import annotations

from dataclasses import dataclass, field

BESTANDEN = "bestanden"
NICHT_BESTANDEN = "nicht bestanden"
NICHT_PRUEFBAR = "nicht prüfbar"

_RANG = {BESTANDEN: 0, NICHT_PRUEFBAR: 1, NICHT_BESTANDEN: 2}

# Art eines Belegs
FEHLER = "fehler"
HINWEIS = "hinweis"
OK = "ok"


@dataclass
class Beleg:
    adresse: str
    fundstelle: str
    befund: str
    art: str = FEHLER

    def als_dict(self) -> dict:
        return {"adresse": self.adresse, "fundstelle": self.fundstelle,
                "befund": self.befund, "art": self.art}


@dataclass
class Teilpruefung:
    name: str
    status: str
    belege: list = field(default_factory=list)

    def als_dict(self) -> dict:
        return {"name": self.name, "status": self.status,
                "belege": [b.als_dict() for b in self.belege]}


@dataclass
class Ergebnis:
    nummer: int
    titel: str
    teile: list = field(default_factory=list)
    hinweise: list = field(default_factory=list)

    @property
    def status(self) -> str:
        if not self.teile:
            return NICHT_PRUEFBAR
        return max((t.status for t in self.teile), key=_RANG.get)

    def teil(self, name: str, status: str, belege=None) -> Teilpruefung:
        t = Teilpruefung(name, status, list(belege or []))
        self.teile.append(t)
        return t

    def bewerten(self, name: str, fehler: list, ok: list | None = None,
                 hinweise: list | None = None, unpruefbar: list | None = None) -> Teilpruefung:
        """Legt eine Teilprüfung an. Fehlerbelege führen zu nicht bestanden,
        sonst führen Belege in unpruefbar zu nicht prüfbar."""
        for b in fehler:
            b.art = FEHLER
        for b in ok or []:
            b.art = OK
        for b in list(hinweise or []) + list(unpruefbar or []):
            b.art = HINWEIS
        if fehler:
            status = NICHT_BESTANDEN
        elif unpruefbar:
            status = NICHT_PRUEFBAR
        else:
            status = BESTANDEN
        return self.teil(name, status, list(fehler) + list(unpruefbar or []) + list(ok or [])
                         + list(hinweise or []))

    def nicht_pruefbar(self, name: str, adresse: str, fundstelle: str, grund: str) -> Teilpruefung:
        return self.teil(name, NICHT_PRUEFBAR, [Beleg(adresse, fundstelle, grund, HINWEIS)])

    def hinweis(self, adresse: str, fundstelle: str, text: str) -> None:
        self.hinweise.append(Beleg(adresse, fundstelle, text, HINWEIS))

    def als_dict(self) -> dict:
        return {"nummer": self.nummer, "titel": self.titel, "status": self.status,
                "teilpruefungen": [t.als_dict() for t in self.teile],
                "hinweise": [h.als_dict() for h in self.hinweise]}


def gesamtstatus(ergebnisse: list) -> str:
    if not ergebnisse:
        return NICHT_PRUEFBAR
    return max((e.status for e in ergebnisse), key=_RANG.get)


class NichtPruefbar(Exception):
    """Wird geworfen, wenn eine Voraussetzung fehlt, etwa die Startseite nicht erreichbar ist."""
