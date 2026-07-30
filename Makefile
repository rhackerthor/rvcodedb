.PHONY: run clean install init

VENV := .venv
PYTHON := $(VENV)/bin/python3
PIP := $(VENV)/bin/pip

EXTENSIONS ?= "rv_i rv_m rv64_i rv_system rv_zicsr"

$(VENV)/bin/python3:
	python3 -m venv $(VENV)
	$(PIP) install -r requirements.txt

init:
	git submodule update --init --recursive
	$(MAKE) -C riscv-opcodes EXTENSIONS=$(EXTENSIONS)
	python3 -m venv $(VENV)
	$(PIP) install -r requirements.txt

run: $(VENV)/bin/python3
	$(PYTHON) -m src.main

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name '*.pyc' -delete 2>/dev/null || true
	rm -rf run.sh

install: $(VENV)/bin/python3
