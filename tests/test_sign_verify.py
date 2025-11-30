# tests/test_sign_verify.py
import sys
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.keystore import create_keystore, save_keystore  # noqa: E402
from app.tx_model import create_tx  # noqa: E402
from app.signer import sign_transaction  # noqa: E402
from app.verifier import verify_signed_tx  # noqa: E402


def test_sign_and_verify_ok(tmp_path: Path):
    ks_path = tmp_path / "wallet.keystore.json"
    nonce_state_path = tmp_path / "nonce_state.json"

    ks = create_keystore("pass123")
    save_keystore(ks, ks_path)

    addr = ks["address"]
    tx = create_tx(from_addr=addr, to_addr="0xdeadbeef", value=10, nonce=1)

    signed = sign_transaction(str(ks_path), "pass123", tx)
    result = verify_signed_tx(signed, nonce_state_path=str(nonce_state_path))
    assert result["valid"]

def test_replay_nonce_rejected(tmp_path: Path):
    ks_path = tmp_path / "wallet.keystore.json"
    nonce_state_path = tmp_path / "nonce_state.json"

    ks = create_keystore("pass123")
    save_keystore(ks, ks_path)
    addr = ks["address"]
    tx = create_tx(from_addr=addr, to_addr="0xdeadbeef", value=10, nonce=5)

    signed = sign_transaction(str(ks_path), "pass123", tx)

    r1 = verify_signed_tx(signed, nonce_state_path=str(nonce_state_path))
    assert r1["valid"]

    # Reusar el mismo paquete → debe ser nonce obsoleto
    r2 = verify_signed_tx(signed, nonce_state_path=str(nonce_state_path))
    assert not r2["valid"]
    assert "stale nonce" in r2["reason"]

def test_address_mismatch_detected(tmp_path: Path):
    ks_path = tmp_path / "wallet.keystore.json"
    nonce_state_path = tmp_path / "nonce_state.json"

    ks = create_keystore("pass123")
    save_keystore(ks, ks_path)
    addr = ks["address"]
    tx = create_tx(from_addr=addr, to_addr="0xdeadbeef", value=10, nonce=1)

    signed = sign_transaction(str(ks_path), "pass123", tx)

    # Alterar la address en el campo "from"
    signed_tampered = json.loads(json.dumps(signed))
    signed_tampered["tx"]["from"] = "0x0000000000000000000000000000000000000000"

    r = verify_signed_tx(signed_tampered, nonce_state_path=str(nonce_state_path))
    assert not r["valid"]
    assert "address mismatch" in r["reason"]