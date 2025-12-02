# app/cli.py
import argparse
import getpass
import json
from pathlib import Path
from typing import Optional

from .keystore import create_keystore, save_keystore, load_keystore
from .tx_model import create_tx
from .signer import sign_transaction
from .verifier import verify_signed_tx

# Donde se guardan las transacciones firmadas 
OUTBOX_DIR = Path("outbox")
# Donde se reciben transacciones de otros usuarios
INBOX_DIR = Path("inbox")
# Donde se guardan las transacciones verificadas
VERIFIED_DIR = Path("verified")
# Donde se guarda keystore
DEFAULT_KEYSTORE = Path("wallet.keystore.json")


def ensure_dirs() -> None:
    '''
    Crea los directorios necesarios si no existen
    '''
    for d in (OUTBOX_DIR, INBOX_DIR, VERIFIED_DIR):
        d.mkdir(parents=True, exist_ok=True)


def cmd_init(args: argparse.Namespace) -> None:
    '''
    Inicialización de la billetera.
    Valida P
    '''
    # Creación de directorios necesarios
    ensure_dirs()
    # Pide passphrase dos veces
    pw1 = getpass.getpass("Nueva passphrase: ")
    pw2 = getpass.getpass("Repite passphrase: ")
    # Validamos que coincidan
    if pw1 != pw2:
        print("Las passphrases no coinciden. Abortando.")
        return
    # Genera keystore cifrado
    ks = create_keystore(pw1)
    # Guarda keystore en Json
    save_keystore(ks, DEFAULT_KEYSTORE)
    print(f"[+] Keystore creado en {DEFAULT_KEYSTORE}")


def cmd_address(args: argparse.Namespace) -> None:
    '''
    Muestra la dirección de la cartera
    '''
    # Obtiene keystore y lo verifica
    ks = load_keystore(DEFAULT_KEYSTORE)
    addr = ks.get("address")
    print("Address:", addr)


def cmd_sign(args: argparse.Namespace) -> None:
    '''
    Firma una nueva transacción
    
    Parámetros que acepta:
        --to: Dirección destino
        --value: Cantidad a transferir
        --nonce: Número secuencial
        --gas_limit: Límite de gas
        --data_hex: Datos extra
    '''
    # Creación de directorios necesarios
    ensure_dirs()
    # Carga keystores guardados
    ks = load_keystore(DEFAULT_KEYSTORE)
    from_addr = ks.get("address")
    # Construye directorio de transacción
    tx = create_tx(
        from_addr=from_addr,
        to_addr=args.to,
        value=args.value,
        nonce=int(args.nonce),
        gas_limit=args.gas_limit,
        data_hex=args.data_hex,
    )
    # Pedimos passphrase
    passphrase = getpass.getpass("Passphrase: ")
    # Firmamos con la llave privada guardado en el keystore
    signed = sign_transaction(str(DEFAULT_KEYSTORE), passphrase, tx)

    # Guardamos resultado
    out_path = OUTBOX_DIR / f"tx_{tx['nonce']}.json"
    out_path.write_text(json.dumps(signed, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[+] Transacción firmada guardada en {out_path}")


def cmd_recv(args: argparse.Namespace) -> None:
    '''
    Verificar transacciones
    '''
    ensure_dirs()

    in_path = Path(args.path)
    # Obtiene transacción firmada
    signed = json.loads(in_path.read_text(encoding="utf-8"))

    # Verifica firma
    result = verify_signed_tx(signed)
    print("[*] Resultado de verificación:", result)

    # Si es valida, la mueve a "verified"
    if result["valid"]:
        out_path = VERIFIED_DIR / in_path.name
        out_path.write_text(json.dumps(signed, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"[+] Transacción válida almacenada en {out_path}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="wallet",
        description="Cold crypto wallet CLI (Proyecto 1)",
    )
    '''
    Estructura de los comandos
    '''
    # Creación de subcomandos
    sub = parser.add_subparsers(dest="command", required=True)

    # Llama a la función "cmd_init()" con el comando "init"
    p_init = sub.add_parser("init", help="Crear un nuevo keystore cifrado")
    p_init.set_defaults(func=cmd_init)

    # Llama a la función "cmd_init()" con el comando "init"
    p_addr = sub.add_parser("address", help="Mostrar la dirección de la billetera")
    p_addr.set_defaults(func=cmd_address)

    # Llama a la función "cmd_init()" con el comando "init" y le agrega los argumentos validos
    p_sign = sub.add_parser("sign", help="Firmar una nueva transacción (outbox/)")
    p_sign.add_argument("--to", required=True, help="Dirección destino")
    p_sign.add_argument("--value", required=True, help="Cantidad a transferir")
    p_sign.add_argument("--nonce", required=True, help="Nonce del remitente (uint64)")
    p_sign.add_argument("--gas_limit", type=int, default=None, help="Gas limit (opcional)")
    p_sign.add_argument("--data_hex", default=None, help="Payload hex opcional (0x...)")
    p_sign.set_defaults(func=cmd_sign)

    # Llama a la función "cmd_init()" con el comando "init" y le agrega su argumento necesario
    p_recv = sub.add_parser("recv", help="Verificar transacción firmada desde un archivo")
    p_recv.add_argument("--path", required=True, help="Ruta al JSON de transacción firmada")
    p_recv.set_defaults(func=cmd_recv)

    return parser


def main(argv: Optional[list[str]] = None) -> None:
    '''
    Función principal 
    '''

    # Generamos parser, y parseamos los argumentos de la linea de comandos
    parser = build_parser()
    args = parser.parse_args(argv)
    # Ejecutamos la función asociada
    args.func(args)


if __name__ == "__main__":
    main()
