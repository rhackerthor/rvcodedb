package rv.util.decoder

import chisel3._
import chisel3.util._
import chisel3.util.experimental.decode._

import rv.util.decoder.filed._

case class InstructionPattern(
    name: String,
    extension: String,
    encode: String,
    args: Seq[String]
) extends DecodePattern {
  override def bitPat: BitPat = BitPat("b" + encode)
  // fileds
  def opcode: String = encode.reverse.substring( 6,  0).reverse
  def rd    : String = encode.reverse.substring(11,  7).reverse
  def funct3: String = encode.reverse.substring(14, 12).reverse
  def rs1   : String = encode.reverse.substring(19, 15).reverse
  def rs2   : String = encode.reverse.substring(24, 20).reverse
  def fucnt7: String = encode.reverse.substring(31, 25).reverse
  def csr   : String = encode.reverse.substring(31, 20).reverse
  // match enum type
  def nameMatch[T <: Data](
      map: Seq[(Seq[String], T)],
      default: T
  ): T = {
    map.view
      .collectFirst { case (set, enumType) if (set.contains(name)) => enumType }
      .getOrElse(default)
  }
}

object Decoder {
  def getFields() = Seq(
    InstTypeField,
  )

  def getDB(filePath: String): Seq[InstructionPattern] = {
    val reader = new DBReader(filePath)
    reader.getDB()
  }
}
