from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QTreeWidget, QTreeWidgetItem, QCheckBox,
    QComboBox, QLabel, QScrollArea, QPushButton,
    QLineEdit,
)
from PyQt6.QtCore import Qt, pyqtSignal

from src.utils.instruction_loader import Instruction


class InstructionPanel(QWidget):
    extension_filter_changed = pyqtSignal(list)
    field_filter_changed = pyqtSignal(list)
    search_text_changed = pyqtSignal(str)
    instruction_assigned = pyqtSignal(str, str)
    batch_assign_requested = pyqtSignal(str)
    unassign_visible_requested = pyqtSignal()
    clear_all_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._all_instructions: list[Instruction] = []
        self._ext_to_checkboxes: dict[str, QCheckBox] = {}
        self._field_to_checkboxes: dict[str, QCheckBox] = {}
        self._instr_to_combo: dict[str, QComboBox] = {}

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        ext_group = QGroupBox("RISC-V 扩展筛选")
        ext_layout = QVBoxLayout(ext_group)

        ext_scroll = QScrollArea()
        ext_scroll.setWidgetResizable(True)
        self._ext_container = QWidget()
        self._ext_container_layout = QVBoxLayout(self._ext_container)
        self._ext_container_layout.setContentsMargins(0, 0, 0, 0)
        self._ext_container_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        ext_scroll.setWidget(self._ext_container)
        self._ext_container.setAutoFillBackground(False)
        ext_scroll.setMaximumHeight(150)
        ext_layout.addWidget(ext_scroll)
        layout.addWidget(ext_group)

        field_group = QGroupBox("变量字段筛选")
        field_layout = QVBoxLayout(field_group)

        field_scroll = QScrollArea()
        field_scroll.setWidgetResizable(True)
        self._field_container = QWidget()
        self._field_container_layout = QVBoxLayout(self._field_container)
        self._field_container_layout.setContentsMargins(0, 0, 0, 0)
        self._field_container_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        field_scroll.setWidget(self._field_container)
        self._field_container.setAutoFillBackground(False)
        field_scroll.setMaximumHeight(120)
        field_layout.addWidget(field_scroll)
        layout.addWidget(field_group)

        batch_group = QGroupBox("批量操作")
        batch_layout = QVBoxLayout(batch_group)
        batch_row1 = QHBoxLayout()
        batch_row1.addWidget(QLabel("批量分配到:"))
        self._batch_combo = QComboBox()
        self._batch_combo.addItem("(选择分组)")
        batch_row1.addWidget(self._batch_combo, 1)
        self._batch_btn = QPushButton("批量分配")
        batch_row1.addWidget(self._batch_btn)
        batch_layout.addLayout(batch_row1)
        batch_row2 = QHBoxLayout()
        self._select_all_btn = QPushButton("全选分配")
        batch_row2.addWidget(self._select_all_btn)
        self._unassign_visible_btn = QPushButton("取消分配")
        batch_row2.addWidget(self._unassign_visible_btn)
        self._clear_all_btn = QPushButton("全部取消")
        batch_row2.addWidget(self._clear_all_btn)
        batch_layout.addLayout(batch_row2)
        layout.addWidget(batch_group)

        search_layout = QHBoxLayout()
        self._search_edit = QLineEdit()
        self._search_edit.setPlaceholderText("搜索指令...")
        self._search_edit.setClearButtonEnabled(True)
        search_layout.addWidget(self._search_edit)
        self._search_count_label = QLabel("")
        search_layout.addWidget(self._search_count_label)
        layout.addLayout(search_layout)

        instr_group = QGroupBox("指令列表")
        instr_layout = QVBoxLayout(instr_group)

        self._tree = QTreeWidget()
        self._tree.setHeaderLabels(["指令", "分组"])
        self._tree.setColumnWidth(0, 100)
        self._tree.setAlternatingRowColors(False)
        self._tree.setRootIsDecorated(False)
        instr_layout.addWidget(self._tree)
        layout.addWidget(instr_group)

        self._batch_btn.clicked.connect(self._on_batch_assign)
        self._select_all_btn.clicked.connect(self._on_select_all)
        self._unassign_visible_btn.clicked.connect(self.unassign_visible_requested.emit)
        self._clear_all_btn.clicked.connect(self.clear_all_requested.emit)
        self._search_edit.textChanged.connect(self._on_search_text_changed)

    def _on_ext_toggled(self):
        selected = [ext for ext, cb in self._ext_to_checkboxes.items() if cb.isChecked()]
        self.extension_filter_changed.emit(selected)

    def _on_field_toggled(self):
        selected = [f for f, cb in self._field_to_checkboxes.items() if cb.isChecked()]
        self.field_filter_changed.emit(selected)

    def _on_search_text_changed(self, text: str):
        self.search_text_changed.emit(text)

    def _on_group_combo_changed(self, instr_name: str, combo: QComboBox):
        text = combo.currentText()
        group_name = text if text != "(未分配)" else ""
        self.instruction_assigned.emit(instr_name, group_name)

    def _on_batch_assign(self):
        target = self._batch_combo.currentText()
        if target and target != "(选择分组)":
            self.batch_assign_requested.emit(target)

    def _on_select_all(self):
        target = self._batch_combo.currentText()
        if not target or target == "(选择分组)":
            return
        for combo in self._instr_to_combo.values():
            combo.setCurrentText(target)

    def set_extensions(self, extensions: list[str], selected: list[str]):
        for cb in list(self._ext_to_checkboxes.values()):
            self._ext_container_layout.removeWidget(cb)
            cb.deleteLater()
        self._ext_to_checkboxes.clear()

        selected_set = set(selected)
        for ext in extensions:
            cb = QCheckBox(ext)
            cb.setChecked(ext in selected_set)
            cb.toggled.connect(self._on_ext_toggled)
            self._ext_to_checkboxes[ext] = cb
            self._ext_container_layout.addWidget(cb)

    def set_variable_fields(self, fields: list[str], selected: list[str]):
        for cb in list(self._field_to_checkboxes.values()):
            self._field_container_layout.removeWidget(cb)
            cb.deleteLater()
        self._field_to_checkboxes.clear()

        selected_set = set(selected)
        for f in fields:
            cb = QCheckBox(f)
            cb.setChecked(f in selected_set)
            cb.toggled.connect(self._on_field_toggled)
            self._field_to_checkboxes[f] = cb
            self._field_container_layout.addWidget(cb)

    def get_selected_extensions(self) -> list[str]:
        return [ext for ext, cb in self._ext_to_checkboxes.items() if cb.isChecked()]

    def get_selected_fields(self) -> list[str]:
        return [f for f, cb in self._field_to_checkboxes.items() if cb.isChecked()]

    def set_search_count(self, visible: int, total: int):
        if visible == total:
            self._search_count_label.setText(f"共 {total} 条")
        else:
            self._search_count_label.setText(f"{visible} / {total} 条")

    def set_instructions(self, instructions: list[Instruction],
                         group_names: list[str], assignments: dict[str, str]):
        self._tree.clear()
        self._instr_to_combo.clear()

        for instr in instructions:
            item = QTreeWidgetItem(self._tree)
            item.setText(0, instr.name)
            item.setToolTip(0, ", ".join(instr.variable_fields))

            combo = QComboBox()
            combo.addItem("(未分配)")
            for gname in group_names:
                combo.addItem(gname)
            current_group = assignments.get(instr.name, "")
            if current_group and current_group in group_names:
                combo.setCurrentText(current_group)
            else:
                combo.setCurrentIndex(0)

            combo.currentTextChanged.connect(
                lambda text, name=instr.name, c=combo: self._on_group_combo_changed(name, c)
            )
            self._tree.setItemWidget(item, 1, combo)
            self._instr_to_combo[instr.name] = combo

        self._rebuild_batch_combo(group_names)

    def _rebuild_batch_combo(self, group_names: list[str]):
        self._batch_combo.blockSignals(True)
        self._batch_combo.clear()
        self._batch_combo.addItem("(选择分组)")
        for gname in group_names:
            self._batch_combo.addItem(gname)
        self._batch_combo.blockSignals(False)
