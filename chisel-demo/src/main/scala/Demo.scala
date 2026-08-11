package demo

import chisel3._
import chisel3.util._
import mq.util.decoder
import chisel3.util.experimental.decode._

// 极简演示模块:
//   1. 用 DecodeTable 对指令硬件解码,得到 InstType / ALUOp 两个字段
//   2. OneHot 编码可直接按位判断指令类型
//   3. 用 CtrlEnum.Mux 按解码结果选通 ALU 结果
class DecoderDemo extends Module {
  val io = IO(new Bundle {
    val inst   = Input(UInt(32.W))
    val a      = Input(UInt(32.W))
    val b      = Input(UInt(32.W))
    val iType  = Output(UInt(decoder.InstTypeCtrl.getWidth.W))
    val aluOp  = Output(UInt(decoder.ALUOpCtrl.getWidth.W))
    val aluRes = Output(UInt(32.W))
    val isALU  = Output(Bool())
    val isLSU  = Output(Bool())
    val isBRU  = Output(Bool())
    val isAdd  = Output(Bool())
  })

  val table  = new DecodeTable(decoder.Instructions.db(), decoder.DecodeFields.all())
  val result = table.decode(io.inst)

  // 解码结果直接赋值给输出
  io.iType := result(decoder.InstTypeField)
  io.aluOp := result(decoder.ALUOpField)

  // OneHot 编码:按位判断类型/操作
  io.isALU := io.iType(decoder.InstTypeCtrl.ALU)
  io.isLSU := io.iType(decoder.InstTypeCtrl.LSU)
  io.isBRU := io.iType(decoder.InstTypeCtrl.BRU)
  io.isAdd := io.aluOp(decoder.ALUOpCtrl.ADD)

  // CtrlEnum.Mux:OneHot 模式下等价于 Mux1H,
  // 映射顺序必须与 ALUOpCtrl 中 Value 定义顺序一致(9 项)
  val sraRes = (io.a.asSInt >> io.b(4, 0)).asUInt
  io.aluRes := decoder.ALUOpCtrl.Mux(io.aluOp, 0.U(32.W))(Seq(
    io.a + io.b,          // ADD
    io.a - io.b,          // SUB
    io.a < io.b,          // SLT / SLTU
    io.a ^ io.b,          // XOR
    io.a | io.b,          // OR
    io.a & io.b,          // AND
    io.a << io.b(4, 0),   // SLL
    io.a >> io.b(4, 0),   // SRL
    sraRes,               // SRA
  ))
}
