import re
from pathlib import Path


def _parse_inst_chisel(chisel_path: Path) -> list[tuple[str, str]]:
    """Parse inst.chisel and return list of (type_name, map_content) pairs."""
    text = chisel_path.read_text(encoding="utf-8")

    start = text.find("object Instructions {")
    if start == -1:
        return []
    end = text.find("\n}", start)
    if end == -1:
        return []
    body = text[start:end + 2]

    groups: list[tuple[str, str]] = []
    for m in re.finditer(r"val (\w+Type) = Map\(", body):
        type_name = m.group(1)
        map_start = m.end()

        depth = 1
        pos = map_start
        while pos < len(body) and depth > 0:
            if body[pos] == '(':
                depth += 1
            elif body[pos] == ')':
                depth -= 1
            pos += 1
        map_body = body[map_start:pos - 1]
        groups.append((type_name, map_body.rstrip()))

    return groups


INSTRUCTION_PATTERN_TEMPLATE = """case class InstructionPattern(
    name: String,
    code: BitPat,
) extends DecodePattern {
  override def bitPat: BitPat = code
  def nameMatch[T <: Data](
    map: Seq[(Seq[String], T)],
    default: T
  ): T = {
    map.view
      .collectFirst { case (set, enumType) if (set.contains(name)) => enumType }
      .getOrElse(default)
  }
}
"""


def generate_insts_scala_from_chisel(
    chisel_path: Path,
    package_name: str = "mq.util.decoder",
) -> str:
    groups = _parse_inst_chisel(chisel_path)

    lines = [f"package {package_name}", ""]
    lines += [
        "import chisel3._",
        "import chisel3.util._",
        "import chisel3.util.experimental.decode._",
        "",
    ]

    lines.append(INSTRUCTION_PATTERN_TEMPLATE)
    lines.append("object Instructions {")

    type_names = []
    for type_name, map_body in groups:
        type_names.append(type_name)
        lines.append(f"  val {type_name} = Map(")
        lines.append(map_body.lstrip("\n"))
        lines.append("  )")

    if type_names:
        lines.append("")
        lines.append("  def db(): Seq[InstructionPattern] = {")
        lines.append("    val insts = ")
        lines.append("      " + " ++\n      ".join(type_names))
        lines.append(
            '    val seq = insts.map { case (name, code) => {\n'
            '      InstructionPattern(name, code)\n'
            '    }}.toSeq\n'
            '    seq'
        )
        lines.append("  }")
        lines.append(
            '  def print() = {\n'
            '    db().foreach(i => {\n'
            '      println(i.name, i.code.toString)\n'
            '    })\n'
            '  }\n'
        )

    lines.append("}")
    return "\n".join(lines) + "\n"
