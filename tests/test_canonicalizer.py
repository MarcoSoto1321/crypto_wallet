# tests/test_canonicalizer.py
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.canonicalizer import canonical_json, canonical_bytes  # noqa: E402


def test_canonical_json_sorting():
    data = {"b": 2, "a": 1}
    cj = canonical_json(data)
    assert cj == '{"a":1,"b":2}'


def test_canonical_bytes():
    data = {"z": 3}
    cb = canonical_bytes(data)
    assert cb == canonical_json(data).encode("utf-8")
