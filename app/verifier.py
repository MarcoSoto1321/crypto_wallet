# app/verifier.py
import json
import base64
from pathlib import Path
from typing import Dict, Any

from cryptography.hazmat.primitives.asymmetric import ed25519

from .canonicalizer import canonical_bytes
from .crypto_utils import derive_address_btc_style

# Archivo donde se guarda el último nonce por address
NONCE_STATE_PATH = Path("nonce_state.json")


def _load_nonce_state(path: Path = NONCE_STATE_PATH) -> Dict[str, int]:
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    return {addr: int(nonce) for addr, nonce in data.items()}


def _save_nonce_state(state: Dict[str, int], path: Path = NONCE_STATE_PATH) -> None:
    path.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")