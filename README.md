# VisualDecoder（可视化译码器）

可视化 Chisel 硬件译码器代码生成工具。通过图形界面将 RISC-V 指令映射到控制信号（OneHot / Binary / Gray），自动生成 Chisel `CtrlEnum` + `DecodeField` 代码。

## 快速开始

```bash
git clone --recursive <repo-url>
cd VisualDecoder
make init      # 拉取子模块 → 生成指令数据库 → 创建虚拟环境
make run       # 启动应用
```

或使用独立脚本（可在任意目录下运行）：

```bash
./run.sh
```

## 工作流

1. **选择/创建 Profile** — 设置包名和 Ctrl.scala 输出路径
2. **勾选扩展** — 选择需要解码的 RISC-V 指令集（RV32I、M、Zicsr 等）
3. **新建 Decoder** — 命名（如 `InstType`），选择编码模式：Binary / OneHot / Gray
4. **创建分组** — 添加 ALU、LSU、BRU 等指令分组，通过下拉菜单或批量操作分配指令
5. **实时预览** — 右侧面板实时显示生成的 Chisel 代码，支持语法高亮
6. **保存** (`Ctrl+S`) — 保存到 JSON 配置文件，`Ctrl.scala` 文件按需导出

## 生成的代码示例

```scala
package mq.util.decoder

import chisel3._
import chisel3.util._
import mq.util.CtrlEnum
import chisel3.util.experimental.decode._

object InstTypeCtrl extends CtrlEnum(CtrlEnum.OneHot) {
  val ALU = Value
  val LSU = Value
  val BRU = Value

  def isALU: Seq[String] = Seq("ADD", "ADDI", "SUB", "AND", ...)
  def isLSU: Seq[String] = Seq("LW", "SW", "LB", ...)
  def isBRU: Seq[String] = Seq("BEQ", "BNE", "JAL", ...)
}

object InstTypeField extends DecodeField[InstructionPattern, UInt] {
  override def name: String = "InstTypeField"
  override def chiselType: UInt = UInt(InstTypeCtrl.getWidth.W)
  override def genTable(op: InstructionPattern): BitPat = {
    BitPat(op.nameMatch(map, 0.U(InstTypeCtrl.getWidth.W)))
  }
}
```

导出时同时生成 `DecodeFields.scala` 和 `Instructions.scala`。可选生成 `CtrlEnum.scala`（CtrlEnum 基类，含 Binary/OneHot/Gray 编码、Mux、PriorityMux）：

```scala
// DecodeFields.scala — 聚合所有 DecodeField
object DecodeFields {
  def all: Seq[DecodeField[InstructionPattern, UInt]] = {
    Seq(
      InstTypeField,
      ALUOpField,
      ...
    )
  }
}

// Instructions.scala — 指令数据库（数据来源：riscv-opcodes/inst.chisel）
object Instructions {
  val IType = Map(
    "ADD"  -> BitPat("b0000000??????????000?????0110011"),
    ...
  )
  val MType = Map(...)

  def db(): Seq[InstructionPattern] = { ... }
  def print() = { ... }
}

// CtrlEnum.scala — 可选生成的基类文件（Profile 中勾选"生成 CtrlEnum.scala"）
object CtrlEnum extends Enumeration {
  type enumType = Value
  val Binary, OneHot, Gray = Value
}

abstract class CtrlEnum(mode: CtrlEnum.enumType) {
  def Value: Int = { ... }           // 编码生成（Binary/OneHot/Gray）
  def Values: Seq[UInt] = { ... }    // 所有编码值
  def getWidth: Int = { ... }        // 位宽
  object Mux { ... }                 // 硬件多路选择器
  object PriorityMux { ... }         // 优先级选择器（仅 OneHot）
}
```

在硬件中使用：

```scala
val table = new DecodeTable(Instructions.db(), DecodeFields.all())
val result = table.decode(io.inst)
io.iType    := result(InstTypeField)
io.alu.op   := result(ALUOpField)
```

## 额外功能

### 可选生成 CtrlEnum.scala

在 Profile 设置中勾选"生成 CtrlEnum.scala"并指定包名（默认 `mq.util`）和输出路径（留空则使用上方输出路径），导出时会同时生成 `CtrlEnum.scala` 基类文件，包含 `CtrlEnum` 抽象类（Binary/OneHot/Gray 编码、`Mux`、`PriorityMux`）。该文件是所有解码器代码的依赖基础。

### 主题切换

菜单 **视图 → 切换主题** 在暗色/亮色（Tokyo Night 配色）之间切换。

## 配置文件

所有数据保存在 `~/.config/VisualDecoder/`：

| 文件 | 说明 |
|------|------|
| `config.json` | 全局设置：主题、最后使用的 Profile、指令数据库路径 |
| `profiles/<name>.json` | Profile 数据：包名、输出路径、扩展、Decoder 和分组定义 |

## Chisel Decoder 演示

`chisel-demo/` 目录包含一个独立的 SBT Chisel 演示工程，展示从 VisualDecoder 生成的解码器代码到硬件解码的完整流程（与 `mini-mq` 的译码方式一致）：

```bash
cd chisel-demo
make test      # 6 个测试用例（ChiselSim 硬件仿真）
make verilog   # 生成 Verilog → build/DecoderDemo.sv
```

演示内容：

1. `InstTypeCtrl` / `ALUOpCtrl` — VisualDecoder 导出的代码格式（CtrlEnum 分组 + DecodeField），可直接替换复用
2. `DecoderDemo` 模块 — `new DecodeTable(Instructions.db(), DecodeFields.all())` 硬件解码指令，输出 iType / aluOp / aluRes
3. OneHot 按位判断（`iType(InstTypeCtrl.ALU)`）+ `CtrlEnum.Mux` 选通 ALU 结果

## 环境要求

- Python >= 3.10
- PyQt6（自动安装）
- Chisel 演示需 JDK 和 SBT

## 快捷键

| 快捷键 | 功能 |
|--------|------|
| `Ctrl+S` | 保存 Profile |

