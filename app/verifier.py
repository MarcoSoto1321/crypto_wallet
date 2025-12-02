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


def verify_signed_tx(
    signed_tx: Dict[str, Any],
    nonce_state_path: str | None = None,
    enforce_nonce: bool = True,
) -> Dict[str, Any]:
    """
    Verifica:
    - Que la dirección derive de la pubkey y coincida con tx["from"]
    - Firma Ed25519
    - Que el nonce sea mayor al último visto (si enforce_nonce=True)

    Regresa: {"valid": bool, "reason": str}
    """
    try:
        tx = signed_tx["tx"]
        signature_b64 = signed_tx["signature_b64"]
        pubkey_b64 = signed_tx["pubkey_b64"]
        sig_scheme = signed_tx.get("sig_scheme", "Ed25519")

        if sig_scheme != "Ed25519":
            return {"valid": False, "reason": f"Unsupported sig_scheme {sig_scheme}"}

        signature = base64.b64decode(signature_b64)
        pub_bytes = base64.b64decode(pubkey_b64)

        # 1) Verificar que la address derive de la pubkey 
        derived_address = derive_address_btc_style(pub_bytes)
        tx_from = tx.get("from")
        if not tx_from:
            return {"valid": False, "reason": "tx.from missing"}

        # Esto atrapa el error "address mismatch" antes de que falle la firma
        if derived_address.lower() != str(tx_from).lower():
            return {"valid": False, "reason": "address mismatch"}

        # 2) Verificar firma
        public_key = ed25519.Ed25519PublicKey.from_public_bytes(pub_bytes)
        message = canonical_bytes(tx)
        # Si la firma no es válida, esto lanza una excepción
        public_key.verify(signature, message)

        # 3) Protección contra replay vía nonce
        if enforce_nonce:
            path_obj = NONCE_STATE_PATH if nonce_state_path is None else Path(nonce_state_path)
            nonce_state = _load_nonce_state(path_obj)

            sender_nonce = int(tx.get("nonce", 0))
            last_nonce = int(nonce_state.get(derived_address, -1))
            if sender_nonce <= last_nonce:
                return {"valid": False, "reason": f"stale nonce: {sender_nonce} <= {last_nonce}"}

            nonce_state[derived_address] = sender_nonce
            _save_nonce_state(nonce_state, path_obj)

        return {"valid": True, "reason": "ok"}

    except Exception as e:
        # Captura errores de firma (cryptography raise exceptions)
        return {"valid": False, "reason": f"exception: {e}"}