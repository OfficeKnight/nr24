"""Wechselt beim direkten Aufruf in die venv unter pruefung/.venv, falls vorhanden."""
import os
import sys
from pathlib import Path

WURZEL = Path(__file__).resolve().parents[1]
_VENV = WURZEL / ".venv"
_PYTHON = _VENV / "bin" / "python"

if _PYTHON.exists() and Path(sys.prefix).resolve() != _VENV.resolve() \
        and not os.environ.get("ABNAHME_KEIN_VENV_WECHSEL"):
    os.execv(str(_PYTHON), [str(_PYTHON), *sys.argv])

if str(WURZEL) not in sys.path:
    sys.path.insert(0, str(WURZEL))
