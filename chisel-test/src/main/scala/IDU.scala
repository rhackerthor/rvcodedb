package rv

import chisel3._
import chisel3.util._
import chisel3.util.experimental.decode._

import rv.util.decoder._
import rv.util.decoder.ctrl._
import rv.util.decoder.filed._

class IDU extends Module {
  val io = IO(new Bundle {
    val in = Input(UInt(32.W))
    val out = Output(UInt(InstTypeCtrl.getWidth.W))
  })
  val decodeDB: String = "/home/rhacker/Code/XingXing/rvcodedb/chisel-test/src/main/resources/rvdb/riscv-opcode.db"
  val decodeTable = new DecodeTable(Decoder.getDB(decodeDB), Decoder.getFields())
  val decodeResult = decodeTable.decode(io.in)
  io.out := decodeResult(InstTypeField)
}
