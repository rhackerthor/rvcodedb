package rv

import _root_.circt.stage.ChiselStage
import chisel3._
import chisel3.util._

import rv.util.decoder

object Main extends App {
  val firtoolOptions = Array(
    // 不显示注释
    "-disable-all-randomization",
    "-strip-debug-info",
    // 以符合verilog-2005的格式输出
    "--lowering-options=" + List(
      // make yosys happy
      // see https://github.com/llvm/circt/blob/main/docs/VerilogGeneration.md
      "disallowLocalVariables",
      "disallowPackedArrays",
      "locationInfoStyle=wrapInAtSquareBracket"
    ).reduce(_ + "," + _)
  )
  ChiselStage.emitSystemVerilogFile(
    new IDU,
    args,
    firtoolOptions
  )
}
