# 项目：可视化 Chisel Decoder 代码生成器 VisualDecoder

## 概述
VisualDecoder 是一个基于 PyQt6 的桌面工具，通过可视化界面将 RISC-V 指令与独热码/二进制/格雷码信号进行映射，并自动生成 Chisel 硬件解码器代码（`CtrlEnum` + `DecodeField` 模式）。

---

## 技术要求

### 运行时环境
- Python >= 3.10
- PyQt6（GUI 框架）
- 标准库 json, os, pathlib

### 配置目录
- `~/.config/VisualDecoder/` — 所有配置文件、Profile 数据均存放在此目录下
- 首次启动时自动创建该目录及默认结构

---

## 核心概念

### 1. Profile（配置）
- 一个 Profile 代表一组完整的代码生成配置，以 JSON 文件形式保存在 `~/.config/VisualDecoder/profiles/<name>.json`
- 每个 Profile 包含：
  - `name`: 配置名称
  - `output_path`: 代码输出目录路径
  - `selected_extensions`: 选中的 RISC-V 扩展列表（如 `["rv_i", "rv_m"]`）
  - `decoders`: 一组 Decoder 定义（支持多个 CtrlEnum+Field 组合）
  - `package_name`: 生成的 Scala 包名（默认 `mq.util.decoder`）

### 2. Decoder
- 一个 Decoder 对应一个 `CtrlEnum` + `DecodeField` 的组合
- 包含：
  - `name`: 解码器名称（如 `InstType`），用于生成 `%NAME%Ctrl` 和 `%NAME%Field`
  - `ctrl_enum_mode`: 编码模式，值为 `Binary` | `OneHot` | `Gray`
  - `groups`: 分组列表

### 3. Group（分组）
- 用户自定义的指令分组
- 包含：
  - `name`: 分组名（如 `ALU`, `LSU`, `BRU`），用于生成 `is%NAME%` 方法和 `val %NAME% = Value`
  - `instructions`: 该分组包含的指令名称列表

**互斥约束（核心规则）：**
> 在同一个 Decoder 内部，各分组的指令集合**必须两两互斥**，即：一条指令只能映射到**唯一一个**分组，不能同时出现在两个分组中。<br>
> 例如，`ADD` 指令不能既属于 `isALU` 又属于 `isBRU`，只能选择其一。<br>
> 这是硬件解码器的固有要求——每条指令在解码阶段必须产生唯一确定的信号值。

### 4. Instruction（指令）
- 数据来源：`riscv-opcodes/instr_dict.json`
- 每条指令包含：名称、encoding、match、mask、extension、variable_fields
- 用户在 GUI 中按扩展筛选，然后将指令分配到不同分组

---

## UI 布局（三栏式）

```
┌───────────────────┬──────────────────────┬─────────────────────┐
│   指令列表         │     分组编辑器        │     代码预览         │
│  (Instruction      │   (Group Editor)     │   (Code Preview)    │
│   List Panel)      │                      │                     │
│                    │                      │                     │
│ [RISC-V 扩展筛选]   │ Profile 选择器       │ 生成的 Scala 代码   │
│  ☑ rv_i           │ + 新建/删除/切换/复制 │ 实时预览             │
│  ☐ rv_m           │                      │ 语法高亮             │
│  ☐ rv_zicsr       │ 名称/包名/输出路径    │ 复制到剪贴板         │
│                    │                      │ 导出 .scala 文件     │
│ [变量字段筛选]      │ Decoder: InstType     │                     │
│  ☑ rd             │  模式: [OneHot ▼]    │                     │
│  ☐ rs1            │  + 新建/删除          │                     │
│  ☐ rs2            │                      │                     │
│  ☐ imm12          │ 分组列表:              │                     │
│                    │ ┌──────────────────┐ │                     │
│ [批量操作]          │ │ ALU              │ │                     │
│  分配到:[▼][批量分配]│ │ LSU              │ │                     │
│  [全选分配][取消分配]│ │ BRU              │ │                     │
│  [全部取消]          │ │ + 新建分组       │ │                     │
│                    │ │ ↑ ↓ 排序         │ │                     │
│ [搜索指令...] N / M │ └──────────────────┘ │                     │
│                    │                      │                     │
│ ┌────────────────┐ │ 分组编辑:              │                     │
│ │ 指令   分组     │ │  名称/重命名/删除     │                     │
│ │ ADD   [ALU ▼] │ │                      │                     │
│ │ ADDI  [ALU ▼] │ │ [保存 Profile]       │                     │
│ │ SUB   [--- ▼] │ │ [导出代码]            │                     │
│ │ ...            │ │                      │                     │
│ └────────────────┘ │                      │                     │
└───────────────────┴──────────────────────┴─────────────────────┘
│                         状态栏                                 │
│ Profile: my [已保存] | 输出: ~/src | 指令库: ../riscv | 主题: 暗色 │
└────────────────────────────────────────────────────────────────┘
```

