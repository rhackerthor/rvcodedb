package rv.util.decoder.filed

import chisel3._
import chisel3.util._
import chisel3.util.experimental.decode._

import rv.util.decoder.InstructionPattern
import rv.util.decoder.ctrl.InstTypeCtrl

object InstTypeField extends DecodeField[InstructionPattern, UInt] {
  override def name: String = "InstTypeField"
  override def chiselType: UInt = UInt(InstTypeCtrl.getWidth.W)
  private def map: Seq[(Seq[String], UInt)] = Seq(
    InstTypeCtrl.isALU -> InstTypeCtrl.Values(InstTypeCtrl.ALU),
    InstTypeCtrl.isMUL -> InstTypeCtrl.Values(InstTypeCtrl.MUL),
    InstTypeCtrl.isDEV -> InstTypeCtrl.Values(InstTypeCtrl.DEV),
    InstTypeCtrl.isBRU -> InstTypeCtrl.Values(InstTypeCtrl.BRU),
    InstTypeCtrl.isLSU -> InstTypeCtrl.Values(InstTypeCtrl.LSU),
    InstTypeCtrl.isCSU -> InstTypeCtrl.Values(InstTypeCtrl.CSU)
  )
  override def genTable(op: InstructionPattern): BitPat = {
    BitPat(op.nameMatch(map, 0.U(InstTypeCtrl.getWidth.W)))
  }
}
