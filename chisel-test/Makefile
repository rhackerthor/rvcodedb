SBT     := sbt
MILL    := mill
GEN_DIR := build

all: verilog
default: verilog

verilog:
	$(MILL) top.runMain rv.Main -td=$(GEN_DIR) --full-stacktrace

verilog-sbt:
	$(SBT) "run --target-dir=$(GEN_DIR)"

clean: 
	rm -rf $(GEN_DIR)

.PHONY: all default verilog verilog-sbt clean 