---

## 交互流程

1. **启动应用** → 加载 Profile 列表（从 `~/.config/VisualDecoder/profiles/`），自动恢复上次使用的 Profile
2. **新建/选择 Profile** → 设置名称、输出路径、包名
3. **选择扩展** → 勾选需要加载的 RISC-V 扩展，指令列表随之更新
4. **变量字段筛选** → 按 `variable_fields`（如 `rd`, `rs1`, `imm12`）进一步过滤指令
5. **搜索指令** → 搜索栏输入名称实时过滤指令列表，右侧显示命中计数
6. **新建 Decoder** → 输入名称（如 `InstType`），选择编码模式
7. **创建分组** → 输入分组名，支持上下移动调整顺序（顺序决定编码值）
8. **分配指令** → 通过下拉菜单为每条指令选择所属分组。**同一条指令只能分配给一个分组**，选择新分组时自动从旧分组移除
9. **批量操作** → 批量分配/取消分配/全部取消，配合搜索和字段筛选可快速分组
10. **实时预览** → 右侧实时显示生成的 Chisel 代码（Scala 语法高亮）
11. **保存 Profile** → `Ctrl+S` 或按钮直接保存到 JSON 配置文件，**无弹窗确认**。输出路径不存在时自动创建。状态栏实时显示 `[已保存]` / `[未保存]` 标记，任何修改（指令分配、分组编辑、Decoder/Profile 变更）会立即将标记切换为 `[未保存]`。仅当检测到指令重复冲突时阻止保存并在状态栏显示错误。
12. **导出代码** → 将生成的 .scala 文件写入 output_path（含 `{Name}Ctrl.scala`、`DecodeFields.scala`、`Instructions.scala`）

---

## CtrlEnum 编码参考

项目中引用的 `CtrlEnum` 类支持三种编码模式：

| 模式    | Value 生成逻辑         | getWidth 结果    | 示例(3个分组)              |
|---------|-----------------------|------------------|---------------------------|
| Binary  | 0, 1, 2, ...          | `log2Ceil(n)`    | 0b00, 0b01, 0b10         |
| OneHot  | 0x1, 0x2, 0x4, ...    | `n`              | 0b001, 0b010, 0b100      |
| Gray    | Gray(0), Gray(1), ... | `log2Ceil(n)`    | 0b00, 0b01, 0b11          |

分组按定义顺序依次调用 `Value` 获取编码值。

---

## 运行方式

项目使用 `.venv` 虚拟环境管理依赖。首次运行前自动创建虚拟环境并安装 PyQt6。

```bash
make init    # 完整初始化：子模块更新 → 生成指令数据库 → 创建 venv → 安装依赖
make init EXTENSIONS="rv_i rv_m"  # 指定扩展（默认 rv_i rv_m rv64_i rv_system rv_zicsr）
make run     # 自动创建 .venv 并启动应用
make clean   # 清理 Python 缓存和 run.sh
make install # 仅创建虚拟环境并安装依赖
./run.sh     # 生成/使用虚拟环境并启动应用（首次自动创建 venv）
```

### `make init` 流程

1. `git submodule update --init --recursive` — 拉取 riscv-opcodes 子模块
2. `make -C riscv-opcodes` — 运行 riscv-opcodes 的 Makefile 生成 `instr_dict.json`，`EXTENSIONS` 变量控制包含的扩展
3. `python3 -m venv .venv` — 创建 Python 虚拟环境
4. `pip install -r requirements.txt` — 安装 PyQt6

---

## 指令数据库切换

用户可通过菜单 **文件 → 选择指令数据库...** 更换 `instr_dict.json` 所在目录路径。新路径保存到 `~/.config/VisualDecoder/config.json` 的 `riscv_opcodes_path` 字段，切换后自动重新加载指令并刷新界面。状态栏显示当前解析后的绝对路径。

---

## 代码生成模板

