#/app/crypto_utils.py 
import os
import hashlib
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from argon2 import PasswordHasher
from argon2.low_level import hash_secret_raw, Type as ArgonType
import base64
from cryptography.exceptions import InvalidTag

# --- Constantes de Seguridad ---
# Parámetros para Argon2id, como sugiere el documento 
# Ajusta 'm_cost' (memoria) y 't_cost' (tiempo) según tu máquina.
ARGON_TIME_COST = 3
ARGON_MEM_COST_KIB = 65536  # 64 MiB
ARGON_PARALLELISM = 4
ARGON_KEY_LEN_BYTES = 32  # Para AES-256, necesitamos una clave de 32 bytes
ARGON_SALT_LEN_BYTES = 16
AES_NONCE_LEN_BYTES = 12  # Estándar para GCM

# --- Funciones Criptográficas ---

def generate_ed25519_keys():
    """
    Genera un nuevo par de claves Ed25519.
    Retorna (private_key_bytes, public_key_bytes)
    """
    private_key = ed25519.Ed25519PrivateKey.generate()
    public_key = private_key.public_key()
    
    # Obtenemos los bytes crudos de las claves
    private_key_bytes = private_key.private_bytes_raw()
    public_key_bytes = public_key.public_bytes_raw()
    
    return private_key_bytes, public_key_bytes

def derive_aes_key(passphrase: str, salt: bytes) -> bytes:
    """
    Deriva una clave AES de 32 bytes desde una contraseña y un salt
    usando Argon2id.
    """
    passphrase_bytes = passphrase.encode('utf-8')
    
    key = hash_secret_raw(
        secret=passphrase_bytes,
        salt=salt,
        time_cost=ARGON_TIME_COST,
        memory_cost=ARGON_MEM_COST_KIB,
        parallelism=ARGON_PARALLELISM,
        hash_len=ARGON_KEY_LEN_BYTES,
        type=ArgonType.ID  # Asegura que usamos Argon2id
    )
    return key

def encrypt_data(data: bytes, key: bytes) -> tuple[bytes, bytes, bytes]:
    """
    Cifra datos usando AES-256-GCM con una clave dada.
    Retorna (ciphertext, nonce, tag)
    """
    aesgcm = AESGCM(key)
    nonce = os.urandom(AES_NONCE_LEN_BYTES)
    
    # Ciframos. El resultado incluye el tag de autenticación al final.
    ciphertext_with_tag = aesgcm.encrypt(nonce, data, None)
    
    # Debemos separar el ciphertext del tag [cite: 27, 28]
    # El tag en AES-GCM es siempre de 16 bytes
    tag_len = 16
    ciphertext = ciphertext_with_tag[:-tag_len]
    tag = ciphertext_with_tag[-tag_len:]
    
    return ciphertext, nonce, tag

def decrypt_data(ciphertext: bytes, tag: bytes, nonce: bytes, key: bytes) -> bytes:
    """
    Descifra datos de AES-256-GCM.
    Lanzará una excepción (InvalidTag) si la clave, nonce, tag o
    ciphertext son incorrectos.
    """
    aesgcm = AESGCM(key)
    
    # Juntamos el ciphertext y el tag para la verificación
    ciphertext_with_tag = ciphertext + tag
    
    plaintext = aesgcm.decrypt(nonce, ciphertext_with_tag, None)
    return plaintext

def derive_address_btc_style(public_key_bytes: bytes) -> str:
    """
    Deriva una dirección estilo Bitcoin (SHA-256 -> RIPEMD-160)
    [cite: 18, 19]. Usamos esto porque 'hashlib' lo soporta nativamente.
    
    Retorna un string hexadecimal.
    """
    # 1. SHA-256 de la clave pública
    sha256_hash = hashlib.sha256(public_key_bytes).digest()
    
    # 2. RIPEMD-160 del hash anterior
    # 'new' es necesario para ripemd160 en hashlib
    ripemd160_hasher = hashlib.new('ripemd160')
    ripemd160_hasher.update(sha256_hash)
    address_bytes = ripemd160_hasher.digest()
    
    # 3. Convertir a string hexadecimal
    # Agregamos un prefijo '0x' por convención
    return "0x" + address_bytes.hex()