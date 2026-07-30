from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QPushButton, QComboBox, QLabel, QLineEdit,
    QListWidget, QListWidgetItem, QMessageBox,
    QFileDialog,
)
from PyQt6.QtCore import Qt, pyqtSignal


class GroupEditorPanel(QWidget):
    profile_selected = pyqtSignal(str)
    profile_create = pyqtSignal()
    profile_delete = pyqtSignal(str)
    profile_copy = pyqtSignal(str)
    profile_name_changed = pyqtSignal(str)

    decoder_selected = pyqtSignal(int)
    decoder_create = pyqtSignal()
    decoder_delete = pyqtSignal(int)
    decoder_mode_changed = pyqtSignal(int, str)
    decoder_name_changed = pyqtSignal(int, str)

    group_selected = pyqtSignal(int)
    group_create = pyqtSignal()
    group_delete = pyqtSignal(int)
    group_rename = pyqtSignal(int, str)
    group_move_up = pyqtSignal(int)
    group_move_down = pyqtSignal(int)

    save_requested = pyqtSignal()
    output_path_browse = pyqtSignal()
    export_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_decoder_idx = -1

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        profile_group = QGroupBox("Profile")
        profile_layout = QVBoxLayout(profile_group)

        profile_row1 = QHBoxLayout()
        profile_row1.addWidget(QLabel("配置:"))
        self._profile_combo = QComboBox()
        self._profile_combo.setMinimumWidth(120)
        profile_row1.addWidget(self._profile_combo, 1)
        self._profile_new_btn = QPushButton("+")
        self._profile_new_btn.setFixedWidth(30)
        self._profile_delete_btn = QPushButton("x")
        self._profile_delete_btn.setFixedWidth(30)
        self._profile_copy_btn = QPushButton("cp")
        self._profile_copy_btn.setFixedWidth(30)
        profile_row1.addWidget(self._profile_new_btn)
        profile_row1.addWidget(self._profile_delete_btn)
        profile_row1.addWidget(self._profile_copy_btn)
        profile_layout.addLayout(profile_row1)

        profile_row2 = QHBoxLayout()
        profile_row2.addWidget(QLabel("名称:"))
        self._profile_name_edit = QLineEdit()
        profile_row2.addWidget(self._profile_name_edit, 1)
        profile_layout.addLayout(profile_row2)

        profile_row3 = QHBoxLayout()
        profile_row3.addWidget(QLabel("包名:"))
        self._package_edit = QLineEdit()
        profile_row3.addWidget(self._package_edit, 1)
        profile_layout.addLayout(profile_row3)

        profile_row4 = QHBoxLayout()
        profile_row4.addWidget(QLabel("输出:"))
        self._output_edit = QLineEdit()
        profile_row4.addWidget(self._output_edit, 1)
        self._output_browse_btn = QPushButton("...")
        self._output_browse_btn.setFixedWidth(30)
        profile_row4.addWidget(self._output_browse_btn)
        profile_layout.addLayout(profile_row4)

        profile_btns = QHBoxLayout()
        self._save_btn = QPushButton("保存 Profile")
        self._export_btn = QPushButton("导出代码")
        profile_btns.addWidget(self._save_btn)
        profile_btns.addWidget(self._export_btn)
        profile_layout.addLayout(profile_btns)

        layout.addWidget(profile_group)

        decoder_group = QGroupBox("Decoder")
        decoder_layout = QVBoxLayout(decoder_group)

        decoder_row1 = QHBoxLayout()
        decoder_row1.addWidget(QLabel("解码器:"))
        self._decoder_combo = QComboBox()
        decoder_row1.addWidget(self._decoder_combo, 1)
        self._decoder_new_btn = QPushButton("+")
        self._decoder_new_btn.setFixedWidth(30)
        self._decoder_delete_btn = QPushButton("x")
        self._decoder_delete_btn.setFixedWidth(30)
        decoder_row1.addWidget(self._decoder_new_btn)
        decoder_row1.addWidget(self._decoder_delete_btn)
        decoder_layout.addLayout(decoder_row1)

        decoder_row2 = QHBoxLayout()
        decoder_row2.addWidget(QLabel("名称:"))
        self._decoder_name_edit = QLineEdit()
        decoder_row2.addWidget(self._decoder_name_edit, 1)
        decoder_layout.addLayout(decoder_row2)

        decoder_row3 = QHBoxLayout()
        decoder_row3.addWidget(QLabel("模式:"))
        self._mode_combo = QComboBox()
        self._mode_combo.addItems(["OneHot", "Binary", "Gray"])
        decoder_row3.addWidget(self._mode_combo, 1)
        decoder_layout.addLayout(decoder_row3)

        layout.addWidget(decoder_group)

        group_group = QGroupBox("分组")
        group_layout = QVBoxLayout(group_group)

        self._group_list = QListWidget()
        group_layout.addWidget(self._group_list)

        group_btn_row = QHBoxLayout()
        self._group_new_btn = QPushButton("+ 新建")
        self._group_delete_btn = QPushButton("删除")
        self._group_up_btn = QPushButton("↑")
        self._group_up_btn.setFixedWidth(30)
        self._group_down_btn = QPushButton("↓")
        self._group_down_btn.setFixedWidth(30)
        group_btn_row.addWidget(self._group_new_btn)
        group_btn_row.addWidget(self._group_delete_btn)
        group_btn_row.addStretch()
        group_btn_row.addWidget(self._group_up_btn)
        group_btn_row.addWidget(self._group_down_btn)
        group_layout.addLayout(group_btn_row)

        group_edit_row = QHBoxLayout()
        group_edit_row.addWidget(QLabel("名称:"))
        self._group_name_edit = QLineEdit()
        group_edit_row.addWidget(self._group_name_edit, 1)
        group_layout.addLayout(group_edit_row)

        group_btn_row2 = QHBoxLayout()
        self._group_rename_btn = QPushButton("重命名")
        group_btn_row2.addWidget(self._group_rename_btn)
        group_btn_row2.addStretch()
        group_layout.addLayout(group_btn_row2)

        layout.addWidget(group_group)
        layout.addStretch()

        self._profile_combo.currentTextChanged.connect(
            lambda t: self.profile_selected.emit(t) if t else None
        )
        self._profile_new_btn.clicked.connect(self.profile_create.emit)
        self._profile_delete_btn.clicked.connect(
            lambda: self.profile_delete.emit(self._profile_combo.currentText())
        )
        self._profile_copy_btn.clicked.connect(
            lambda: self.profile_copy.emit(self._profile_combo.currentText())
        )
        self._profile_name_edit.textChanged.connect(self.profile_name_changed.emit)

        self._decoder_combo.currentIndexChanged.connect(self.decoder_selected.emit)
        self._decoder_new_btn.clicked.connect(self.decoder_create.emit)
        self._decoder_delete_btn.clicked.connect(
            lambda: self.decoder_delete.emit(self._decoder_combo.currentIndex())
        )
        self._mode_combo.currentTextChanged.connect(
            lambda t: self.decoder_mode_changed.emit(
                self._decoder_combo.currentIndex(), t
            )
        )
        self._decoder_name_edit.textChanged.connect(
            lambda t: self.decoder_name_changed.emit(
                self._decoder_combo.currentIndex(), t
            )
        )

        self._group_list.currentRowChanged.connect(self.group_selected.emit)
        self._group_new_btn.clicked.connect(self.group_create.emit)
        self._group_delete_btn.clicked.connect(
            lambda: self.group_delete.emit(self._group_list.currentRow())
        )
        self._group_rename_btn.clicked.connect(
            lambda: self.group_rename.emit(
                self._group_list.currentRow(),
                self._group_name_edit.text(),
            )
        )
        self._group_up_btn.clicked.connect(
            lambda: self.group_move_up.emit(self._group_list.currentRow())
        )
        self._group_down_btn.clicked.connect(
            lambda: self.group_move_down.emit(self._group_list.currentRow())
        )

        self._save_btn.clicked.connect(self.save_requested.emit)
        self._output_browse_btn.clicked.connect(self.output_path_browse.emit)
        self._export_btn.clicked.connect(self.export_requested.emit)

    def set_profile_list(self, names: list[str], current: str = ""):
        self._profile_combo.blockSignals(True)
        self._profile_combo.clear()
        self._profile_combo.addItems(names)
        if current and current in names:
            self._profile_combo.setCurrentText(current)
        self._profile_combo.blockSignals(False)

    def set_profile_fields(self, name: str, output_path: str, package_name: str):
        self._profile_name_edit.blockSignals(True)
        self._output_edit.blockSignals(True)
        self._package_edit.blockSignals(True)
        self._profile_name_edit.setText(name)
        self._output_edit.setText(output_path)
        self._package_edit.setText(package_name)
        self._profile_name_edit.blockSignals(False)
        self._output_edit.blockSignals(False)
        self._package_edit.blockSignals(False)

    def get_profile_fields(self) -> tuple:
        return (
            self._profile_name_edit.text(),
            self._output_edit.text(),
            self._package_edit.text(),
        )

    def set_decoder_list(self, names: list[str], current_idx: int = -1):
        self._decoder_combo.blockSignals(True)
        self._decoder_combo.clear()
        self._decoder_combo.addItems(names)
        if current_idx >= 0 and current_idx < len(names):
            self._decoder_combo.setCurrentIndex(current_idx)
        self._decoder_combo.blockSignals(False)
        self._current_decoder_idx = current_idx

    def set_decoder_fields(self, name: str, mode: str):
        self._decoder_name_edit.blockSignals(True)
        self._mode_combo.blockSignals(True)
        self._decoder_name_edit.setText(name)
        self._mode_combo.setCurrentText(mode)
        self._decoder_name_edit.blockSignals(False)
        self._mode_combo.blockSignals(False)

    def get_decoder_fields(self) -> tuple:
        return self._decoder_name_edit.text(), self._mode_combo.currentText()

    def set_groups(self, group_names: list[str], select_idx: int = -1):
        self._group_list.blockSignals(True)
        self._group_list.clear()
        for gname in group_names:
            self._group_list.addItem(gname)
        if select_idx >= 0 and select_idx < len(group_names):
            self._group_list.setCurrentRow(select_idx)
        self._group_list.blockSignals(False)

    def get_group_count(self) -> int:
        return self._group_list.count()

    def browse_output_path(self) -> str:
        path = QFileDialog.getExistingDirectory(self, "选择输出目录")
        if path:
            self._output_edit.setText(path)
        return path