### 生成文件命名
- `{DecoderName}Ctrl.scala` — 每个 Decoder 生成一个独立的 `.scala` 文件，包含 CtrlEnum 和 DecodeField
- `DecodeFields.scala` — 聚合文件，包含 `DecodeFields` object，将所有 Field 对象汇总到 `def all` 方法中

### 模板变量
- `%PACKAGE%` → Profile 的 package_name
- `%NAME%` → Decoder 的 name
- `%MODE%` → 编码模式（`CtrlEnum.Binary` / `CtrlEnum.OneHot` / `CtrlEnum.Gray`）
- `%GROUPS%` → 循环生成各分组内容

### 输出模板（假想代码）

```scala
package %PACKAGE%

import chisel3._
import chisel3.util._
import mq.util.CtrlEnum
import chisel3.util.experimental.decode._

// === CtrlEnum ===
object %NAME%Ctrl extends CtrlEnum(CtrlEnum.%MODE%) {
  %FOR_EACH_GROUP%
  val %GROUP_NAME% = Value
  %END_FOR%

  %FOR_EACH_GROUP%
  def is%GROUP_NAME%: Seq[String] = Seq(
    %FOR_EACH_INSTRUCTION%
    "%INSTRUCTION_NAME%",
    %END_FOR%
  )
  %END_FOR%
}

// === DecodeField ===
object %NAME%Field extends DecodeField[InstructionPattern, UInt] {
  override def name: String = "%NAME%Field"
  override def chiselType: UInt = UInt(%NAME%Ctrl.getWidth.W)

  private def map: Seq[(Seq[String], UInt)] = Seq(
    %FOR_EACH_GROUP%
    %NAME%Ctrl.is%GROUP_NAME% -> %NAME%Ctrl.Values(%NAME%Ctrl.%GROUP_NAME%),
    %END_FOR%
  )

  override def genTable(op: InstructionPattern): BitPat = {
    BitPat(op.nameMatch(map, 0.U(%NAME%Ctrl.getWidth.W)))
  }
}
```

### DecodeFields 聚合模板

导出时自动生成 `DecodeFields.scala`，聚合所有 Decoder 的 Field 对象：

```scala
package %PACKAGE%

import chisel3._
import chisel3.util._
import chisel3.util.experimental.decode._

object DecodeFields {
  def all: Seq[DecodeField[InstructionPattern, UInt]] = {
    Seq(
      %FOR_EACH_DECODER%
      %NAME%Field,
      %END_FOR%
    )
  }
}
```

---

### Instructions.scala 输出模板

导出代码时自动生成 `Instructions.scala`，将指令数据库按扩展分组导出，包含 `InstructionPattern` case class 和 `Instructions` 对象：

```scala
package %PACKAGE%

import chisel3._
import chisel3.util._
import chisel3.util.experimental.decode._

case class InstructionPattern(
    name: String,
    code: BitPat,
) extends DecodePattern {
  override def bitPat: BitPat = code
  def nameMatch[T <: Data](
    map: Seq[(Seq[String], T)],
    default: T
  ): T = {
    map.view
      .collectFirst { case (set, enumType) if (set.contains(name)) => enumType }
      .getOrElse(default)
  }
}

object Instructions {
  val IType = Map(
    "ADD"              -> BitPat("b0000000??????????000?????0110011"),
    "ADDI"             -> BitPat("b?????????????????000?????0010011"),
    ...
  )
  val MType = Map(
    "DIV"              -> BitPat("b0000001??????????100?????0110011"),
    ...
  )

  def db(): Seq[InstructionPattern] = { ... }
  def print() = { ... }
}
```

**数据来源**：指令分组及类型名称（`IType`、`MType` 等）直接解析 `riscv-opcodes/inst.chisel`，与官方 riscv-opcodes 仓库保持一致，确保指令归属准确无误。

---

## 数据流

