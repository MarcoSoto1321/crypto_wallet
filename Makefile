# Makefile con Autogestión de Entorno Virtual

# Configuración del entorno
VENV := venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip
PYTEST := $(VENV)/bin/pytest

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
$(VENV)/bin/activate: requirements.txt
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	touch $(VENV)/bin/activate

# 'install' es un alias para asegurar que el venv esté listo
install: $(VENV)/bin/activate

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
	rm -rf __pycache__
	rm -rf app/__pycache__
	rm -rf tests/__pycache__
	rm -rf .pytest_cache
	rm -rf $(VENV)
	@echo "[✓] Entorno limpiado correctamente"