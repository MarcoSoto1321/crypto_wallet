import json
import base64
import sys
import pytest
from cryptography.exceptions import InvalidTag
from pathlib import Path
from app.keystore import create_keystore, save_keystore, load_keystore, unlock_keystore

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

def test_keystore_flow():
    """
    Prueba completa de creación, guardado, carga (con comprobación) y desbloqueo de un keystore
    El mejor de los casos donde todo funciona correctamente
    """
    passphrase = "Hola123"
    path = Path("test_wallet.keystore.json")

    ks = create_keystore(passphrase)
    assert "ciphertext_b64" in ks
    save_keystore(ks, path)
    assert path.exists()

    ks2 = load_keystore(path)
    assert ks2["pubkey_b64"] == ks["pubkey_b64"]

    priv, pub, addr = unlock_keystore(ks2, passphrase)
    assert len(priv) == 32
    assert addr.startswith("0x")

    # Intento de desbloqueo con passphrase incorrecta (si se activa?)
    with pytest.raises(InvalidTag):
        unlock_keystore(ks2, "asd;lkfjh")


def test_keystore_tampered_ciphertext():
    """
    Prueba de detección de manipulación externa en el ciphertext del keystore
    """
    passphrase = "Hola456"
    path = Path("test_wallet.keystore.json")
    ks = create_keystore(passphrase)
    save_keystore(ks, path)
    data = json.loads(path.read_text(encoding="utf-8"))
    ct_bytes = base64.b64decode(data["ciphertext_b64"])
    # Se modifica un solo byte del cyphertext para ver si lo detecta
    tampered = bytes([ct_bytes[0] ^ 0x01]) + ct_bytes[1:]
    data["ciphertext_b64"] = base64.b64encode(tampered).decode("utf-8")
    
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    # Pytest espera que se lance un ValueError del checksum, en cuyo caso la prueba pasa
    with pytest.raises(ValueError, match="Checksum"):
        load_keystore(path)

def test_keystore_tampered_nonce():
    """
    Prueba de detección de manipulación externa en el nonce del keystore
    """
    passphrase = "Hola789"
    path = Path("test_wallet.keystore.json")
    ks = create_keystore(passphrase)
    save_keystore(ks, path)

    data = json.loads(path.read_text(encoding="utf-8"))
    nonce_bytes = base64.b64decode(data["cipher_params"]["nonce_b64"])
    # Ahora se modifica un byte en el nonce
    tampered_nonce = bytes([nonce_bytes[0] ^ 0xFF]) + nonce_bytes[1:]
    data["cipher_params"]["nonce_b64"] = base64.b64encode(tampered_nonce).decode("utf-8")

    path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    # Mismo caso, se espera ValueError por fallo en el Checksum
    with pytest.raises(ValueError, match="Checksum"):
        load_keystore(path)

def test_keystore_tampered_kdf_params():
    """
    Prueba de detección de manipulación externa en los parámetros KDF del keystore
    """
    passphrase = "Hola012"
    path = Path("test_wallet.keystore.json")
    ks = create_keystore(passphrase)
    save_keystore(ks, path)

    data = json.loads(path.read_text(encoding="utf-8"))
    data["kdf_params"]["t_cost"] = data["kdf_params"]["t_cost"] + 1
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    # Mismo caso, se espera ValueError cuando falle la comprobción del chaeksum
    with pytest.raises(ValueError, match="Checksum"):
        load_keystore(path)