```
                    ┌──────────────────────────┐
                    │ Makefile EXTENSIONS       │
                    │    ↓ make -C riscv-opcodes│
                    │  instr_dict.json          │
                    │  inst.chisel              │
                    │ riscv_opcodes_path ←──────┼──→ 用户可在 GUI 中修改
                    └──────────────────────────┘
                                │
           ┌─────────────────────┤
           ▼                     ▼
    InstructionLoader    insts_scala.py
           │                     │
           ├── (扩展筛选)         ├── 解析 inst.chisel
           ├── (字段筛选)         ├── 提取按扩展分组的 Map
           └── (搜索筛选)         └──→ Instructions.scala
           │                     (随导出写入 output_path)
           ▼
   Profile (配置状态)  ← 保存在 ~/.config/VisualDecoder/profiles/<name>.json
          │
          ▼
   CodeGenerator        ← 读取 Profile 中的 decoders + groups
          │
          ▼
   {Name}Ctrl.scala     ← 写入 output_path（每个 Decoder 一个文件）
          │
          ▼
   DecodeFields.scala    ← 聚合文件，包含 DecodeFields.all
          │
          ▼
   Instructions.scala    ← 指令数据库文件，按扩展分组
```

---

## 项目文件结构

```
rvcodedb/
├── Agent.md                        # 本文件
├── Makefile                        # 启动/构建/初始化脚本
├── requirements.txt                # Python 依赖（PyQt6）
├── .gitignore                      # Git 忽略规则
├── .gitmodules                     # Git 子模块配置
├── riscv-opcodes/                  # git submodule，RISC-V 指令数据源
│   ├── instr_dict.json             # 主要数据源（由 riscv-opcodes Makefile 生成）
│   └── ...
├── run.sh                          # 启动脚本（自动创建 venv 并运行应用）
├── src/
│   ├── __init__.py
│   ├── main.py                     # 应用入口
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── main_window.py          # 主窗口，三栏布局，信号协调
│   │   ├── instruction_panel.py    # 左侧：扩展筛选、字段筛选、搜索、批量操作、指令列表
│   │   ├── group_editor.py         # 中间：Profile/Decoder/Group 编辑
│   │   ├── code_preview.py         # 右侧：代码预览面板（复制/导出）
│   │   ├── dialogs.py              # 对话框（新建Profile、新建Decoder、新建分组、重命名）
│   │   ├── themes.py               # Tokyo Night 暗色/亮色 QSS 主题
│   │   └── syntax_highlighter.py   # Scala 语法高亮器
│   ├── models/
│   │   ├── __init__.py
│   │   ├── profile.py              # Profile/Decoder/Group/Instruction 数据模型
│   │   └── profile_manager.py      # Profile CRUD 操作（读写 JSON）
│   ├── codegen/
│   │   ├── __init__.py
│   │   ├── template.py             # 代码生成逻辑
│   │   ├── insts_scala.py          # Instructions.scala 生成模块（InstructionPattern + Instructions 对象）
│   │   └── templates/
│   │       ├── __init__.py
│   │       └── ctrl_enum.py        # CtrlEnum + DecodeField 模板字符串
│   └── utils/
│       ├── __init__.py
│       ├── config.py               # 配置目录管理（~/.config/VisualDecoder）
│       └── instruction_loader.py   # 指令数据加载、过滤工具函数
└── .venv/                          # Python 虚拟环境（make run 自动创建）

chisel-demo/                         # Chisel Decoder 演示项目（独立 SBT/Mill 工程）
├── build.sbt / build.mill / Makefile
├── src/main/scala/
│   ├── Main.scala                   # 入口：生成 Verilog
│   ├── Demo.scala                   # DecoderDemo 模块：解码指令，输出 InstType + ALUOp
│   └── util/
│       ├── CtrlEnum.scala           # 枚举编码（Binary/OneHot/Gray + Mux）
│       └── decoder/
│           ├── InstructionPattern.scala  # 指令模式匹配
│           ├── DBReader.scala        # .db 文件读取器
│           ├── Decoder.scala         # Decoder 对象：getFields → DecodeFields.all + getDB → DecodeTable
│           ├── InstTypeCtrl.scala    # 指令类型枚举（ALU/MUL/DIV/LSU/BRU）
│           ├── InstTypeField.scala   # InstType 解码字段
│           ├── ALUOpCtrl.scala       # ALU 操作枚举（ADD/SLT/AND/OR/XOR/SLL/SRL/SRA）
│           └── ALUOpField.scala      # ALUOp 解码字段
├── src/main/resources/rvdb/
│   └── riscv-opcode.db              # RV32I + M 指令数据库（45条指令）
└── src/test/scala/
    └── DecoderTest.scala            # 6 个测试用例，验证指令解码正确性
```

---

## 配置文件 JSON Schema

### Profile JSON 结构 (`~/.config/VisualDecoder/profiles/<name>.json`)

