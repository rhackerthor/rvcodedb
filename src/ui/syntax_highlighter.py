import re
from PyQt6.QtCore import QRegularExpression
from PyQt6.QtGui import QSyntaxHighlighter, QTextCharFormat, QFont, QColor


class ScalaHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._rules = []

        keyword_fmt = QTextCharFormat()
        keyword_fmt.setForeground(QColor("#9e8bc0"))
        keyword_fmt.setFontWeight(QFont.Weight.Bold)
        keywords = [
            "object", "class", "trait", "val", "var", "def", "override",
            "extends", "with", "import", "package", "private", "protected",
            "sealed", "abstract", "final", "implicit", "lazy", "type",
            "new", "this", "super", "return", "throw", "try", "catch",
            "finally", "if", "else", "match", "case", "for", "while", "do",
            "yield", "true", "false", "null", "=>", "<-", "_",
        ]
        for word in keywords:
            pattern = QRegularExpression(f"\\b{word}\\b")
            self._rules.append((pattern, keyword_fmt))

        type_fmt = QTextCharFormat()
        type_fmt.setForeground(QColor("#7d8ab5"))
        types = [
            "Int", "Long", "Float", "Double", "Boolean", "String", "Char",
            "Byte", "Short", "Unit", "Nothing", "Any", "Seq", "List", "Map",
            "Set", "Option", "Either", "Try", "Future", "UInt", "Bool",
            "SInt", "Vec", "Bundle", "DecodeField", "InstructionPattern",
            "BitPat", "CtrlEnum",
        ]
        for t in types:
            pattern = QRegularExpression(f"\\b{t}\\b")
            self._rules.append((pattern, type_fmt))

        string_fmt = QTextCharFormat()
        string_fmt.setForeground(QColor("#7db8a0"))
        self._rules.append((QRegularExpression("\"[^\"]*\""), string_fmt))

        number_fmt = QTextCharFormat()
        number_fmt.setForeground(QColor("#c4906a"))
        self._rules.append((QRegularExpression("\\b0[xX][0-9a-fA-F]+\\b"), number_fmt))
        self._rules.append((QRegularExpression("\\b\\d+\\.?\\d*[Lf]?\\b"), number_fmt))

        comment_fmt = QTextCharFormat()
        comment_fmt.setForeground(QColor("#56576a"))
        self._rules.append((QRegularExpression("//[^\n]*"), comment_fmt))

        annotation_fmt = QTextCharFormat()
        annotation_fmt.setForeground(QColor("#b09868"))
        self._rules.append((QRegularExpression("@\\w+"), annotation_fmt))

        member_fmt = QTextCharFormat()
        member_fmt.setForeground(QColor("#7d9eb5"))
        self._rules.append((QRegularExpression("\\b\\w+(?=\\()"), member_fmt))

    def highlightBlock(self, text):
        for pattern, fmt in self._rules:
            it = pattern.globalMatch(text)
            while it.hasNext():
                match = it.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), fmt)
