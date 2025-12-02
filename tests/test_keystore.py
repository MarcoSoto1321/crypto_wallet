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

# - Caso donde todo funciona correctamente
def test_keystore_flow():
    # Una contraseña genérica y una ruta de prueba
    passphrase = "Hola123"
    path = Path("test_wallet.keystore.json")

    # Crea el keystore
    ks = create_keystore(passphrase)

    #Se asegura que estén los campos esperados en el keystore
    assert "ciphertext_b64" in ks
    assert "pubkey_b64" in ks

    # Guarda el keystore en disco
    save_keystore(ks, path)
    assert path.exists()

    # Carga el keystore desde disco
    ks2 = load_keystore(path)
    # Lo que carga debe ser idéntico a lo que se generó y guardó
    assert ks2["pubkey_b64"] == ks["pubkey_b64"]

    # Desbloquear la llave privada con la passphrase
    priv, pub, addr = unlock_keystore(ks2, passphrase)
    # Asegurarse de la longitud de la llave privada y que la pública no esté vacía
    assert len(priv) == 32
    assert len(pub) > 0
    # Que la dirección tenga el formato hexadecimal
    assert isinstance(addr, str) and addr.startswith("0x")

    # Intento de desbloquear con passphrase incorrecta
    with pytest.raises(InvalidTag):
        unlock_keystore(ks2, "asd;lkfjh")

# - Se altera el ciphertext
def test_keystore_tampered_ciphertext():
    passphrase = "Hola456"
    path = Path("test_wallet.keystore.json")

    ks = create_keystore(passphrase)
    save_keystore(ks, path)

    # Leer el JSON y alterar ciphertext_b64
    data = json.loads(path.read_text(encoding="utf-8"))
    ct_bytes = base64.b64decode(data["ciphertext_b64"])
    # flip de un bit en el primer byte
    tampered = bytes([ct_bytes[0] ^ 0x01]) + ct_bytes[1:]
    data["ciphertext_b64"] = base64.b64encode(tampered).decode("utf-8")

    # Guardar keystore cambiado
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    # Si el checksum funciona, de aquí no debe pasar
    ks_cambiado = load_keystore(path)

    # Lo mismo pero para intentar desbloquear el keystore
    with pytest.raises(InvalidTag):
        unlock_keystore(ks_cambiado, passphrase)

# - Se altera el nonce
def test_keystore_tampered_nonce():
    passphrase = "Hola789"
    path = Path("test_wallet.keystore.json")

    ks = create_keystore(passphrase)
    save_keystore(ks, path)

    data = json.loads(path.read_text(encoding="utf-8"))

    # Se cambia un byte del nonce
    nonce_bytes = base64.b64decode(data["cipher_params"]["nonce_b64"])
    tampered_nonce = bytes([nonce_bytes[0] ^ 0xFF]) + nonce_bytes[1:]
    data["cipher_params"]["nonce_b64"] = base64.b64encode(tampered_nonce).decode("utf-8")

    # Se guarda el nuevo archivo modificado
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    # Otra vez, el checksum debe impedir que se termine de cargar cuando no coincidan
    ks_corrupto = load_keystore(path)

    with pytest.raises(InvalidTag):
        unlock_keystore(ks_corrupto, passphrase)

# - Se alteran los parámetros del kdf
def test_keystore_tampered_kdf_params():
    passphrase = "Hola012"
    path = Path("test_wallet.keystore.json")

    ks = create_keystore(passphrase)
    save_keystore(ks, path)

    data = json.loads(path.read_text(encoding="utf-8"))

    # Se cambia t_cost
    data["kdf_params"]["t_cost"] = data["kdf_params"]["t_cost"] + 1

    path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    # Otra vez va a impedir que se cargue el archivo
    ks_corrupto = load_keystore(path)

    # Ahora que lo pienso, unlock_keystore no recibe los parámetros del archivo,
    # solo toma los globales de /app/crypto_utils
    # Nota a posteriori: lo mismo está en un comentario en unlock_keystore de /app/crypto_utils
    with pytest.raises(InvalidTag):
        unlock_keystore(ks_corrupto, passphrase)