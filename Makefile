# Makefile con Autogestión de Entorno Virtual

# Configuración del entorno
# Detectar Windows o Linux/macOS
ifeq ($(OS),Windows_NT)
    VENV := venv
    PYTHON := $(VENV)/Scripts/python.exe
else
    VENV := venv
    PYTHON := $(VENV)/bin/python
endif

PIP := $(PYTHON) -m pip
VENV_SENTINEL := $(VENV)/.venv_created

.PHONY: all install test clean init address run help

# Comando por defecto
help:
	@echo "----------------------------------------------------------------"
	@echo "                 CRYPTO WALLET CLI - AUTOMÁTICO                 "
	@echo "----------------------------------------------------------------"
	@echo "  make install   -> Crea el entorno virtual e instala dependencias"
	@echo "  make test      -> Corre los tests usando el entorno aislado"
	@echo "  make init      -> Inicializa la wallet"
	@echo "  make address   -> Muestra tu dirección"
	@echo "  make run args=\"...\" -> Ejecuta comandos con argumentos"
	@echo "  make clean     -> Borra el entorno virtual y temporales"
	@echo "----------------------------------------------------------------"

# Regla inteligente: Si la carpeta venv no existe, la crea.
# Si requirements.txt cambia, actualiza las librerías.

$(VENV_SENTINEL): requirements.txt
	python3 -m venv $(VENV)
	$(PYTHON) -m pip install --upgrade pip
	$(PIP) install -r requirements.txt
	@echo "ok" > $(VENV_SENTINEL)

# 'install' es un alias para asegurar que el venv esté listo
install: $(VENV_SENTINEL)

# Todos los comandos dependen de 'install', así que si el venv no existe,
# se crea solo antes de ejecutar el comando.
test: install
	$(PYTHON) -m pytest

init: install
	$(PYTHON) -m app.cli init

address: install
	$(PYTHON) -m app.cli address

run: install
	$(PYTHON) -m app.cli $(args)

clean:
ifeq ($(OS),Windows_NT)
	if exist venv rmdir /S /Q venv
	if exist __pycache__ rmdir /S /Q __pycache__
	if exist app\__pycache__ rmdir /S /Q app\__pycache__
	if exist tests\__pycache__ rmdir /S /Q tests\__pycache__
	if exist .pytest_cache rmdir /S /Q .pytest_cache
else
	rm -rf venv __pycache__ app/__pycache__ tests/__pycache__ .pytest_cache
endif
	@echo "[✓] Entorno limpiado correctamente"