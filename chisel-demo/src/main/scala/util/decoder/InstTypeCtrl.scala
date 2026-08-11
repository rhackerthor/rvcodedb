package mq.util.decoder

import chisel3._
import chisel3.util._
import mq.util.CtrlEnum
import chisel3.util.experimental.decode._

// === CtrlEnum ===
// OneHot 编码:ALU=0b001, LSU=0b010, BRU=0b100
object InstTypeCtrl extends CtrlEnum(CtrlEnum.OneHot) {
  val ALU = Value
  val LSU = Value
  val BRU = Value

  def isALU: Seq[String] = Seq(
    "ADD",
    "ADDI",
    "SUB",
    "AND",
    "OR",
    "XOR",
    "SLL",
    "SRL",
    "SRA",
    "SLT",
    "SLTU",
    "LUI",
    "AUIPC",
  )
  def isLSU: Seq[String] = Seq(
    "LW",
    "SW",
  )
  def isBRU: Seq[String] = Seq(
    "BEQ",
    "JAL",
    "JALR",
  )
}

// === DecodeField ===
object InstTypeField extends DecodeField[InstructionPattern, UInt] {
  override def name: String = "InstTypeField"
  override def chiselType: UInt = UInt(InstTypeCtrl.getWidth.W)

  private def map: Seq[(Seq[String], UInt)] = Seq(
    InstTypeCtrl.isALU -> InstTypeCtrl.Values(InstTypeCtrl.ALU),
    InstTypeCtrl.isLSU -> InstTypeCtrl.Values(InstTypeCtrl.LSU),
    InstTypeCtrl.isBRU -> InstTypeCtrl.Values(InstTypeCtrl.BRU),
  )

  override def genTable(op: InstructionPattern): BitPat = {
    BitPat(op.nameMatch(map, 0.U(InstTypeCtrl.getWidth.W)))
  }
}