```json
{
  "name": "my_config",
  "output_path": "/home/user/project/src/main/scala/mq/util/decoder",
  "package_name": "mq.util.decoder",
  "selected_extensions": ["rv_i", "rv_m"],
  "decoders": [
    {
      "name": "InstType",
      "ctrl_enum_mode": "OneHot",
      "groups": [
        {
          "name": "ALU",
          "instructions": ["ADD", "ADDI", "SUB", "AND", "OR", "XOR", "SLL", "SRL", "SRA", "SLT", "SLTU"]
        },
        {
          "name": "LSU",
          "instructions": ["LW", "SW", "LB", "SB", "LH", "SH", "LBU", "LHU"]
        },
        {
          "name": "BRU",
          "instructions": ["BEQ", "BNE", "BLT", "BGE", "BLTU", "BGEU"]
        }
      ]
    },
    {
      "name": "FuncUnit",
      "ctrl_enum_mode": "Binary",
      "groups": [
        {
          "name": "Arith",
          "instructions": ["ADD", "SUB", "ADDI"]
        },
        {
          "name": "Logic",
          "instructions": ["AND", "OR", "XOR", "ANDI", "ORI", "XORI"]
        }
      ]
    }
  ]
}
```

### 全局配置 (`~/.config/VisualDecoder/config.json`)

```json
{
  "last_profile": "my_config",
  "window_geometry": null,
  "riscv_opcodes_path": "./riscv-opcodes",
  "theme": "night"
}
```

- `riscv_opcodes_path`：指令数据库（`instr_dict.json`）所在目录的路径，支持相对路径或绝对路径
- 用户可在 GUI 设置中修改此路径（如指向其他版本的 riscv-opcodes 仓库）
- 若路径无效，加载指令时提示用户并在 UI 中引导修正

---

## 实现要点

1. **指令互斥性校验（实时 + 保存时）**：当用户为指令切换分组时，自动从旧分组移除该指令，确保同一条指令只属于一个分组。保存 Profile 时做最终校验，若检测到指令重复分配则在状态栏显示错误并阻止保存
2. **无弹窗保存 + 脏状态追踪**：`Ctrl+S` 或保存按钮直接保存，不弹出确认对话框。状态栏显示 `[已保存]` / `[未保存]` 标记，任何数据变更（指令分配、分组编辑、Decoder/Profile 变更）自动标记为未保存状态。输出路径不存在时自动创建目录
3. **代码预览**：右侧面板为只读代码编辑器，使用 `QSyntaxHighlighter` 实现 Scala 语法高亮（关键字、类型、字符串、数字、注释、注解），实时反映 Profile 修改
4. **Profile 管理**：支持 Profile 的创建、切换、复制、删除、重命名。重命名时同步更新文件系统中的 JSON 文件和 `config.json` 中的 `last_profile` 引用
5. **输出路径自动创建**：保存或导出时若 output_path 不存在则自动递归创建目录
6. **CtrlEnum 分组顺序**：分组顺序决定编码值，支持上移/下移调整顺序
7. **暗色/浅色主题切换**：通过菜单 **视图 → 切换主题** 在 Dark/Light 之间切换，持久化到 `config.json`。配色为 Tokyo Night 柔化版，降低了原始 Tokyo Night 的对比度和饱和度。使用 Qt StyleSheet 实现，`src/ui/themes.py` 存放完整 QSS 字符串
8. **QScrollArea 背景适配**：QScrollArea 内的容器需在 `setWidget()` 之后调用 `setAutoFillBackground(False)`，使其透明继承滚动区域 QSS 背景色
9. **语法高亮配色**：`src/ui/syntax_highlighter.py` 中的颜色值与暗色主题统一柔化
10. **指令数据库切换**：菜单 **文件 → 选择指令数据库...** 更换 `instr_dict.json` 路径，保存到 `config.json` → `riscv_opcodes_path`。切换后重新加载并刷新界面，状态栏显示解析后的绝对路径
11. **变量字段筛选**：左侧面板第二栏，勾选 `variable_fields`（rd, rs1, rs2, imm12 等）后指令列表显示包含任一选中字段的指令（OR 逻辑），与扩展筛选联动
12. **搜索指令**：搜索栏输入名称实时过滤指令列表，大小写不敏感子串匹配，与扩展筛选 + 字段筛选取交集，右上角显示命中计数
13. **批量操作**：批量分配（将可见指令分配到目标分组）、全选分配（一键分配可见指令到目标分组）、取消分配（取消可见指令的分配）、全部取消（清空当前 Decoder 所有分组）
14. **JSON 容错**：`load_global_config()` 和 `load_profile()` 对损坏的 JSON 文件做 try/except 处理，返回默认值而非崩溃
15. **配置恢复**：若 `last_profile` 指向的 Profile 不存在，启动时自动加载第一个可用 Profile
## 键盘快捷键：`Ctrl+S` 保存 Profile

