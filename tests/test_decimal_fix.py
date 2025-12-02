import sys
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.signer import validate_tx

def test_validate_tx_accepts_decimals():
    """Prueba que validate_tx acepte strings con punto decimal."""
    # Este es el caso que fallaba antes y ahora debe pasar
    tx = {
        "to": "0x123", "value": "10.5", "nonce": 1, "timestamp": "2025-01-01T00:00:00Z"
    }
    validate_tx(tx)

def test_validate_tx_accepts_integers_as_string():
    """Regresión: Asegurar que no rompimos los enteros como string."""
    tx = {
        "to": "0x123", "value": "100", "nonce": 1, "timestamp": "2025-01-01T00:00:00Z"
    }
    validate_tx(tx)

def test_validate_tx_rejects_invalid_numbers():
    """Asegurar que sigamos rechazando basura."""
    tx = {
        "to": "0x123", "value": "diez", "nonce": 1, "timestamp": "2025-01-01T00:00:00Z"
    }
    with pytest.raises(ValueError):
        validate_tx(tx)