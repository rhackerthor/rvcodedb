from PyQt6.QtWidgets import (
    QDialog, QFormLayout,
    QLineEdit, QComboBox, QDialogButtonBox,
)


class NewProfileDialog(QDialog):
    def __init__(self, parent=None, name: str = "", output_path: str = "",
                 package_name: str = "mq.util.decoder"):
        super().__init__(parent)
        self.setWindowTitle("新建 Profile")
        self.setMinimumWidth(400)

        layout = QFormLayout(self)

        self._name_edit = QLineEdit(name)
        layout.addRow("名称:", self._name_edit)

        self._output_edit = QLineEdit(output_path)
        layout.addRow("输出路径:", self._output_edit)

        self._package_edit = QLineEdit(package_name)
        layout.addRow("包名:", self._package_edit)

        btns = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        layout.addRow(btns)

        self._name_edit.setFocus()

    def get_values(self) -> tuple:
        return (
            self._name_edit.text().strip(),
            self._output_edit.text().strip(),
            self._package_edit.text().strip(),
        )


class NewDecoderDialog(QDialog):
    def __init__(self, parent=None, name: str = "", mode: str = "OneHot"):
        super().__init__(parent)
        self.setWindowTitle("新建 Decoder")
        self.setMinimumWidth(300)

        layout = QFormLayout(self)

        self._name_edit = QLineEdit(name)
        layout.addRow("名称:", self._name_edit)

        self._mode_combo = QComboBox()
        self._mode_combo.addItems(["OneHot", "Binary", "Gray"])
        self._mode_combo.setCurrentText(mode)
        layout.addRow("编码模式:", self._mode_combo)

        btns = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        layout.addRow(btns)

        self._name_edit.setFocus()

    def get_values(self) -> tuple:
        return (self._name_edit.text().strip(), self._mode_combo.currentText())


class NewGroupDialog(QDialog):
    def __init__(self, parent=None, name: str = ""):
        super().__init__(parent)
        self.setWindowTitle("新建分组")
        self.setMinimumWidth(250)

        layout = QFormLayout(self)

        self._name_edit = QLineEdit(name)
        layout.addRow("分组名称:", self._name_edit)

        btns = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        layout.addRow(btns)

        self._name_edit.setFocus()

    def get_name(self) -> str:
        return self._name_edit.text().strip()
