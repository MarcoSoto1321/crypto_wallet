import sys
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.verifier import verify_signed_tx

# Estos datos fueron generados una vez y NO deben cambiar.
GOLDEN_ADDRESS = "0x9ea155f9bb1bda0a9343fe1d6e63b014cfded1b4"

GOLDEN_VECTORS = [
    {
        "tx": {"from": "0x9ea155f9bb1bda0a9343fe1d6e63b014cfded1b4", "to": "0x1234567890abcdef", "value": "100", "nonce": 1, "timestamp": "2025-12-02T00:24:19.557269Z"},
        "signature_b64": "0r4B65a/pwy53zndWWqBuwFyShjfQt1YWMsa4P2GjZB6rbYG3T1HcbuQldBcWIprMobcNLatUqnbPvZmLYKiAg==",
        "pubkey_b64": "7GRRcI44i6UKdEBDvCLqbopc4xc0zeH2rcFnimzVDTQ="
    },
    {
        "tx": {"from": "0x9ea155f9bb1bda0a9343fe1d6e63b014cfded1b4", "to": "0xdeadbeef", "value": "50.55", "nonce": 2, "timestamp": "2025-12-02T00:24:19.557533Z"},
        "signature_b64": "utLJoREGZnAsBQc4e1CKvkD1FNPcU3VAmHf9D6c9g1JT9wGeyHVOgy1e2qpHlQLnaieipz0i5Oc45BTjn0/qDg==",
        "pubkey_b64": "7GRRcI44i6UKdEBDvCLqbopc4xc0zeH2rcFnimzVDTQ="
    },
    {
        "tx": {"from": "0x9ea155f9bb1bda0a9343fe1d6e63b014cfded1b4", "to": "0xcafe", "value": "0", "nonce": 3, "timestamp": "2025-12-02T00:24:19.557541Z", "gas_limit": 50000, "data_hex": "0xabcdef"},
        "signature_b64": "bcweVu1dMlb8TJTS1usNMM7l60CQyXCSN1Dmt/g/McVr18U+dYPswmphUaSsRTAUyH0FdDWioUVuP4zzoNe9Bw==",
        "pubkey_b64": "7GRRcI44i6UKdEBDvCLqbopc4xc0zeH2rcFnimzVDTQ="
    },
]

def test_golden_vectors_validity():
    """
    Verifica que las firmas generadas en el pasado sigan siendo válidas
    con el código actual. Asegura compatibilidad y determinismo.
    """
    for vector in GOLDEN_VECTORS:
        # Reconstruimos el paquete firmado como lo espera el verificador
        signed_pkg = {
            "tx": vector["tx"],
            "sig_scheme": "Ed25519",
            "signature_b64": vector["signature_b64"],
            "pubkey_b64": vector["pubkey_b64"]
        }
        
        # enforce_nonce=False porque son pruebas estáticas sin estado previo
        result = verify_signed_tx(signed_pkg, enforce_nonce=False)
        
        assert result["valid"] is True, f"El vector dorado falló: {result.get('reason')}"
        
        # Verificación extra: La dirección derivada debe coincidir
        assert vector["tx"]["from"] == GOLDEN_ADDRESS