---

## Chisel Decoder 演示项目 (`chisel-demo/`)

独立的 SBT/Mill Chisel 工程，展示从指令数据库到硬件解码器的完整流程。

### 运行方式

```bash
cd chisel-demo
make test      # 运行测试（6 个测试用例）
make verilog   # 生成 Verilog → build/DecoderDemo.sv
```

### Decode 流程

```
riscv-opcode.db ──→ DBReader ──→ Seq[InstructionPattern]
                                       │
          ┌────────────────────────────┤
          ▼                            ▼
   InstTypeCtrl (OneHot)      ALUOpCtrl (OneHot)
   InstTypeField              ALUOpField
          │                            │
          └────────┬───────────────────┘
                   ▼
            DecodeTable ──→ decode(inst: UInt) ──→ Map[DecodeField, UInt]
                   │
          ┌────────┴────────┐
          ▼                 ▼
    result(InstTypeField)  result(ALUOpField)
          │                 │
          ▼                 ▼
   CtrlEnum.Mux(key)   CtrlEnum.Mux(key)
   (硬件多路选择器)      (硬件多路选择器)
```

### 关键代码示例

**CtrlEnum 定义 (OneHot 编码)**:
```scala
object InstTypeCtrl extends CtrlEnum(CtrlEnum.OneHot) {
  val ALU, MUL, DIV, LSU, BRU = Value  // 0b00001, 0b00010, 0b00100, 0b01000, 0b10000
  def isALU: Seq[String] = Seq("add", "addi", "and", ...)  // 指令→枚举值 映射表
}
```

**DecodeField 定义**:
```scala
object InstTypeField extends DecodeField[InstructionPattern, UInt] {
  override def name: String = "InstTypeField"
  override def chiselType: UInt = UInt(InstTypeCtrl.getWidth.W)
  private def map: Seq[(Seq[String], UInt)] = Seq(
    InstTypeCtrl.isALU -> InstTypeCtrl.Values(InstTypeCtrl.ALU),  // Seq["add","addi",...] -> 0b00001.U
    ...
  )
  override def genTable(op: InstructionPattern): BitPat = {
    BitPat(op.nameMatch(map, 0.U(InstTypeCtrl.getWidth.W)))
  }
}
```

**硬件模块中使用**:
```scala
val table = new DecodeTable(Decoder.getDB(dbPath), Decoder.getFields())
val result = table.decode(io.inst)           // 解码一条指令
val iType = result(InstTypeField)            // 提取指令类型（OneHot 编码）
val isALU = iType(InstTypeCtrl.ALU)          // 按位判断是否为 ALU 指令

// 使用 CtrlEnum.Mux 实现硬件多路选择
val aluResult = ALUOpCtrl.Mux(aluOp, 0.U)(Seq(
  a + b,    // ADD
  slt,      // SLT
  a & b,    // AND
  a | b,    // OR
  a ^ b,    // XOR
  a << b,   // SLL
  a >> b,   // SRL
  sraRes    // SRA
))
```

### 核心文件清单

| 文件 | 行数 | 说明 |
|------|------|------|
| `CtrlEnum.scala` | 80 | 枚举编码基类，支持 Binary/OneHot/Gray，提供 Mux/PriorityMux 硬件选择器 |
| `InstructionPattern.scala` | 30 | 指令模式类，继承 DecodePattern，实现 BitPat 和 nameMatch |
| `DBReader.scala` | 25 | 从空格分隔的 .db 文件读取指令并构建 InstructionPattern 列表 |
| `Decoder.scala` | 15 | Decoder 伴生对象，聚合所有 Field 和 DB 加载逻辑 |
| `Demo.scala` | 30 | 演示模块：解码 RISC-V 指令，输出 InstType 和 ALUOp |
| `DecoderTest.scala` | 80 | 6 个测试用例，验证 ADD/BEQ/LW/XOR/OR 等指令的正确解码 |

---

## Tokyo Night 配色参考

### Night（暗色主题）

