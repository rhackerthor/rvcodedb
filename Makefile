# path
TARGET_PATH=$(shell pwd)
# TARGET_PATH=$(shell pwd)/../src/main/resources/rvdb
CHISEL_TEST_PATH=$(shell pwd)/chisel-test/src/main/resources/rvdb
RISCV_OPCODES_PATH=$(shell pwd)/riscv-opcodes

# file
TARGET=$(TARGET_PATH)/riscv-opcode.db
CHISEL_TEST=$(CHISEL_TEST_PATH)/riscv-opcode.db
JSON=$(RISCV_OPCODES_PATH)/instr_dict.json

# 添加需要使用的指令集
EXTENSION=rv_i,rv_m,rv_zicsr,rv64_i,rv_system

# venv
VENV = venv
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip

all: default
default: inst-db

$(VENV)/bin/activate: requirements.txt
	python3 -m venv $(VENV)
	$(PYTHON) -m pip install --upgrade pip
	$(PIP) install -r requirements.txt

inst-json:
	echo "$(RISCV_OPCODES_PATH)"
	$(MAKE) -C $(RISCV_OPCODES_PATH)

inst-db: inst-json $(VENV)/bin/activate
	$(PYTHON) db.py --input $(JSON) --output $(TARGET) --extension $(EXTENSION)

chisel-test: inst-json $(VENV)/bin/activate
	$(PYTHON) db.py --input $(JSON) --output $(CHISEL_TEST) --extension $(EXTENSION)

ctrl-gender: inst-db $(VENV)/bin/activate
	$(PYTHON) ctrl-gender.py

.PHONY: all default inst_json inst_db chisel_test
