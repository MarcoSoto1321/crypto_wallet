# tests/test_transaction.py
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.transaction import create_transaction, validate_transaction, transaction_to_json, json_to_transaction, json_to_file, file_to_json
from app.keystore import create_keystore, save_keystore, load_keystore, unlock_keystore
from app.signer import sign_transaction
from app.canonicalizer import canonical_bytes

# Crea una transacción mínima y revisa que tenga los campos obligatorios y tipos correctos
def test_transaction_minimal():

    transaction = create_transaction(
        # Lo rellena el signer
        from_address="",
        to_address="0x123456",
        value="100",
        nonce=0
    )

    # Campos obligatorios
    assert "from" in transaction
    assert "to" in transaction
    assert "value" in transaction
    assert "nonce" in transaction
    assert "timestamp" in transaction

    # Tipos básicos
    assert isinstance(transaction["from"], str)
    assert isinstance(transaction["to"], str)
    assert isinstance(transaction["value"], str)
    assert isinstance(transaction["nonce"], int)
    assert isinstance(transaction["timestamp"], str)

    assert transaction["from"] == ""

# Crea una transacción con gas_limit y data_hex para probar que se agregan correctamente
def test_create_transaction_optionals():
    transaction = create_transaction(
        from_address="0xabc123",
        to_address="0xdef456",
        value=42.5,
        nonce=1,
        gas_limit=20000,
        data="0xCAFECAFE",
    )

    assert transaction["from"] == "0xabc123"
    assert transaction["to"] == "0xdef456"
    # value debe haber quedado como string
    assert isinstance(transaction["value"], str)
    assert transaction["value"] == "42.5"

    assert transaction["nonce"] == 1
    assert transaction["gas_limit"] == 20000
    assert transaction["data_hex"] == "0xCAFECAFE"

# Si el nonce es negativo, debe lanzar ValueError al crear la transacción
def test_transaction_invalid_nonce():
    # Las pruebas que implementen pytest.raises aparecerán como PASSED si se lanzó la excepción que se espera (ValueError)
    with pytest.raises(ValueError, match="nonce") as err:
        create_transaction(
            # Es lo mismo None a un string vacío para create_transaction ?
            from_address=None,
            to_address="0xaaaaaaaa",
            value="1",
            nonce=-1
        )
    #print (err.value)

# Si gas_limit es negativo, también debe lanzar ValueError
def test_transaction_invalid_gas():
    with pytest.raises(ValueError, match="gas_limit"):
        create_transaction(
            from_address=None,
            to_address="0xabc",
            value="1",
            nonce=0,
            gas_limit=-10
        )

# Una transacción correcta
def test_validate_transaction():
    transaction = create_transaction(
        from_address="0xabc123",
        to_address="0xdef456",
        value="10",
        nonce=5,
        gas_limit=65535,
        data="0x00"
    )

    # No debe lanzar excepción
    validate_transaction(transaction)

# Sin algún campo obligatorio debe lanzar ValueError
def test_transaction_missing_field():
    transaction = {
        "from": "0xabc",

        "value": "10",
        "nonce": 0,
        "timestamp": "2025-01-01T00:00:00.000000Z"
    }
    with pytest.raises(ValueError, match="to"):
        validate_transaction(transaction)

# Con tipos de datos erróneos
def test_transaction_wrong_types():
    transaction = {
        "from": "0xabc",
        "to": "0xdef",
        "value": 10, #value como entero
        "nonce": 0,
        "timestamp": "2025-01-01T00:00:00.000000Z"
    }
    with pytest.raises(ValueError, match="value"):
        validate_transaction(transaction)

#  transaction_to_json + json_to_transaction son inversos razonables
def test_transaction_json():
    transaction_original = create_transaction(
        from_address="0xabc",
        to_address="0xdef",
        value="123",
        nonce=7
    )

    raw = transaction_to_json(transaction_original)
    # validate_transaction siempre se llama al convertir el json a transacción
    transaction_loaded = json_to_transaction(raw)

    assert transaction_loaded == transaction_original

# Guarda una transacción en archivo y luego la carga
def test_transaction_file(tmp_path: Path):
    transaction_original = create_transaction(
        from_address="0xabc",
        to_address="0xdef",
        value="999",
        nonce=3
    )

    file_path = tmp_path / "transaction.json"

    json_to_file(transaction_original, str(file_path))
    raw = file_to_json(str(file_path))
    transaction_loaded = json_to_transaction(raw)

    assert transaction_loaded == transaction_original

# Prueba el firmado de signer.py para una transacción con "from" vacío,
# la prueba más completa hasta ahora
def test_sign_transaction():
    with TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        # Crea el keystore
        keystore_path = tmpdir / "wallet.keystore.json"
        passphrase = "test-passphrase"

        ks = create_keystore(passphrase)
        save_keystore(ks, keystore_path)

        loaded_ks = load_keystore(keystore_path)
        priv, pub, addr = unlock_keystore(loaded_ks, passphrase)
        assert isinstance(priv, (bytes, bytearray))
        assert isinstance(pub, (bytes, bytearray))
        assert isinstance(addr, str)

        # Crear transacción sin 'from' (en el flujo del programa, el usuario hace una transacción)
        transaction = create_transaction(
            from_address=None,
            to_address="0xabababab",
            value="50",
            nonce=0
        )

        # Valida la transacción antes de firmar
        validate_transaction(transaction)

        # Firma
        signed = sign_transaction(str(keystore_path), passphrase, transaction)

        assert "tx" in signed
        assert "sig_scheme" in signed
        assert "signature_b64" in signed
        assert "pubkey_b64" in signed
        assert signed["sig_scheme"] == "Ed25519"

        # from coincide con la address del keystore ?
        transaction_signed = signed["tx"]
        assert transaction_signed["from"] == addr

        # canonical_bytes funciona sobre la transaction final ?
        cb = canonical_bytes(transaction_signed)
        assert isinstance(cb, (bytes, bytearray))
        assert len(cb) > 0
