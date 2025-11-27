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

OUTBOX_DIR = Path("outbox")
INBOX_DIR = Path("inbox")
VERIFIED_DIR = Path("verified")
DEFAULT_KEYSTORE = Path("wallet.keystore.json")


def ensure_dirs() -> None:
    for d in (OUTBOX_DIR, INBOX_DIR, VERIFIED_DIR):
        d.mkdir(parents=True, exist_ok=True)


def cmd_init(args: argparse.Namespace) -> None:
    ensure_dirs()
    pw1 = getpass.getpass("Nueva passphrase: ")
    pw2 = getpass.getpass("Repite passphrase: ")
    if pw1 != pw2:
        print("Las passphrases no coinciden. Abortando.")
        return

    ks = create_keystore(pw1)
    save_keystore(ks, DEFAULT_KEYSTORE)
    print(f"[+] Keystore creado en {DEFAULT_KEYSTORE}")


def cmd_address(args: argparse.Namespace) -> None:
    ks = load_keystore(DEFAULT_KEYSTORE)
    addr = ks.get("address")
    print("Address:", addr)


def cmd_sign(args: argparse.Namespace) -> None:
    ensure_dirs()

    ks = load_keystore(DEFAULT_KEYSTORE)
    from_addr = ks.get("address")

    tx = create_tx(
        from_addr=from_addr,
        to_addr=args.to,
        value=args.value,
        nonce=int(args.nonce),
        gas_limit=args.gas_limit,
        data_hex=args.data_hex,
    )

    passphrase = getpass.getpass("Passphrase: ")
    signed = sign_transaction(str(DEFAULT_KEYSTORE), passphrase, tx)

    out_path = OUTBOX_DIR / f"tx_{tx['nonce']}.json"
    out_path.write_text(json.dumps(signed, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[+] Transacción firmada guardada en {out_path}")


def cmd_recv(args: argparse.Namespace) -> None:
    ensure_dirs()

    in_path = Path(args.path)
    signed = json.loads(in_path.read_text(encoding="utf-8"))

    result = verify_signed_tx(signed)
    print("[*] Resultado de verificación:", result)

    if result["valid"]:
        out_path = VERIFIED_DIR / in_path.name
        out_path.write_text(json.dumps(signed, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"[+] Transacción válida almacenada en {out_path}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="wallet",
        description="Cold crypto wallet CLI (Proyecto 1)",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_init = sub.add_parser("init", help="Crear un nuevo keystore cifrado")
    p_init.set_defaults(func=cmd_init)

    p_addr = sub.add_parser("address", help="Mostrar la dirección de la billetera")
    p_addr.set_defaults(func=cmd_address)

    p_sign = sub.add_parser("sign", help="Firmar una nueva transacción (outbox/)")
    p_sign.add_argument("--to", required=True, help="Dirección destino")
    p_sign.add_argument("--value", required=True, help="Cantidad a transferir")
    p_sign.add_argument("--nonce", required=True, help="Nonce del remitente (uint64)")
    p_sign.add_argument("--gas_limit", type=int, default=None, help="Gas limit (opcional)")
    p_sign.add_argument("--data_hex", default=None, help="Payload hex opcional (0x...)")
    p_sign.set_defaults(func=cmd_sign)

    p_recv = sub.add_parser("recv", help="Verificar transacción firmada desde un archivo")
    p_recv.add_argument("--path", required=True, help="Ruta al JSON de transacción firmada")
    p_recv.set_defaults(func=cmd_recv)

    return parser


def main(argv: Optional[list[str]] = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
