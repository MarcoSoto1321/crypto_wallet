# Proyecto 1: Billetera Fría de Criptomonedas (Crypto 2026-1)

El proyecto consiste en la creación de una billetera fría (offline) para un sistema de cuentas, implementada desde cero en Python y fundamentada en el uso de primitivas y procedimientos criptográficos estandarizados.

## Objetivo del Proyecto
Desarrollar una billetera fría funcional que permita generar claves, almacenar de forma segura la clave privada, firmar transacciones, verificar firmas recibidas y simular el flujo básico de envío/recepción sin depender de frameworks externos ni de una red real.

## Pila Tecnológica

- **Lenguaje:** Python 3.10+
- **Esquema de Firma:** Ed25519 (RFC 8032)
- **KDF (Derivación de Clave):** Argon2id
- **Cifrado (Almacén):** AES-256-GCM
- **Formato de Dirección:** SHA-256 -> RIPEMD-160 (Estilo Bitcoin)

## Estructura del Repositorio

```text
/crypto_wallet/
|
├── /app/             # Código fuente (Lógica Core)
├── /tests/           # Pruebas unitarias y vectores dorados
├── /inbox/           # Simulación de transacciones recibidas
├── /outbox/          # Transacciones firmadas listas para "enviar"
├── /verified/        # Transacciones verificadas y válidas
|
├── Makefile          # Automatización de comandos
├── README.md         # Documentación
└── requirements.txt  # Dependencias
```

## Cómo Construir y Ejecutar

Este proyecto utiliza Makefile para gestionar el entorno virtual y la ejecución automáticamente. No es necesario instalar librerías manualmente.

Requiere la instalación previa de Makefile en Windows.

### 1. Instalación Automática

El siguiente comando crea el entorno virtual (venv) e instala las dependencias:

```bash
make install
```

### 2. Uso de la Billetera (CLI)

#### A. Inicializar una nueva billetera

Crea un keystore cifrado (wallet.keystore.json).

```bash
make init
```

(Nota: El sistema advertirá si la passphrase es insegura/corta)

#### B. Ver tu dirección y clave pública

```bash
make address
```

#### C. Firmar una transacción (Enviar)

Crea un archivo firmado en la carpeta /outbox. Usa make run args="..." para pasar los parámetros.

```bash
make run args="sign --to 0xDestinoEjemplo --value 50.5 --nonce 1"
```

#### D. Recibir y Verificar una transacción

Lee un archivo JSON desde /inbox, verifica su firma y si es válido lo mueve a /verified.

Primero, simula la recepción copiando un archivo:

```bash
cp outbox/tx_1.json inbox/transaccion.json
```

Luego, ejecuta el verificador:

```bash
make run args="recv --path inbox/transaccion.json"
```

## Pruebas y Vectores Dorados

El proyecto incluye una suite de pruebas completa que cubre:

1. **Tests Unitarios:** Keygen, cifrado/descifrado, firmado y canonicalización.
2. **Vectores Dorados (Golden Vectors):** Pruebas con datos estáticos pre-calculados (tests/test_golden.py) para garantizar que la lógica de firma sea determinista y compatible con versiones futuras.

Para ejecutar todas las pruebas automáticamente:

```bash
make test
```

## Modelo de Amenazas y Limitaciones

### Modelo de Amenazas (En Alcance)

- **Robo de keystore:** Mitigado por cifrado AES-256-GCM y KDF Argon2id (resistente a fuerza bruta GPU).
- **Manipulación de tx:** Mitigado por firmas Ed25519 sobre JSON canónico.
- **Manipulación de Keystore:** Mitigado por Checksum con SHA-256.
- **Replay Attacks:** El verificador mantiene un estado local de nonces (nonce_state.json) para rechazar transacciones antiguas.

### Limitaciones (Fuera de Alcance)

- No hay conexión a red real (todo es simulación local de archivos).
- No maneja balances (no verifica si tienes fondos, solo si la firma es válida).
- El keystore no usa semillas mnemónicas (BIP-39).
- No hay medidas contra ataques de side-channel o en caso de que la máquina tenga malware
### Conclusión
El proyecto permitió implementar desde cero una billetera fría completa, integrando canonicalización, firmado seguro, verificación de transacciones y manejo de claves cifradas. La estructura reproducible con Makefile, junto con pruebas unitarias y vectores dorados, garantiza que el sistema sea consistente, verificable y fácilmente extensible.
