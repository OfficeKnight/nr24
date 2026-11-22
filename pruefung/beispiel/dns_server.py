#!/usr/bin/env python3
"""Kleiner DNS-Server für die Beispielhosts. Beantwortet nur TXT-Abfragen aus der Tabelle unten.

Aufruf mit python3 dns_server.py [--port 5353]
"""
import argparse
import socket
import struct

EINTRAEGE = {
    "gut.test": ["v=spf1 mx -all"],
    "_dmarc.gut.test": ["v=DMARC1; p=reject; rua=mailto:dmarc@gut.test"],
    "mail._domainkey.gut.test": ["v=DKIM1; k=rsa; p=MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQC1beispielschluessel"],
    "live.test": ["v=spf1 include:_spf.live.test ~all"],
    "_dmarc.live.test": ["v=DMARC1; p=quarantine"],
    "mail._domainkey.live.test": ["v=DKIM1; k=rsa; p=MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQC2beispielschluessel"],
    "schlecht.test": ["v=spf1 a mx +all"],
    "mail._domainkey.schlecht.test": ["v=DKIM1; k=rsa; p="],
}
VORHANDEN = {"gut.test", "live.test", "schlecht.test", "www.gut.test", "www.live.test", "www.schlecht.test"}


def name_lesen(daten: bytes, pos: int):
    teile = []
    while True:
        laenge = daten[pos]
        if laenge == 0:
            return ".".join(teile), pos + 1
        teile.append(daten[pos + 1:pos + 1 + laenge].decode("ascii", "replace"))
        pos += 1 + laenge


def antwort(anfrage: bytes) -> bytes:
    kennung, _flags, anzahl = struct.unpack(">HHH", anfrage[:6])
    name, pos = name_lesen(anfrage, 12)
    typ, klasse = struct.unpack(">HH", anfrage[pos:pos + 4])
    frage = anfrage[12:pos + 4]
    name_klein = name.lower().rstrip(".")
    texte = EINTRAEGE.get(name_klein, []) if typ == 16 else []
    existiert = name_klein in EINTRAEGE or name_klein in VORHANDEN
    rcode = 0 if existiert else 3
    kopf = struct.pack(">HHHHHH", kennung, 0x8400 | rcode, 1, len(texte), 0, 0)
    teile = [kopf, frage]
    for t in texte:
        roh = t.encode("utf-8")
        stuecke = b"".join(bytes([len(roh[i:i + 255])]) + roh[i:i + 255] for i in range(0, max(len(roh), 1), 255))
        teile.append(b"\xc0\x0c" + struct.pack(">HHIH", 16, 1, 60, len(stuecke)) + stuecke)
    return b"".join(teile)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--adresse", default="127.0.0.1")
    p.add_argument("--port", type=int, default=5353)
    args = p.parse_args()
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((args.adresse, args.port))
    print(f"DNS-Server auf {args.adresse}:{args.port}", flush=True)
    while True:
        daten, absender = s.recvfrom(4096)
        try:
            s.sendto(antwort(daten), absender)
        except (IndexError, struct.error):
            pass


if __name__ == "__main__":
    main()
