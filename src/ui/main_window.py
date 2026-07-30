from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QSplitter,
    QMenuBar, QMenu, QMessageBox, QStatusBar, QApplication,
    QFileDialog,
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QAction
from pathlib import Path
import os

from src.models.profile import Profile, Decoder, Group
from src.models.profile_manager import (
    list_profile_names, load_profile, save_profile,
    delete_profile, copy_profile, rename_profile,
)
from src.utils.config import load_global_config, save_global_config
from src.utils.instruction_loader import (
    load_instructions, get_available_extensions,
    get_instructions_by_extensions, Instruction,
    get_resolved_opcodes_path,
    get_available_variable_fields, filter_instructions_by_fields,
)
from src.codegen.template import generate_decoder_code, export_to_files
from src.ui.themes import THEMES
from src.ui.instruction_panel import InstructionPanel
from src.ui.group_editor import GroupEditorPanel
from src.ui.code_preview import CodePreviewPanel
from src.ui.dialogs import (
    NewProfileDialog, NewDecoderDialog,
    NewGroupDialog, RenameDialog,
)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VisualDecoder")
        self.setMinimumSize(1200, 700)

        self._profile: Profile | None = None
        self._current_decoder_idx: int = -1
        self._all_instructions: list[Instruction] = []
        self._filtered_instructions: list[Instruction] = []
        self._selected_variable_fields: list[str] = []
        self._search_text: str = ""
        self._dirty: bool = False

        global_cfg = load_global_config()
        self._theme = global_cfg.get("theme", "night")
        self._opcodes_path = global_cfg.get("riscv_opcodes_path", "./riscv-opcodes")

        self._project_root = Path(__file__).resolve().parent.parent.parent

        self._setup_ui()
        self._setup_menu()
        self._apply_theme()

        self._connect_signals()
        self._load_initial_state()

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        self._instruction_panel = InstructionPanel()
        self._group_editor = GroupEditorPanel()
        self._code_preview = CodePreviewPanel()

        splitter.addWidget(self._instruction_panel)
        splitter.addWidget(self._group_editor)
        splitter.addWidget(self._code_preview)

        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 2)
        splitter.setStretchFactor(2, 3)

        layout = QHBoxLayout(central)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.addWidget(splitter)

        self.setStatusBar(QStatusBar())
        self.statusBar().showMessage("就绪")

    def _setup_menu(self):
        menubar = self.menuBar()

        file_menu = menubar.addMenu("文件")
        save_action = QAction("保存 Profile\tCtrl+S", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self._on_save_profile)
        file_menu.addAction(save_action)

        export_action = QAction("导出代码", self)
        export_action.triggered.connect(self._on_export_code)
        file_menu.addAction(export_action)

        file_menu.addSeparator()

        opcodes_action = QAction("选择指令数据库...", self)
        opcodes_action.triggered.connect(self._on_select_opcodes_path)
        file_menu.addAction(opcodes_action)

        file_menu.addSeparator()

        exit_action = QAction("退出", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        view_menu = menubar.addMenu("视图")
        theme_action = QAction("切换主题 (暗/亮)", self)
        theme_action.triggered.connect(self._on_toggle_theme)
        view_menu.addAction(theme_action)

        help_menu = menubar.addMenu("帮助")
        about_action = QAction("关于", self)
        about_action.triggered.connect(self._on_about)
        help_menu.addAction(about_action)

    def _connect_signals(self):
        ip = self._instruction_panel
        ip.extension_filter_changed.connect(self._on_extension_filter_changed)
        ip.field_filter_changed.connect(self._on_field_filter_changed)
        ip.search_text_changed.connect(self._on_search_text_changed)
        ip.instruction_assigned.connect(self._on_instruction_assigned)
        ip.batch_assign_requested.connect(self._on_batch_assign)
        ip.unassign_visible_requested.connect(self._on_unassign_visible)
        ip.clear_all_requested.connect(self._on_clear_all)

        ge = self._group_editor
        ge.profile_selected.connect(self._on_profile_selected)
        ge.profile_create.connect(self._on_profile_create)
        ge.profile_delete.connect(self._on_profile_delete)
        ge.profile_copy.connect(self._on_profile_copy)
        ge.profile_name_changed.connect(self._on_profile_name_changed)

        ge.decoder_selected.connect(self._on_decoder_selected)
        ge.decoder_create.connect(self._on_decoder_create)
        ge.decoder_delete.connect(self._on_decoder_delete)
        ge.decoder_mode_changed.connect(self._on_decoder_mode_changed)
        ge.decoder_name_changed.connect(self._on_decoder_name_changed)

        ge.group_selected.connect(self._on_group_selected)
        ge.group_create.connect(self._on_group_create)
        ge.group_delete.connect(self._on_group_delete)
        ge.group_rename.connect(self._on_group_rename)
        ge.group_move_up.connect(self._on_group_move_up)
        ge.group_move_down.connect(self._on_group_move_down)

        ge.save_requested.connect(self._on_save_profile)
        ge.output_path_browse.connect(self._on_output_browse)
        ge.export_requested.connect(self._on_export_code)

        cp = self._code_preview
        cp.get_export_button().clicked.connect(self._on_export_code)

    def _load_initial_state(self):
        self._all_instructions = load_instructions(
            self._opcodes_path, self._project_root
        )

        extensions = get_available_extensions(self._all_instructions)
        self._instruction_panel.set_extensions(extensions, [])

        var_fields = get_available_variable_fields(self._all_instructions)
        self._instruction_panel.set_variable_fields(var_fields, [])

        profile_names = list_profile_names()
        self._group_editor.set_profile_list(profile_names)

        global_cfg = load_global_config()
        last_profile = global_cfg.get("last_profile", "")
        if last_profile and last_profile in profile_names:
            self._load_profile(last_profile)
        elif profile_names:
            self._load_profile(profile_names[0])

    def _apply_theme(self):
        qss = THEMES.get(self._theme, THEMES["night"])
        self.setStyleSheet(qss)

    def _update_status(self):
        db_path = get_resolved_opcodes_path(self._opcodes_path, self._project_root)
        if self._profile:
            saved = "已保存" if not self._dirty else "未保存"
            msg = (
                f"Profile: {self._profile.name} [{saved}]"
                f" | 输出: {self._profile.output_path}"
                f" | 指令库: {db_path}"
                f" | 主题: {'暗色' if self._theme == 'night' else '亮色'}"
            )
        else:
            msg = f"指令库: {db_path} | 主题: {'暗色' if self._theme == 'night' else '亮色'}"
        self.statusBar().showMessage(msg)

    def _refresh_all(self):
        self._refresh_group_editor()
        self._refresh_instruction_panel()
        self._refresh_code_preview()
        self._update_status()

    def _refresh_group_editor(self):
        ge = self._group_editor
        if not self._profile:
            ge.set_profile_fields("", "", "")
            ge.set_decoder_list([], -1)
            ge.set_groups([], -1)
            return

        ge.set_profile_fields(
            self._profile.name,
            self._profile.output_path,
            self._profile.package_name,
        )

        decoder_names = [d.name for d in self._profile.decoders]
        ge.set_decoder_list(decoder_names, self._current_decoder_idx)

        decoder = self._get_current_decoder()
        if decoder:
            ge.set_decoder_fields(decoder.name, decoder.ctrl_enum_mode)
            group_names = [g.name for g in decoder.groups]
            ge.set_groups(group_names)
        else:
            ge.set_decoder_fields("", "OneHot")
            ge.set_groups([], -1)

    def _refresh_instruction_panel(self):
        ip = self._instruction_panel

        extensions = get_available_extensions(self._all_instructions)
        selected = self._profile.selected_extensions if self._profile else []
        ip.set_extensions(extensions, selected)

        var_fields = get_available_variable_fields(self._all_instructions)
        ip.set_variable_fields(var_fields, self._selected_variable_fields)

        decoder = self._get_current_decoder()
        group_names = [g.name for g in decoder.groups] if decoder else []
        assignments = self._get_assignments()

        ip.set_instructions(self._filtered_instructions, group_names, assignments)

    def _refresh_code_preview(self):
        decoder = self._get_current_decoder()
        if decoder and self._profile:
            code = generate_decoder_code(self._profile, decoder)
            self._code_preview.set_code(code)
        else:
            self._code_preview.set_code("// 请选择 Decoder 以预览代码")

    def _get_current_decoder(self) -> Decoder | None:
        if (self._profile and
                0 <= self._current_decoder_idx < len(self._profile.decoders)):
            return self._profile.decoders[self._current_decoder_idx]
        return None

    def _get_assignments(self) -> dict[str, str]:
        result = {}
        decoder = self._get_current_decoder()
        if decoder:
            for group in decoder.groups:
                for instr in group.instructions:
                    result[instr] = group.name
        return result

    def _load_profile(self, name: str):
        profile = load_profile(name)
        if profile is None:
            return

        self._profile = profile
        self._current_decoder_idx = 0 if profile.decoders else -1
        self._dirty = False

        if profile.selected_extensions:
            self._instruction_panel.set_extensions(
                get_available_extensions(self._all_instructions),
                profile.selected_extensions,
            )
        self._apply_filters()

        cfg = load_global_config()
        cfg["last_profile"] = name
        save_global_config(cfg)

        self._group_editor.set_profile_list(
            list_profile_names(), name
        )
        self._refresh_all()

    def _on_profile_selected(self, name: str):
        if not name:
            return
        self._load_profile(name)

    def _on_profile_create(self):
        dlg = NewProfileDialog(self)
        if dlg.exec() == NewProfileDialog.DialogCode.Accepted:
            name, output_path, pkg = dlg.get_values()
            if not name:
                QMessageBox.warning(self, "错误", "Profile 名称不能为空")
                return

            existing = list_profile_names()
            if name in existing:
                QMessageBox.warning(self, "错误", f"Profile '{name}' 已存在")
                return

            profile = Profile(
                name=name, output_path=output_path, package_name=pkg
            )
            save_profile(profile)

            names = list_profile_names()
            self._group_editor.set_profile_list(names, name)
            self._load_profile(name)

    def _on_profile_delete(self, name: str):
        if not name:
            return
        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除 Profile '{name}' 吗？",
        )
        if reply == QMessageBox.StandardButton.Yes:
            delete_profile(name)
            self._profile = None
            self._current_decoder_idx = -1

            names = list_profile_names()
            self._group_editor.set_profile_list(names, "")
            self._refresh_all()

    def _on_profile_copy(self, name: str):
        if not name:
            return
        dlg = NewProfileDialog(
            self, name=f"{name}_copy",
            output_path=self._profile.output_path if self._profile else "",
            package_name=self._profile.package_name if self._profile else "mq.util.decoder",
        )
        if dlg.exec() == NewProfileDialog.DialogCode.Accepted:
            new_name, output_path, pkg = dlg.get_values()
            if not new_name:
                return
            if new_name in list_profile_names():
                QMessageBox.warning(self, "错误", f"Profile '{new_name}' 已存在")
                return

            new_profile = copy_profile(name, new_name)
            if new_profile:
                names = list_profile_names()
                self._group_editor.set_profile_list(names, new_name)
                self._load_profile(new_name)

    def _on_profile_name_changed(self, text: str):
        if self._profile and text and text != self._profile.name:
            old_name = self._profile.name
            if rename_profile(old_name, text):
                self._profile.name = text
                self._group_editor.set_profile_list(list_profile_names(), text)
                cfg = load_global_config()
                if cfg.get("last_profile") == old_name:
                    cfg["last_profile"] = text
                    save_global_config(cfg)
                self._dirty = True
                self._update_status()

    def _on_save_profile(self):
        if not self._profile:
            self.statusBar().showMessage("请先选择或创建一个 Profile")
            return

        name, output_path, pkg = self._group_editor.get_profile_fields()
        self._profile.name = name
        self._profile.output_path = output_path
        self._profile.package_name = pkg

        selected = self._instruction_panel.get_selected_extensions()
        self._profile.selected_extensions = selected

        decoder = self._get_current_decoder()
        if decoder:
            dname, dmode = self._group_editor.get_decoder_fields()
            decoder.name = dname
            decoder.ctrl_enum_mode = dmode

        for dec in self._profile.decoders:
            conflicts = dec.validate_no_duplicates()
            if conflicts:
                self.statusBar().showMessage(
                    f"保存失败: Decoder '{dec.name}' 存在重复指令"
                )
                return

        if output_path and not Path(output_path).exists():
            Path(output_path).mkdir(parents=True, exist_ok=True)

        save_profile(self._profile)
        self._dirty = False
        self._update_status()

    def _on_export_code(self):
        if not self._profile:
            self.statusBar().showMessage("请先选择一个 Profile")
            return

        self._on_save_profile()

        if not self._profile.output_path:
            self.statusBar().showMessage("请先设置输出路径")
            return

        output_dir = Path(self._profile.output_path)
        if not output_dir.exists():
            output_dir.mkdir(parents=True, exist_ok=True)

        chisel_path = self._project_root / "riscv-opcodes" / "inst.chisel"
        written = export_to_files(self._profile, overwrite=True, chisel_path=chisel_path)
        if written:
            self.statusBar().showMessage(
                f"已导出 {len(written)} 个文件到: {output_dir}"
            )
        else:
            self.statusBar().showMessage("没有生成任何文件（可能没有 Decoder）")

    def _apply_filters(self):
        instructions = self._all_instructions

        selected_extensions = self._instruction_panel.get_selected_extensions()
        if selected_extensions:
            instructions = get_instructions_by_extensions(
                instructions, selected_extensions
            )

        if self._selected_variable_fields:
            instructions = filter_instructions_by_fields(
                instructions, self._selected_variable_fields
            )

        if self._search_text:
            text = self._search_text.upper()
            instructions = [i for i in instructions if text in i.name]

        self._filtered_instructions = instructions
        if self._profile:
            self._profile.selected_extensions = selected_extensions

    def _on_extension_filter_changed(self, selected: list[str]):
        self._apply_filters()

        decoder = self._get_current_decoder()
        group_names = [g.name for g in decoder.groups] if decoder else []
        assignments = self._get_assignments()
        self._instruction_panel.set_instructions(
            self._filtered_instructions, group_names, assignments
        )
        self._dirty = True
        self._update_status()
        self._update_search_count()

    def _on_field_filter_changed(self, selected: list[str]):
        self._selected_variable_fields = selected
        self._apply_filters()

        decoder = self._get_current_decoder()
        group_names = [g.name for g in decoder.groups] if decoder else []
        assignments = self._get_assignments()
        self._instruction_panel.set_instructions(
            self._filtered_instructions, group_names, assignments
        )
        self._update_search_count()

    def _on_search_text_changed(self, text: str):
        self._search_text = text
        self._apply_filters()

        decoder = self._get_current_decoder()
        group_names = [g.name for g in decoder.groups] if decoder else []
        assignments = self._get_assignments()
        self._instruction_panel.set_instructions(
            self._filtered_instructions, group_names, assignments
        )
        self._update_search_count()

    def _update_search_count(self):
        total = len(self._all_instructions)
        if not total:
            self._instruction_panel.set_search_count(0, 0)
            return
        ext_selected = self._instruction_panel.get_selected_extensions()
        if ext_selected:
            ext_filtered = get_instructions_by_extensions(self._all_instructions, ext_selected)
        else:
            ext_filtered = list(self._all_instructions)
        if self._selected_variable_fields:
            ext_filtered = filter_instructions_by_fields(ext_filtered, self._selected_variable_fields)
        visible = len(self._filtered_instructions)
        self._instruction_panel.set_search_count(visible, len(ext_filtered))

    def _on_instruction_assigned(self, instr_name: str, group_name: str):
        decoder = self._get_current_decoder()
        if not decoder:
            return
        decoder.assign_instruction(instr_name, group_name if group_name else None)
        self._dirty = True
        self._update_status()
        self._refresh_code_preview()

    def _on_batch_assign(self, target_group: str):
        decoder = self._get_current_decoder()
        if not decoder:
            return
        for instr in self._filtered_instructions:
            decoder.assign_instruction(instr.name, target_group)
        self._dirty = True
        self._update_status()
        self._refresh_instruction_panel()
        self._refresh_code_preview()

    def _on_unassign_visible(self):
        decoder = self._get_current_decoder()
        if not decoder:
            return
        for instr in self._filtered_instructions:
            decoder.assign_instruction(instr.name, None)
        self._dirty = True
        self._update_status()
        self._refresh_instruction_panel()
        self._refresh_code_preview()

    def _on_clear_all(self):
        decoder = self._get_current_decoder()
        if not decoder:
            return
        for group in decoder.groups:
            group.instructions.clear()
        self._dirty = True
        self._update_status()
        self._refresh_instruction_panel()
        self._refresh_code_preview()

    def _on_decoder_selected(self, idx: int):
        self._current_decoder_idx = idx
        decoder = self._get_current_decoder()
        if decoder:
            self._group_editor.set_decoder_fields(
                decoder.name, decoder.ctrl_enum_mode
            )
            group_names = [g.name for g in decoder.groups]
            self._group_editor.set_groups(group_names, 0 if group_names else -1)
        else:
            self._group_editor.set_decoder_fields("", "OneHot")
            self._group_editor.set_groups([], -1)

        self._refresh_instruction_panel()
        self._refresh_code_preview()

    def _on_decoder_create(self):
        if not self._profile:
            QMessageBox.warning(self, "警告", "请先选择一个 Profile")
            return

        dlg = NewDecoderDialog(self)
        if dlg.exec() == NewDecoderDialog.DialogCode.Accepted:
            dname, dmode = dlg.get_values()
            if not dname:
                return
            existing = [d.name for d in self._profile.decoders]
            if dname in existing:
                QMessageBox.warning(self, "错误", f"Decoder '{dname}' 已存在")
                return

            self._profile.decoders.append(Decoder(name=dname, ctrl_enum_mode=dmode))
            self._current_decoder_idx = len(self._profile.decoders) - 1
            self._dirty = True
            self._update_status()
            self._refresh_group_editor()
            self._refresh_instruction_panel()
            self._refresh_code_preview()

    def _on_decoder_delete(self, idx: int):
        if not self._profile or idx < 0 or idx >= len(self._profile.decoders):
            return
        dname = self._profile.decoders[idx].name
        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除 Decoder '{dname}' 吗？"
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._profile.decoders.pop(idx)
            self._current_decoder_idx = min(idx, len(self._profile.decoders) - 1) if self._profile.decoders else -1
            self._dirty = True
            self._update_status()
            self._refresh_all()

    def _on_decoder_mode_changed(self, idx: int, mode: str):
        if self._profile and 0 <= idx < len(self._profile.decoders):
            self._profile.decoders[idx].ctrl_enum_mode = mode
            self._dirty = True
            self._update_status()
            self._refresh_code_preview()

    def _on_decoder_name_changed(self, idx: int, name: str):
        if self._profile and 0 <= idx < len(self._profile.decoders):
            self._profile.decoders[idx].name = name
            self._dirty = True
            self._update_status()
            self._refresh_group_editor()
            self._refresh_code_preview()

    def _on_group_selected(self, idx: int):
        decoder = self._get_current_decoder()
        if decoder and 0 <= idx < len(decoder.groups):
            self._group_editor._group_name_edit.setText(decoder.groups[idx].name)

    def _on_group_create(self):
        decoder = self._get_current_decoder()
        if not decoder:
            QMessageBox.warning(self, "警告", "请先选择一个 Decoder")
            return

        dlg = NewGroupDialog(self)
        if dlg.exec() == NewGroupDialog.DialogCode.Accepted:
            gname = dlg.get_name()
            if not gname:
                return
            existing = [g.name for g in decoder.groups]
            if gname in existing:
                QMessageBox.warning(self, "错误", f"分组 '{gname}' 已存在")
                return

            decoder.groups.append(Group(name=gname))
            group_names = [g.name for g in decoder.groups]
            self._group_editor.set_groups(group_names, len(group_names) - 1)
            self._dirty = True
            self._update_status()
            self._refresh_instruction_panel()
            self._refresh_code_preview()

    def _on_group_delete(self, idx: int):
        decoder = self._get_current_decoder()
        if not decoder or idx < 0 or idx >= len(decoder.groups):
            return
        gname = decoder.groups[idx].name
        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除分组 '{gname}' 吗？（其中的指令将变为未分配）"
        )
        if reply == QMessageBox.StandardButton.Yes:
            decoder.groups.pop(idx)
            new_idx = min(idx, len(decoder.groups) - 1) if decoder.groups else -1
            group_names = [g.name for g in decoder.groups]
            self._group_editor.set_groups(group_names, new_idx)
            self._dirty = True
            self._update_status()
            self._refresh_instruction_panel()
            self._refresh_code_preview()

    def _on_group_rename(self, idx: int, name: str):
        decoder = self._get_current_decoder()
        if not decoder or idx < 0 or idx >= len(decoder.groups) or not name:
            return
        decoder.groups[idx].name = name
        group_names = [g.name for g in decoder.groups]
        self._group_editor.set_groups(group_names, idx)
        self._dirty = True
        self._update_status()
        self._refresh_instruction_panel()
        self._refresh_code_preview()

    def _on_group_move_up(self, idx: int):
        decoder = self._get_current_decoder()
        if not decoder or idx <= 0:
            return
        decoder.reorder_group(idx, idx - 1)
        group_names = [g.name for g in decoder.groups]
        self._group_editor.set_groups(group_names, idx - 1)
        self._dirty = True
        self._update_status()
        self._refresh_instruction_panel()
        self._refresh_code_preview()

    def _on_group_move_down(self, idx: int):
        decoder = self._get_current_decoder()
        if not decoder or idx < 0 or idx >= len(decoder.groups) - 1:
            return
        decoder.reorder_group(idx, idx + 1)
        group_names = [g.name for g in decoder.groups]
        self._group_editor.set_groups(group_names, idx + 1)
        self._dirty = True
        self._update_status()
        self._refresh_instruction_panel()
        self._refresh_code_preview()

    def _on_output_browse(self):
        path = self._group_editor.browse_output_path()

    def _on_toggle_theme(self):
        self._theme = "day" if self._theme == "night" else "night"
        self._apply_theme()
        cfg = load_global_config()
        cfg["theme"] = self._theme
        save_global_config(cfg)
        self._update_status()

    def _on_select_opcodes_path(self):
        path = QFileDialog.getOpenFileName(
            self, "选择指令数据库文件",
            str(self._project_root),
            "JSON 文件 (instr_dict.json);;所有文件 (*)"
        )[0]
        if not path:
            return

        p = Path(path)
        if not p.exists():
            QMessageBox.warning(self, "错误", f"文件不存在: {path}")
            return

        if p.is_file():
            if p.name != "instr_dict.json":
                QMessageBox.warning(self, "警告", "所选文件不是 instr_dict.json，将继续尝试加载。")
            self._opcodes_path = str(p.parent)
        else:
            self._opcodes_path = str(p)

        cfg = load_global_config()
        cfg["riscv_opcodes_path"] = self._opcodes_path
        save_global_config(cfg)

        self._all_instructions = load_instructions(
            self._opcodes_path, self._project_root
        )

        self._selected_variable_fields = []

        if not self._all_instructions:
            QMessageBox.warning(
                self, "加载失败",
                f"在路径 '{self._opcodes_path}' 中未找到 instr_dict.json，\n"
                f"请选择正确的指令数据库目录。"
            )
            self._filtered_instructions = []
        else:
            self._apply_filters()

        self._refresh_all()
        self._update_status()

    def _on_about(self):
        QMessageBox.about(
            self, "关于 VisualDecoder",
            "VisualDecoder - 可视化 Chisel Decoder 代码生成器\n\n"
            "通过可视化界面将 RISC-V 指令与独热码/二进制/格雷码信号进行映射，\n"
            "并自动生成 Chisel 硬件解码器代码。\n\n"
            "基于 PyQt6"
        )
