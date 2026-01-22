# path
TARGET_PATH=$(shell pwd)
CHISEL_TEST_PATH=$(shell pwd)/chisel-test/src/main/resources/rvdb
RISCV_OPCODES_PATH=$(shell pwd)/riscv-opcodes

# file
TARGET=$(TARGET_PATH)/riscv-opcode.db
CHISEL_TEST=$(CHISEL_TEST_PATH)/riscv-opcode.db
JSON=$(RISCV_OPCODES_PATH)/instr_dict.json

# 添加需要使用的指令集
EXTENSION=rv_i,rv_m,rv_zicsr

# venv
VENV = venv
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip

all: default
default: inst_db

$(VENV)/bin/activate: requirements.txt
	python3 -m venv $(VENV)
	$(PYTHON) -m pip install --upgrade pip
	$(PIP) install -r requirements.txt

inst_json:
	echo "$(RISCV_OPCODES_PATH)"
	$(MAKE) -C $(RISCV_OPCODES_PATH)

inst_db: inst_json $(VENV)/bin/activate
	$(PYTHON) db.py --input $(JSON) --output $(TARGET) --extension $(EXTENSION)

chisel_test: inst_json $(VENV)/bin/activate
	$(PYTHON) db.py --input $(JSON) --output $(CHISEL_TEST) --extension $(EXTENSION)

ctrl_genter: inst_json $(VENV)/bin/activate
	$(PYTHON) ctrl-gender.py

.PHONY: all default inst_json inst_db chisel_test
