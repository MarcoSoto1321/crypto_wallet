# Proyecto 1: Billetera Fría de Criptomonedas (Crypto 2026-1)

[cite_start]Este proyecto es una implementación de una billetera de criptomonedas fría (offline) para un sistema basado en cuentas, como se especifica en el documento del proyecto[cite: 1].

## Pila Tecnológica

- **Lenguaje:** [Python/TypeScript/Go/Rust]
- [cite_start]**Esquema de Firma:** Ed25519 [cite: 12, 162]
- [cite_start]**KDF (Almacén):** Argon2id
- [cite_start]**Cifrado (Almacén):** AES-256-GCM [cite: 16]
- [cite_start]**Formato de Dirección:** KECCAK-256(pubkey) [12..] (Estilo Ethereum) [cite: 18]

## Estructura del Repositorio

```
/mi-crypto-wallet/
|
├── /app/             # Código fuente
├── /tests/           # Pruebas unitarias y vectores "golden"
├── /docs/            # Documento técnico y borradores
├── /inbox/           # Simulación de transacciones recibidas
├── /outbox/          # Transacciones firmadas listas para "enviar"
├── /verified/        # Transacciones verificadas y válidas
|
├── README.md         # Esto
└── requirements.txt  # Dependencias
```

## Cómo Construir y Ejecutar

[cite_start][cite: 104]

**1. Instalar Dependencias**

```bash
# Para Python
pip install -r requirements.txt
```

**2. Ejecutar la Aplicación (CLI)**

[cite_start][cite: 81, 94]

```bash
# (Ejemplo de cómo será)
# Crear una nueva billetera
python -m app.cli init

# Ver tu dirección
python -m app.cli address

# Firmar una transacción
python -m app.cli sign --to "0x..." --value 100 --nonce 0

# Verificar una transacción recibida
python -m app.cli recv --path ./inbox/tx_a_verificar.json
```

## Modelo de Amenazas y Limitaciones

- [cite_start]**Modelo de Amenazas (En Alcance):**
  - Robo del archivo `.keystore.json` (Mitigado por KDF fuerte y cifrado).
  - Manipulación de transacciones (Mitigado por firma criptográfica).
  - [cite_start]Ataques de Replay (Mitigado por rastreo de nonce)[cite: 61].
- [cite_start]**Limitaciones (Fuera de Alcance):** [cite: 107, 115]
  - Este proyecto no se conecta a ninguna red blockchain real.
  - No maneja estado de cuenta (balances).
  - No usa semillas mnemónicas (BIP-39) para la versión base.

## Pruebas

[cite_start][cite: 79]

Para ejecutar las pruebas:

```bash
# (Ejemplo)
pytest
```
