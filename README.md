# RVCODE-DB
- 该项目通过python解析riscv-opcodes提供的json文件,生成便于Chisel读取的csv文件
## 使用方法:
``` bash
# 拉取子项目
git submodule update --init --recursive
# 生成csv文件
make
```
- 通过修改`Makefile`中的`PATH`参数指定目标文件的路径
## chisel test
- 该项目提供了一个chisel参考项目,完成读取csv文件并使用decode类完成译码逻辑的生成
``` bash
# 执行下面的命令,会生成一个含有部分译码信息的csv文件
make chisel
```
```
