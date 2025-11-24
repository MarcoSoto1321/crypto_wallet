# app/canonicalizer.py
import json
from typing import Any, Dict


def canonical_json(data: Dict[str, Any]) -> str:
    """
    JSON canónico:
    - Llaves ordenadas lexicográficamente.
    - Sin espacios extra.
    """
    return json.dumps(
        data,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def canonical_bytes(data: Dict[str, Any]) -> bytes:
    """
    JSON canónico codificado en UTF-8 (para firmar/verificar).
    """
    return canonical_json(data).encode("utf-8")
