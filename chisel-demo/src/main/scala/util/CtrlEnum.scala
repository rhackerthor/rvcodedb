package mq.util

import chisel3._
import chisel3.util._

// VisualDecoder 在 generate_ctrl_enum=true 时导出的基类,
// 支持 Binary / OneHot / Gray 三种编码
object CtrlEnum extends Enumeration {
  type enumType = Value
  val Binary, OneHot, Gray = Value
}

abstract class CtrlEnum(mode: CtrlEnum.enumType) {
  private var counter = 0
  private var valuesList = Seq.empty[Int]

  def BinarytoGray(binary: Int): Int = binary ^ (binary >> 1)

  def BinarytoOneHot(binary: Int): Int = 1 << binary

  def Value: Int = {
    val value = mode match {
      case CtrlEnum.Binary => counter
      case CtrlEnum.OneHot => BinarytoOneHot(counter)
      case CtrlEnum.Gray   => BinarytoGray(counter)
    }
    valuesList :+= value
    counter += 1
    counter - 1
  }

  def Values: Seq[UInt] = valuesList.map(v => v.U(getWidth.W))

  def getWidth: Int = {
    if (valuesList.isEmpty) 0
    else
      mode match {
        case CtrlEnum.Binary => log2Ceil(valuesList.size)
        case CtrlEnum.OneHot => valuesList.size
        case CtrlEnum.Gray   => log2Ceil(valuesList.size)
      }
  }

  object Mux {
    def apply[T <: Data](key: UInt, default: T)(mapping: Seq[T]): T = {
      require(mapping.length <= valuesList.length, "Seq has too many members")
      require(mapping.length >= valuesList.length, "Seq has too few members")

      mode match {
        case CtrlEnum.OneHot =>
          Mux1H((0 until Values.size).map(i => key(i) -> mapping(i)))
        case _ =>
          MuxLookup(key, default)(Values.zip(mapping))
      }
    }
  }

  object PriorityMux {
    def apply[T <: Data](key: UInt, default: T)(mapping: Seq[T]): T = {
      require(mapping.length <= valuesList.length, "Seq has too many members")
      require(mapping.length >= valuesList.length, "Seq has too few members")
      require(mode == CtrlEnum.OneHot, "only OneHot encode can use this apply")

      chisel3.util.PriorityMux(
        (0 until Values.size).map(i => key(i) -> mapping(i))
      )
    }
  }
}
