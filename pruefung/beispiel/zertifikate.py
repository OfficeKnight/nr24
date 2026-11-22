#!/usr/bin/env python3
"""Erzeugt eine Test-Zertifizierungsstelle und Zertifikate für die Beispielhosts.

Die Dateien landen in beispiel/zertifikate/ und werden nicht eingecheckt.
schlecht.test bekommt absichtlich ein Zertifikat mit nur 10 Tagen Laufzeit.
"""
import subprocess
from pathlib import Path

ZIEL = Path(__file__).resolve().parent / "zertifikate"
HOSTS = {"gut": 365, "live": 365, "drittanbieter": 365, "schlecht": 10}


def openssl(*args: str) -> None:
    subprocess.run(["openssl", *args], check=True, cwd=ZIEL, capture_output=True)


def main() -> None:
    ZIEL.mkdir(exist_ok=True)
    if not (ZIEL / "ca.crt").exists():
        openssl("req", "-x509", "-newkey", "rsa:2048", "-nodes", "-keyout", "ca.key", "-out", "ca.crt",
                "-days", "30", "-subj", "/CN=Beispiel Test-CA", "-addext", "basicConstraints=critical,CA:TRUE",
                "-addext", "keyUsage=critical,keyCertSign,cRLSign")
    for name, tage in HOSTS.items():
        namen = [f"{name}.test"] + ([f"www.{name}.test"] if name != "drittanbieter" else [])
        (ZIEL / f"{name}.ext").write_text(
            "basicConstraints=CA:FALSE\nkeyUsage=digitalSignature,keyEncipherment\n"
            "extendedKeyUsage=serverAuth\nsubjectAltName=" + ",".join(f"DNS:{n}" for n in namen) + "\n",
            encoding="utf-8")
        openssl("req", "-new", "-newkey", "rsa:2048", "-nodes", "-keyout", f"{name}.key", "-out", f"{name}.csr",
                "-subj", f"/CN={namen[0]}")
        openssl("x509", "-req", "-in", f"{name}.csr", "-CA", "ca.crt", "-CAkey", "ca.key", "-CAcreateserial",
                "-out", f"{name}.crt", "-days", str(tage), "-extfile", f"{name}.ext")
    print(f"Zertifikate in {ZIEL}")


if __name__ == "__main__":
    main()
