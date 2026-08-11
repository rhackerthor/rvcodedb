package mq.util.decoder

import chisel3._
import chisel3.util._
import mq.util.CtrlEnum
import chisel3.util.experimental.decode._

// === CtrlEnum ===
// OneHot 编码:9 个 ALU 操作,每组一条指令,对应一个编码位
object ALUOpCtrl extends CtrlEnum(CtrlEnum.OneHot) {
  val ADD = Value
  val SUB = Value
  val SLT = Value
  val XOR = Value
  val OR  = Value
  val AND = Value
  val SLL = Value
  val SRL = Value
  val SRA = Value

  def isADD: Seq[String] = Seq("ADD", "ADDI", "LUI", "AUIPC")
  def isSUB: Seq[String] = Seq("SUB")
  def isSLT: Seq[String] = Seq("SLT", "SLTU")
  def isXOR: Seq[String] = Seq("XOR")
  def isOR: Seq[String]  = Seq("OR")
  def isAND: Seq[String] = Seq("AND")
  def isSLL: Seq[String] = Seq("SLL")
  def isSRL: Seq[String] = Seq("SRL")
  def isSRA: Seq[String] = Seq("SRA")
}

// === DecodeField ===
object ALUOpField extends DecodeField[InstructionPattern, UInt] {
  override def name: String = "ALUOpField"
  override def chiselType: UInt = UInt(ALUOpCtrl.getWidth.W)

  private def map: Seq[(Seq[String], UInt)] = Seq(
    ALUOpCtrl.isADD -> ALUOpCtrl.Values(ALUOpCtrl.ADD),
    ALUOpCtrl.isSUB -> ALUOpCtrl.Values(ALUOpCtrl.SUB),
    ALUOpCtrl.isSLT -> ALUOpCtrl.Values(ALUOpCtrl.SLT),
    ALUOpCtrl.isXOR -> ALUOpCtrl.Values(ALUOpCtrl.XOR),
    ALUOpCtrl.isOR  -> ALUOpCtrl.Values(ALUOpCtrl.OR),
    ALUOpCtrl.isAND -> ALUOpCtrl.Values(ALUOpCtrl.AND),
    ALUOpCtrl.isSLL -> ALUOpCtrl.Values(ALUOpCtrl.SLL),
    ALUOpCtrl.isSRL -> ALUOpCtrl.Values(ALUOpCtrl.SRL),
    ALUOpCtrl.isSRA -> ALUOpCtrl.Values(ALUOpCtrl.SRA),
  )

  override def genTable(op: InstructionPattern): BitPat = {
    BitPat(op.nameMatch(map, 0.U(ALUOpCtrl.getWidth.W)))
  }
}
