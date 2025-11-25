# app/transaction.py
import json
from datetime import datetime, timezone
from typing import Any, Dict, Optional

def time_iso8601() -> str:
    '''
    Genera un timestamp con formato ISO 8601 (YYYY-MM-DD HH:MinMin:SS.mSmSmS)
    '''
    #La Z del final significa que está en UTC
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")

def create_transaction(
    from_address: Optional[str], #Puede ir vacío porque se puede llenar en el signer con la keystore
    to_address: [str],
    value: int | float | str,
    nonce: int,
    gas_limit: Optional[int] = None,
    data: Optional[str] = None
    ) -> Dict[str, Any]:
    '''
    Crea una transacción, sin guardarla en disco
    - Información mínima que recibe: Destinatario, valor númerico o string y nonce
    - Información opcional que recibe: Remitente, límite de gas, info de la transacción en Hex
    - Convierte value en string
    - Añade timestamp en formado ISO 8601
    '''

    # Convierte int o float a string
    if isinstance(value, (int, float)):
        value = str(value)
    
    #Por si hay valores no válidos de nonce y gas
    if nonce < 0:
        raise ValueError("El nonce no puede ser menor a 0")
    if gas_limit is not None and gas_limit < 0:
        raise ValueError("Si hay gas_limit este debe ser >= 0")

    # Construcción del diccionario
    transaction: Dict[str, Any] = {
        #O le pasa lo que recibe o pone emisor vacío
        "from": from_address or "",
        "to": to_address,
        "value": value,
        "nonce": nonce,
        "timestamp": time_iso8601()
    }

    # Simplemente pasa el gas y los datos
    if gas_limit is not None:
        transaction["gas_limit"] = gas_limit
    
    if data is not None:
        transaction["data_hex"] = data

    return transaction


def validate_transaction(transaction: Dict[str, Any]) -> None
    '''
    Verifica que el diccionario cargado tenga los campos correctos
    - Arroja ValueError si falta un campo obligarotio o si es incorrecto, incluyendo campos opcionales 
    '''
    # Primero verifica los campos obligatorios
    # No se si data_hex puede contener cualquier cosa, así que no lo incluyo
    must_have = ["from","to","value","nonce","timestamp"]
    for field in must_have:
        if field not in transaction:
            raise ValueError(f"Transacción inválida, falta el campo '{field}'")

    # Verifica el tipo de dato de los campos
    if not isinstance(transaction["from"], str):
        raise ValueError("Tipo de dato de 'from' incorrecto, se esperaba un string")

    if not isinstance(transaction["to"], str):
        raise ValueError("Tipo de dato de 'to' incorrecto, se esperaba un string")

    if not isinstance(transaction["value"], str):
        raise ValueError("Tipo de dato de 'value' incorrecto, se esperaba un string")

    if not isinstance(transaction["nonce"], int) or transaction["nonce"] < 0:
        raise ValueError("Valor de 'nonce' inválido o tipo de dato incorrecto, se esperaba un entero >= 0")

    if "gas_limit" in transaction:
        if not isinstance(transaction["gas_limit"], int) or transaction["gas_limit"] < 0:
            raise ValueError("Valor de  'gas_limit' inválido o tipo de dato incorrecto, se esperaba un entero >= 0")

    if "data_hex" in transaction:
        if not isinstance(transaction["data_hex"], str):
            raise ValueError("Valor de 'data_hex' incorrecto, se esperaba un string")

    #Cómo comprobar que esté en ISO 8601?
    if not isinstance(transaction["timestamp"], str):
        raise ValueError("Formato de 'timestamp' incorrecto, se espera un string")


# Aparentemente, es una buena práctica separar la serialización de la lógica del sistema de archivos
# (https://en.wikipedia.org/wiki/Single-responsibility_principle)
def transaction_to_json(transaction: Dict[str, Any]) -> str:
    """
    Guarda una transacción en JSON no canónico.
    - No escribe en disco, devuelve el string JSON a json_to_file
    """
    return json.dumps(transaction, indent=2)

def json_to_file(transaction: Dict[str, Any], filepath: str) -> None:
    '''
    Guarda en disco un JSON no canónico
    - No convierte la transacción a JSON, se la pasa a transaction_to_json
    '''
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(transaction_to_json(transaction))


# Lo mismo para cargar el JSON, una función carga el archivo y otra la convierte a transacción
def file_to_json(filepath: str) -> str:
    '''
    Carga un archivo JSON no canónico desde disco
    - No convierte el JSON en transacción, hay que pasárselo a json_to_transaction
    '''
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()

def json_to_transaction(json_str: str) -> Dict[str, Any]:
    '''
    Carga un JSON no canónico y lo convierte en transacción
    - No lee desde disco, recibe el JSON de file_to_json
    - Antes de devolver la transacción, la valida con validate_transaction
    '''
    transaction = json.loads(json_str)
    validate_transaction(transaction)
    return transaction

