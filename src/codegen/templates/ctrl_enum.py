CTRL_ENUM_TEMPLATE = """package %PACKAGE%

import chisel3._
import chisel3.util._
import mq.util.CtrlEnum
import chisel3.util.experimental.decode._

// === CtrlEnum ===
object %NAME%Ctrl extends CtrlEnum(CtrlEnum.%MODE%) {
%GROUPS_VALS%

%GROUPS_DEFS%
}

// === DecodeField ===
object %NAME%Field extends DecodeField[InstructionPattern, UInt] {
  override def name: String = "%NAME%Field"
  override def chiselType: UInt = UInt(%NAME%Ctrl.getWidth.W)

  private def map: Seq[(Seq[String], UInt)] = Seq(
%MAP_ENTRIES%
  )

  override def genTable(op: InstructionPattern): BitPat = {
    BitPat(op.nameMatch(map, 0.U(%NAME%Ctrl.getWidth.W)))
  }
}
"""

GROUP_VAL_TEMPLATE = """  val %GROUP_NAME% = Value"""

GROUP_DEF_TEMPLATE = """  def is%GROUP_NAME%: Seq[String] = Seq(
%INSTRUCTIONS%
  )"""

INSTR_LINE_TEMPLATE = """    "%INSTR%","""

MAP_ENTRY_TEMPLATE = """    %NAME%Ctrl.is%GROUP_NAME% -> %NAME%Ctrl.Values(%NAME%Ctrl.%GROUP_NAME%),"""

DECODER_FIELDS_TEMPLATE = """package %PACKAGE%

import chisel3._
import chisel3.util._
import chisel3.util.experimental.decode._

object DecodeFields {
  def all: Seq[DecodeField[InstructionPattern, UInt]] = {
    Seq(
%FIELD_LIST%
    )
  }
}
"""
