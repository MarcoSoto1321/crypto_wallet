# app/tx_model.py
from typing import Optional, Dict, Any, Union
import datetime


def create_tx(
    from_addr: str,
    to_addr: str,
    value: Union[int, str],
    nonce: int,
    gas_limit: Optional[int] = None,
    data_hex: Optional[str] = None,
    timestamp: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Crea un diccionario de transacción con los campos mínimos requeridos.

    - value se guarda como string para evitar broncas con floats.
    - nonce y gas_limit se fuerzan a int.
    - timestamp es ISO8601 (UTC) si no se proporciona.
    """
    if timestamp is None:
        timestamp = datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

    tx: Dict[str, Any] = {
        "from": from_addr,
        "to": to_addr,
        "value": str(value),
        "nonce": int(nonce),
        "timestamp": timestamp,
    }
    if gas_limit is not None:
        tx["gas_limit"] = int(gas_limit)
    if data_hex is not None:
        tx["data_hex"] = data_hex

    return tx