暗色主题配色经过柔化处理，降低了原始 Tokyo Night 的对比度和色彩饱和度，适合长时间使用。

| Token      | 颜色值     | 用途                     |
|-----------|-----------|--------------------------|
| bg        | `#242530` | 主背景（编辑区）           |
| bg_dark   | `#1f202a` | 侧边栏/面板/状态栏背景     |
| bg_highlight | `#2a2c38` | 当前行/悬停高亮           |
| bg_input  | `#1c1c24` | 输入框/下拉框背景          |
| fg        | `#9b9eb0` | 主前景文字                |
| fg_dark   | `#6e7080` | 次要文字/状态栏文字        |
| fg_gutter  | `#44475a` | 行号/折叠栏/滚动条        |
| blue      | `#7d8ab5` | 函数/类型/链接             |
| purple    | `#9e8bc0` | 关键字/Class/Tag         |
| cyan      | `#7d9eb5` | 属性/变量/标记            |
| green     | `#7db8a0` | 字符串/Hint              |
| yellow    | `#b09868` | 参数/Warning             |
| orange    | `#c4906a` | 常量/数字                |
| red       | `#f7768e` | 错误/删除                |
| comment   | `#56576a` | 注释                     |
| border    | `#1c1c22` | 面板边框                 |
| active    | `#4a5a8a` | 选中态/高亮色            |
| btn_text  | `#c8ccd4` | 按钮文字                 |
| selection | `#515c7e4d` | 文本选择背景          |

### Day（浅色主题）

| Token      | 颜色值     | 用途                     |
|-----------|-----------|--------------------------|
| bg        | `#e1e2e7` | 主背景（编辑区）           |
| bg_dark   | `#d0d5e3` | 侧边栏/浮层面板背景        |
| bg_highlight | `#c4c8da` | 当前行高亮               |
| fg        | `#3760bf` | 主前景文字                |
| fg_dark   | `#6172b0` | 次要文字/侧边栏文字        |
| fg_gutter  | `#a8aecb` | 行号/折叠栏               |
| blue      | `#2e7de9` | 函数/链接                 |
| purple    | `#9854f1` | 关键字/Class/Tag         |
| cyan      | `#007197` | 属性/变量/标记            |
| green     | `#587539` | 字符串/Hint              |
| yellow    | `#8c6c3e` | 参数/Warning             |
| orange    | `#b15c00` | 常量/数字                |
| red       | `#f52a65` | 错误/删除                |
| comment   | `#848cb5` | 注释                     |
| border    | `#b4b5b9` | 面板边框                 |
| active    | `#4094a3` | 选中态/高亮色            |
| selection | `#b7c1e3` | 文本选择背景             |

### 在 PyQt 中应用

使用 Qt StyleSheet (QSS) 方式实现，示例结构：

```python
# Night 主题示例（柔化版）
NIGHT_QSS = """
QMainWindow { background-color: #242530; }
QLabel { color: #9b9eb0; }
QTreeWidget, QListWidget { 
    background-color: #1f202a; 
    color: #9b9eb0; 
    border: 1px solid #1c1c22; 
}
QTreeWidget::item:selected, QListWidget::item:selected { 
    background-color: #4a5a8a; 
}
QComboBox {
    background-color: #1c1c24;
    color: #9b9eb0;
    border: 1px solid #1a1a20;
}
QPushButton {
    background-color: #4a5a8a;
    color: #c8ccd4;
    border: none;
    padding: 4px 12px;
}
QPushButton:hover { background-color: #5a6a9a; }
QTextEdit, QPlainTextEdit {
    background-color: #242530;
    color: #9b9eb0;
    font-family: monospace;
}
QStatusBar { 
    background-color: #1f202a; 
    color: #6e7080; 
    border-top: 1px solid #1c1c22; 
}
QScrollArea { background-color: #1f202a; border: none; }
"""
```

---

## 待确认事项

- [x] 一键复制到剪贴板（已实现）
- [ ] 是否需要支持从 `inst.chisel` 文件导入额外的指令信息（如指令类型分类映射）？
- [ ] 生成的 .scala 文件是否需要一个包对象（package.scala）来统一管理 import？
- [ ] 是否需要支持拖拽分组排序（替代当前的上移/下移按钮）？
- [ ] 是否需要支持从 Profile 导入/导出为 ZIP？
- [ ] 是否需要在启动时校验 `riscv_opcodes_path` 路径有效性并自动提示？
