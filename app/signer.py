# app/signer.py
import base64
import datetime
from typing import Dict, Any

from cryptography.hazmat.primitives.asymmetric import ed25519

from .canonicalizer import canonical_bytes
from .keystore import load_keystore, unlock_keystore

# ============================================================
# VALIDACIÓN DE TRANSACCIONES
# ============================================================
def validate_tx(tx: Dict[str, Any]) -> None:
    """
    Valida que la transacción tenga los campos necesarios y en formato correcto.
    Lanza excepciones explícitas para facilitar depuración y verificación.
    """
    required = ["to", "value", "nonce", "timestamp"]

    # Validar presencia de campos obligatorios
    for field in required:
        if field not in tx:
            raise ValueError(f"Falta el campo obligatorio '{field}' en la transacción.")

    # Validar dirección destino
    if not isinstance(tx["to"], str):
        raise TypeError("El campo 'to' debe ser una cadena (dirección).")

    # Validar timestamp ISO8601
    try:
        datetime.datetime.fromisoformat(tx["timestamp"])
    except Exception:
        raise ValueError("El campo 'timestamp' no está en formato ISO8601.")

# ============================================================
# FUNCIÓN PRINCIPAL: FIRMAR TRANSACCIÓN
# ============================================================
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

    # Validar transacción antes de firmar
    validate_tx(tx)

    # Cargar keystore y recuperar llaves
    keystore = load_keystore(keystore_path)
    private_key_bytes, public_key_bytes, address = unlock_keystore(keystore, passphrase)

    # Si el campo "from" no está, lo rellenamos con la dirección de este keystore
    if not tx.get("from"):
        tx["from"] = address

    # Crear bytes canónicos del mensaje
    message = canonical_bytes(tx)

    # Firmar usando Ed25519
    priv = ed25519.Ed25519PrivateKey.from_private_bytes(private_key_bytes)
    signature = priv.sign(message)

    # Construir paquete firmado
    signed_tx: Dict[str, Any] = {
        "tx": tx,
        "sig_scheme": "Ed25519",
        "signature_b64": base64.b64encode(signature).decode("utf-8"),
        "pubkey_b64": base64.b64encode(public_key_bytes).decode("utf-8"),
    }

    return signed_tx
