from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPlainTextEdit,
    QPushButton, QGroupBox, QApplication,
)

from src.ui.syntax_highlighter import ScalaHighlighter


class CodePreviewPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._code = ""

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        header = QGroupBox("代码预览")
        header_layout = QVBoxLayout(header)

        btn_layout = QHBoxLayout()
        self._copy_btn = QPushButton("复制到剪贴板")
        self._export_btn = QPushButton("导出 .scala 文件")
        btn_layout.addWidget(self._copy_btn)
        btn_layout.addWidget(self._export_btn)
        btn_layout.addStretch()
        header_layout.addLayout(btn_layout)

        self._editor = QPlainTextEdit()
        self._editor.setReadOnly(True)
        self._editor.setTabStopDistance(20)
        self._highlighter = ScalaHighlighter(self._editor.document())
        header_layout.addWidget(self._editor)

        layout.addWidget(header)

        self._copy_btn.clicked.connect(self._on_copy)

    def set_code(self, code: str):
        self._code = code
        self._editor.setPlainText(code)

    def _on_copy(self):
        QApplication.clipboard().setText(self._code)

    def get_export_button(self):
        return self._export_btn
