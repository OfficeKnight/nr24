"""Die zehn Prüfmodule. Jedes Modul lässt sich auch einzeln aufrufen."""
from . import (p01_adressen, p02_tls, p03_sicherheitsheader, p04_einwilligung, p05_auffindbarkeit,
               p06_strukturdaten, p07_pflichtangaben, p08_barrierefreiheit, p09_leistung, p10_email_dns)

ALLE = [p01_adressen, p02_tls, p03_sicherheitsheader, p04_einwilligung, p05_auffindbarkeit,
        p06_strukturdaten, p07_pflichtangaben, p08_barrierefreiheit, p09_leistung, p10_email_dns]
