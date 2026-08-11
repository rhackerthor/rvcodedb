package mq.util.decoder

import chisel3._
import chisel3.util._
import chisel3.util.experimental.decode._

// 聚合文件:所有 Field 汇总,供 DecodeTable 使用
object DecodeFields {
  def all(): Seq[DecodeField[InstructionPattern, UInt]] = Seq(
    InstTypeField,
    ALUOpField,
  )
}
