# app/signer.py
import base64
from typing import Dict, Any

from cryptography.hazmat.primitives.asymmetric import ed25519

from .canonicalizer import canonical_bytes
from .keystore import load_keystore, unlock_keystore


def sign_transaction(
    keystore_path: str,
    passphrase: str,
    tx: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Firma una transacción usando la llave privada almacenada en el keystore.

    Regresa un paquete de transacción firmada:
    {
      "tx": {...},
      "sig_scheme": "Ed25519",
      "signature_b64": "...",
      "pubkey_b64": "..."
    }
    """
    keystore = load_keystore(keystore_path)
    private_key_bytes, public_key_bytes, address = unlock_keystore(keystore, passphrase)

    # Si el campo "from" no está, lo rellenamos con la dirección de este keystore
    if not tx.get("from"):
        tx["from"] = address

    message = canonical_bytes(tx)
    priv = ed25519.Ed25519PrivateKey.from_private_bytes(private_key_bytes)
    signature = priv.sign(message)

    signed_tx: Dict[str, Any] = {
        "tx": tx,
        "sig_scheme": "Ed25519",
        "signature_b64": base64.b64encode(signature).decode("utf-8"),
        "pubkey_b64": base64.b64encode(public_key_bytes).decode("utf-8"),
    }
    return signed_tx
