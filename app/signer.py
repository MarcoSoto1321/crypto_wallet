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
        if tx[field] is None or tx[field] == "":
            raise ValueError(f"El campo '{field}' no puede estar vacío.")

    # Validar dirección destino
    if not isinstance(tx["to"], str):
        raise TypeError("El campo 'to' debe ser una cadena (dirección).")

    # Validar 'value'
    value = tx["value"]
    if isinstance(value, int):
        pass
    elif isinstance(value, str) and value.isdigit():
        pass
    else:
        raise ValueError("El campo 'value' debe ser un entero o un string numérico.")

    # Validar 'nonce' entero uint64
    if not isinstance(tx["nonce"], int):
        raise TypeError("El campo 'nonce' debe ser un entero (uint64).")
    if tx["nonce"] < 0:
        raise ValueError("El campo 'nonce' no puede ser negativo.")

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
    """
    # Validar transacción antes de firmar
    validate_tx(tx)

    # ---------------------------
    # 1. Cargar keystore
    # ---------------------------
    try:
        keystore = load_keystore(keystore_path)
    except FileNotFoundError as e:   
        raise FileNotFoundError("No se encontró el archivo de keystore en la ruta dada.") from e
    except Exception as e:           
        raise RuntimeError(f"Error al cargar el keystore: {e}") from e

    # 2. Desbloquear clave privada
    try:
        private_key_bytes, public_key_bytes, address = unlock_keystore(keystore, passphrase)
    except Exception as e:          
        raise ValueError(f"Error al desbloquear el keystore. "
                         f"Passphrase incorrecta o archivo corrupto: {e}") from e

    # 3. Insertar campo 'from'
    if not tx.get("from"):
        tx["from"] = address

    # ---------------------------
    # 4. Creación de bytes canónicos
    # ---------------------------
    try:
        message = canonical_bytes(tx)
    except Exception as e:          
        raise RuntimeError(f"Error al generar bytes canónicos de la transacción: {e}") from e

    # 5. Crear objeto de llave privada
    try:
        priv = ed25519.Ed25519PrivateKey.from_private_bytes(private_key_bytes)
    except Exception as e:           
        raise RuntimeError("La llave privada del keystore es inválida o está corrupta.") from e

    # 6. Firmar mensaje
    try:
        signature = priv.sign(message)
    except Exception as e:           
        raise RuntimeError(f"Error al firmar la transacción: {e}") from e

    # 7. Construir paquete firmado
    signed_tx: Dict[str, Any] = {
        "tx": tx,
        "sig_scheme": "Ed25519",
        "signature_b64": base64.b64encode(signature).decode("utf-8"),
        "pubkey_b64": base64.b64encode(public_key_bytes).decode("utf-8"),
    }

    return signed_tx
