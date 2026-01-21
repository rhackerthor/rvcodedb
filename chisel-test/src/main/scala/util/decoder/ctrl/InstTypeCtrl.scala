package rv.util.decoder.ctrl

import chisel3._
import chisel3.util._
import rv.util.CtrlEnum

object InstTypeCtrl extends CtrlEnum(CtrlEnum.OneHot) {
  val ALU, MUL, DEV, LSU, BRU, CSU = Value

  def isALU: Seq[String] = Seq(
    "add", "addi", "and", "andi",
    // TODO: add other instructions
  )

  def isMUL: Seq[String] = Seq(
    "mul", "mulh", "mulhsu", "mulhu",
  )

  def isDEV: Seq[String] = Seq(
    "rem", "remu", "div", "divu"
  )

  def isLSU: Seq[String] = Seq(
    "lb", "lbu", "lh",
    // TODO: add other instructions
  )

  def isBRU: Seq[String] = Seq(
    "beg", "jal"
    // TODO: add other instructions
  )

  def isCSU: Seq[String] = Seq(
    "csrrc"
    // TODO: add other instructions
  )
}
