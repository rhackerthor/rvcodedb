SBT := sbt

test:
	$(SBT) test

verilog:
	$(SBT) "runMain Main --target-dir=build"
	@echo "Verilog 已生成: build/DecoderDemo.sv"

clean:
	rm -rf build target project/target project/project

.PHONY: test verilog clean
