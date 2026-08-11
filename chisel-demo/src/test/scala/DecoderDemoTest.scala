package demo

import chisel3._
import chisel3.simulator.scalatest.ChiselSim
import org.scalatest.freespec.AnyFreeSpec
import org.scalatest.matchers.must.Matchers

// 硬件仿真验证:解码 ADD/SUB/LW/BEQ/SLL/SRA,检查类型与 ALU 结果
class DecoderDemoTest extends AnyFreeSpec with Matchers with ChiselSim {

  "ADD 解码为 ALU 且 aluRes = a + b" in {
    simulate(new DecoderDemo) { dut =>
      dut.io.inst.poke("h00000033".U) // add x0, x0, x0
      dut.io.a.poke(3.U)
      dut.io.b.poke(5.U)
      dut.io.isALU.expect(true.B)
      dut.io.isAdd.expect(true.B)
      dut.io.aluRes.expect(8.U)
    }
  }

  "SUB 解码为 ALU 且 aluRes = a - b" in {
    simulate(new DecoderDemo) { dut =>
      dut.io.inst.poke("h40000033".U) // sub x0, x0, x0
      dut.io.a.poke(5.U)
      dut.io.b.poke(3.U)
      dut.io.isALU.expect(true.B)
      dut.io.aluRes.expect(2.U)
    }
  }

  "LW 解码为 LSU" in {
    simulate(new DecoderDemo) { dut =>
      dut.io.inst.poke("h00002003".U) // lw x0, 0(x0)
      dut.io.isLSU.expect(true.B)
      dut.io.isALU.expect(false.B)
      dut.io.aluRes.expect(0.U) // LSU 指令无 ALU 操作
    }
  }

  "BEQ 解码为 BRU" in {
    simulate(new DecoderDemo) { dut =>
      dut.io.inst.poke("h00000063".U) // beq x0, x0, 0
      dut.io.isBRU.expect(true.B)
      dut.io.isALU.expect(false.B)
    }
  }

  "SLL 解码为 ALU 且 aluRes = a << b" in {
    simulate(new DecoderDemo) { dut =>
      dut.io.inst.poke("h00001033".U) // sll x0, x0, x0
      dut.io.a.poke(1.U)
      dut.io.b.poke(4.U)
      dut.io.aluRes.expect(16.U)
    }
  }

  "SRA 解码为 ALU 且 aluRes = a >> b (算术右移)" in {
    simulate(new DecoderDemo) { dut =>
      dut.io.inst.poke("h40005033".U) // sra x0, x0, x0
      dut.io.a.poke("hfffffff8".U)    // -8
      dut.io.b.poke(1.U)
      dut.io.aluRes.expect("hfffffffc".U) // -4
    }
  }
}
