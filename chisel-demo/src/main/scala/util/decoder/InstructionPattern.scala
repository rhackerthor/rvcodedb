package mq.util.decoder

import chisel3._
import chisel3.util._
import chisel3.util.experimental.decode._

case class InstructionPattern(
    name: String,
    code: BitPat,
) extends DecodePattern {
  override def bitPat: BitPat = code

  // 按指令名查找所属分组的编码值,找不到则返回默认值
  def nameMatch[T <: Data](
    map: Seq[(Seq[String], T)],
    default: T
  ): T = {
    map.view
      .collectFirst { case (set, enumType) if (set.contains(name)) => enumType }
      .getOrElse(default)
  }
}
