package rv.util.decoder

import scala.io.Source
import scala.util.{Try, Using}

class DBReader(filePath: String) {
  private val source = Source.fromFile(filePath)

  def instsNum: Int = source.getLines().length

  def getDB(): Seq[InstructionPattern] = {
    source.getLines().map(line => {
      val parts = line.split(" ")
      require(line.size >= 2, s"Invalid database entry: $line")
      InstructionPattern(
        name      = parts.apply(0),
        extension = parts.apply(1),
        encode    = parts.apply(2),
        args      = parts.slice(3, parts.length - 1).toSeq
      )
    }).toSeq
  }

  def printAll(): Unit = {
    getDB.foreach(println)
  }

  def close(): Unit = {
    source.close()
  }
}
