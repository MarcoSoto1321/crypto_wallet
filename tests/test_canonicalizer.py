# tests/test_canonicalizer.py
import sys
from pathlib import Path

# Agregar raíz del proyecto al path para poder importar app/
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.canonicalizer import canonical_json, canonical_bytes

def test_canonical_json_sorting():
    """
    Prueba que canonical_json ordena las llaves del diccionario
    """
    # canonical_json debe ordenar las llaves siempre de la misma manera
    data = {"b": 2, "a": 1}
    cj = canonical_json(data)
    assert cj == '{"a":1,"b":2}'

def test_canonical_bytes():
    """
    Prueba que canonical_bytes codifica el JSON canónico a UTF-8
    """
    # canonical_bytes debe ser igual al JSON canónico codificado en UTF-8
    data = {"z": 3}
    cb = canonical_bytes(data)
    assert cb == canonical_json(data).encode("utf-8")

def test_canonical_json_no_spaces():
    """
    Prueba que canonical_json elimina espacios innecesarios
    """
    # El JSON canónico no debe contener espacios
    data = {"x": 1, "a": 2}
    assert " " not in canonical_json(data)

def test_canonical_json_utf8():
    """
    Prueba que canonical_json maneja correctamente caracteres UTF-8
    """
    # Comprobar que caracteres UTF-8 no se escapan
    data = {"ñ": "á"}
    assert canonical_json(data) == '{"ñ":"á"}'
