# app/signer.py

"""
Módulo encargado de firmar transacciones usando Ed25519.

Aquí solo se realiza el firmado; la verificación va en otro módulo. 
El flujo general es:

1) Validar que la transacción tenga los campos básicos y en el formato correcto.
2) Cargar el keystore y obtener la clave privada asociada.
3) Si la transacción no incluye el campo "from", se usa la dirección del keystore.
4) Se genera una versión JSON canónica para asegurar que siempre se firme lo mismo.
5) La firma se genera con Ed25519.
6) Se regresa un diccionario con la transacción firmada, la firma base64 y la llave pública.

"""

import base64
import datetime
from typing import Dict, Any

from cryptography.hazmat.primitives.asymmetric import ed25519

from .canonicalizer import canonical_bytes
from .keystore import load_keystore, unlock_keystore


# ------------------------------------------------------------
# Validación básica de la transacción
# ------------------------------------------------------------
def validate_tx(tx: Dict[str, Any]) -> None:
    """
    Revisa que la transacción cuente con los campos mínimos y que
    sus valores tengan un formato razonable.
    """

    required = ["to", "value", "nonce", "timestamp"]

    # Validar presencia y contenido
    for field in required:
        if field not in tx:
            raise ValueError(f"Falta el campo obligatorio '{field}'.")
        if tx[field] is None or tx[field] == "":
            raise ValueError(f"El campo '{field}' no puede quedar vacío.")

    # Dirección destino
    if not isinstance(tx["to"], str):
        raise TypeError("El campo 'to' debe ser una cadena.")

    # 'value' puede ser entero o string numérico
    value = tx["value"]
    if not (isinstance(value, int) or (isinstance(value, str) and value.isdigit())):
        raise ValueError("El campo 'value' debe ser un entero o string numérico.")

    # 'nonce' debe ser entero y no negativo
    if not isinstance(tx["nonce"], int):
        raise TypeError("El campo 'nonce' debe ser un entero.")
    if tx["nonce"] < 0:
        raise ValueError("El 'nonce' no puede ser negativo.")

    # Formato de timestamp
    try:
        datetime.datetime.fromisoformat(tx["timestamp"])
    except Exception:
        raise ValueError("El campo 'timestamp' debe estar en formato ISO8601.")


# ------------------------------------------------------------
# Función principal: firmado
# ------------------------------------------------------------
def sign_transaction(
    keystore_path: str,
    passphrase: str,
    tx: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Firma una transacción usando la clave privada almacenada en el keystore.

    Regresa un paquete con:
      - La transacción original
      - El esquema de firma
      - La firma en Base64
      - La llave pública correspondiente
    """

    # Validación previa
    validate_tx(tx)

    # 1. Cargar keystore
    try:
        keystore = load_keystore(keystore_path)
    except FileNotFoundError as e:
        raise FileNotFoundError("No se encontró el archivo de keystore.") from e
    except Exception as e:
        raise RuntimeError(f"Error al cargar el keystore: {e}") from e

    # 2. Recuperar claves desde el keystore
    try:
        private_key_bytes, public_key_bytes, address = unlock_keystore(keystore, passphrase)
    except Exception as e:
        raise ValueError("La passphrase es incorrecta o el keystore está dañado.") from e

    # 3. Asignar campo 'from' si no existe
    if not tx.get("from"):
        tx["from"] = address

    # 4. Obtener representación canónica
    try:
        message = canonical_bytes(tx)
    except Exception as e:
        raise RuntimeError(f"Error al generar JSON canónico: {e}") from e

    # 5. Cargar clave privada Ed25519
    try:
        priv = ed25519.Ed25519PrivateKey.from_private_bytes(private_key_bytes)
    except Exception:
        raise RuntimeError("La clave privada en el keystore no es válida.")

    # 6. Generar la firma
    try:
        signature = priv.sign(message)
    except Exception as e:
        raise RuntimeError(f"Error durante el firmado: {e}") from e

    # 7. Paquete final
    signed_tx: Dict[str, Any] = {
        "tx": tx,
        "sig_scheme": "Ed25519",
        "signature_b64": base64.b64encode(signature).decode("utf-8"),
        "pubkey_b64": base64.b64encode(public_key_bytes).decode("utf-8"),
    }

    return signed_tx
