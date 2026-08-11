import demo.DecoderDemo
import _root_.circt.stage.ChiselStage

object Main extends App {
  ChiselStage.emitSystemVerilogFile(
    new DecoderDemo,
    args,
    firtoolOpts = Array("--lowering-options=disallowLocalVariables")
  )
  println("Verilog 已生成: build/DecoderDemo.sv")
}
