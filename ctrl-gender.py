#!/usr/bin/env python3
"""
RISC-V 控制信号生成器
"""

import sys
import os
import json
import csv
import shutil
from pathlib import Path
from dataclasses import dataclass, asdict, field
from typing import List, Dict, Any, Optional, Set, Tuple
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QTextEdit, QListWidget, QListWidgetItem,
    QComboBox, QTabWidget, QTreeWidget, QTreeWidgetItem, QSplitter,
    QGroupBox, QFormLayout, QMessageBox, QFileDialog, QDialog,
    QInputDialog, QDialogButtonBox, QScrollArea, QFrame, QCheckBox,
    QMenuBar, QMenu, QStatusBar, QToolBar, QTableWidget,
    QTableWidgetItem, QHeaderView, QPlainTextEdit
)
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QSettings
from PyQt6.QtGui import QFont, QFontDatabase, QIcon, QAction, QActionEvent, QColor, QPalette


# 数据类定义
@dataclass
class Instruction:
    name: str
    extension: str
    encode: str
    args: List[str]
    
    def __str__(self):
        return f"{self.name} ({self.extension}): {self.encode}"

@dataclass
class ControlSignal:
    name: str
    encoding_type: str  # OneHot, Binary, Gray
    width: int
    values: Dict[str, List[str]]
    created_at: str
    instructions: List[str]
    signal_id: str = field(default_factory=lambda: datetime.now().strftime("%Y%m%d_%H%M%S"))
    
    def to_dict(self):
        return {
            'name': self.name,
            'encoding_type': self.encoding_type,
            'width': self.width,
            'values': self.values,
            'created_at': self.created_at,
            'instructions': self.instructions,
            'signal_id': self.signal_id
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(**data)

class InstructionSelectDialog(QDialog):
    """指令选择对话框"""
    def __init__(self, parent=None, instructions=None, selected_instructions=None, 
                 disabled_instructions=None, value_mapping=None):
        super().__init__(parent)
        self.instructions = instructions or []
        self.selected_instructions = set(selected_instructions or [])
        self.disabled_instructions = set(disabled_instructions or [])
        self.value_mapping = value_mapping or {}  # 值到指令的映射：{指令名: [值名1, 值名2, ...]}
        
        self.setWindowTitle("选择指令")
        self.setModal(True)
        self.resize(600, 700)
        
        # 加载当前主题设置
        self.settings = QSettings("rvctrl-gender", "settings")
        self.current_theme = self.settings.value("current_theme", "light", type=str)
        
        self.apply_theme()
        
        self.init_ui()
        
    def apply_theme(self):
        """应用当前主题"""
        if self.current_theme == "dark":
            self.setStyleSheet(self.get_dark_theme())
        else:
            self.setStyleSheet(self.get_light_theme())
    
    def get_light_theme(self):
        """获取亮色主题样式表"""
        return """
            QDialog {
                background-color: #ffffff;
                color: #2c3e50;
            }
            QLabel {
                color: #2c3e50;
                font-weight: bold;
            }
            QLineEdit {
                background-color: #f8f9fa;
                color: #2c3e50;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                padding: 6px;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
            }
            QListWidget {
                background-color: #ffffff;
                color: #2c3e50;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                alternate-background-color: #f8f9fa;
            }
            QListWidget::item {
                padding: 6px;
                border-bottom: 1px solid #dee2e6;
            }
            QListWidget::item:selected {
                background-color: #3498db;
                color: #ffffff;
                font-weight: bold;
            }
            QListWidget::item:disabled {
                background-color: #f8f9fa;
                color: #95a5a6;
                border-left: 4px solid #f39c12;
            }
            QPushButton {
                background-color: #f8f9fa;
                color: #2c3e50;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e9ecef;
                border: 2px solid #3498db;
                color: #3498db;
            }
            QPushButton:pressed {
                background-color: #dee2e6;
            }
        """
    
    def get_dark_theme(self):
        """获取暗色主题样式表"""
        return """
            QDialog {
                background-color: #2d2d2d;
                color: #e0e0e0;
            }
            QLabel {
                color: #e0e0e0;
                font-weight: bold;
            }
            QLineEdit {
                background-color: #3c3c3c;
                color: #e0e0e0;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 6px;
            }
            QLineEdit:focus {
                border: 2px solid #4a9eff;
            }
            QListWidget {
                background-color: #3c3c3c;
                color: #e0e0e0;
                border: 1px solid #555555;
                border-radius: 4px;
                alternate-background-color: #333333;
            }
            QListWidget::item {
                padding: 6px;
                border-bottom: 1px solid #555555;
            }
            QListWidget::item:selected {
                background-color: #4a9eff;
                color: #ffffff;
                font-weight: bold;
            }
            QListWidget::item:disabled {
                background-color: #3c3c3c;
                color: #777777;
                border-left: 4px solid #ffa726;
            }
            QPushButton {
                background-color: #3c3c3c;
                color: #e0e0e0;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #4c4c4c;
                border: 2px solid #4a9eff;
                color: #4a9eff;
            }
            QPushButton:pressed {
                background-color: #2c2c2c;
            }
        """
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # 搜索框
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("🔍 搜索:"))
        self.search_edit = QLineEdit()
        self.search_edit.textChanged.connect(self.filter_instructions)
        self.search_edit.setPlaceholderText("输入指令名、指令集或编码进行搜索...")
        search_layout.addWidget(self.search_edit)
        layout.addLayout(search_layout)
        
        # 禁用指令提示
        if self.disabled_instructions:
            disabled_count = len(self.disabled_instructions)
            disabled_info = QLabel(f"⚠️ 有 {disabled_count} 条指令已被其他值使用，不可选择")
            if self.current_theme == "dark":
                disabled_info.setStyleSheet("color: #ffa726; font-weight: bold; padding: 5px; border: 1px solid #ffa726; border-radius: 4px; background-color: #3c3c3c;")
            else:
                disabled_info.setStyleSheet("color: #f39c12; font-weight: bold; padding: 5px; border: 1px solid #f39c12; border-radius: 4px; background-color: #f8f9fa;")
            layout.addWidget(disabled_info)
        
        # 指令列表
        self.list_widget = QListWidget()
        self.list_widget.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        self.populate_instruction_list()
        layout.addWidget(self.list_widget)
        
        # 按钮
        button_layout = QHBoxLayout()
        
        select_all_btn = QPushButton("全选")
        select_all_btn.clicked.connect(self.select_all)
        button_layout.addWidget(select_all_btn)
        
        clear_all_btn = QPushButton("取消全选")
        clear_all_btn.clicked.connect(self.clear_all)
        button_layout.addWidget(clear_all_btn)
        
        button_layout.addStretch()
        
        ok_btn = QPushButton("确定")
        ok_btn.clicked.connect(self.accept)
        button_layout.addWidget(ok_btn)
        
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def populate_instruction_list(self):
        """填充指令列表，显示更多信息"""
        self.list_widget.clear()
        for inst in self.instructions:
            # 创建显示文本：指令名 [指令集] 编码 (args)
            display_text = f"{inst.name} [{inst.extension}]"
            if inst.encode:
                # 缩短编码显示，只显示前20个字符，如果太长的话
                encode_display = inst.encode[:30] + "..." if len(inst.encode) > 30 else inst.encode
                display_text += f"\n编码: {encode_display}"
            if inst.args:
                args_str = " ".join(inst.args)
                display_text += f"\n参数: {args_str}"
            
            # 如果指令被禁用，添加绑定信息
            if inst.name in self.disabled_instructions:
                if inst.name in self.value_mapping:
                    bound_values = self.value_mapping[inst.name]
                    if bound_values:
                        bound_text = "、".join(bound_values[:3])  # 最多显示3个值
                        if len(bound_values) > 3:
                            bound_text += f" 等{len(bound_values)}个值"
                        display_text += f"\n🔒 已绑定到: {bound_text}"
            
            item = QListWidgetItem(display_text)
            item.setData(Qt.ItemDataRole.UserRole, inst.name)
            
            # 设置工具提示
            tooltip = f"指令: {inst.name}\n指令集: {inst.extension}\n编码: {inst.encode}\n参数: {' '.join(inst.args)}"
            if inst.name in self.disabled_instructions:
                if inst.name in self.value_mapping:
                    bound_values = self.value_mapping[inst.name]
                    if bound_values:
                        tooltip += f"\n\n❌ 此指令已绑定到以下值:\n"
                        for value_name in bound_values:
                            tooltip += f"  • {value_name}\n"
                    else:
                        tooltip += f"\n\n❌ 此指令已被其他值使用"
            item.setToolTip(tooltip)
            
            # 禁用已被其他值使用的指令
            if inst.name in self.disabled_instructions:
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEnabled)
                if self.current_theme == "dark":
                    item.setBackground(QColor("#3c3c3c"))
                    item.setForeground(QColor("#777777"))
                else:
                    item.setBackground(QColor("#f8f9fa"))
                    item.setForeground(QColor("#95a5a6"))
            
            self.list_widget.addItem(item)
            
            # 设置选中状态（只选中不在禁用列表中的指令）
            if inst.name in self.selected_instructions and inst.name not in self.disabled_instructions:
                item.setSelected(True)
    
    def filter_instructions(self, text):
        """过滤指令列表"""
        text = text.lower()
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            inst_name = item.data(Qt.ItemDataRole.UserRole).lower()
            item_text = item.text().lower()
            item.setHidden(text not in inst_name and text not in item_text)
    
    def select_all(self):
        """全选（跳过已禁用的指令）"""
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            if not item.isHidden() and item.flags() & Qt.ItemFlag.ItemIsEnabled:
                item.setSelected(True)
    
    def clear_all(self):
        """取消全选"""
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            item.setSelected(False)
    
    def get_selected_instructions(self):
        """获取选中的指令"""
        selected = []
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            if item.isSelected() and not item.isHidden():
                selected.append(item.data(Qt.ItemDataRole.UserRole))
        return selected

class ValueConfigWidget(QFrame):
    """值配置部件"""
    config_changed = pyqtSignal()
    
    def __init__(self, parent=None, value_name="", instructions=None):
        super().__init__(parent)
        self.instructions = instructions or []
        self.selected_instructions = []
        self.get_disabled_instructions_func = None  # 用于获取其他值已选指令的函数
        self.get_value_mapping_func = None  # 用于获取指令到值的映射函数
        
        self.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Raised)
        self.setLineWidth(2)
        
        # 加载当前主题设置
        self.settings = QSettings("rvctrl-gender", "settings")
        self.current_theme = self.settings.value("current_theme", "light", type=str)
        
        self.init_ui(value_name)
    
    def set_get_disabled_instructions_func(self, func):
        """设置获取其他值已选指令的函数"""
        self.get_disabled_instructions_func = func
    
    def set_get_value_mapping_func(self, func):
        """设置获取指令到值映射的函数"""
        self.get_value_mapping_func = func
    
    def init_ui(self, value_name):
        layout = QVBoxLayout()
        layout.setContentsMargins(12, 12, 12, 12)
        
        # 值名称
        name_layout = QHBoxLayout()
        name_label = QLabel("值名称:")
        name_label.setStyleSheet(self.get_label_style())
        name_layout.addWidget(name_label)
        self.name_edit = QLineEdit(value_name)
        self.name_edit.textChanged.connect(self.config_changed.emit)
        name_layout.addWidget(self.name_edit)
        layout.addLayout(name_layout)
        
        # 指令信息
        self.inst_label = QLabel("已选择 0 条指令")
        self.inst_label.setStyleSheet(self.get_count_style())
        layout.addWidget(self.inst_label)
        
        # 选择按钮
        self.select_btn = QPushButton("📋 选择指令...")
        self.select_btn.clicked.connect(self.select_instructions)
        layout.addWidget(self.select_btn)
        
        # 已选指令预览（最多显示5个）
        self.preview_label = QLabel("")
        self.preview_label.setWordWrap(True)
        self.preview_label.setStyleSheet(self.get_preview_style())
        layout.addWidget(self.preview_label)
        
        self.setLayout(layout)
        self.update_preview()
    
    def get_label_style(self):
        """获取标签样式"""
        if self.current_theme == "dark":
            return "color: #e0e0e0; font-weight: bold;"
        else:
            return "color: #2c3e50; font-weight: bold;"
    
    def get_count_style(self):
        """获取计数样式"""
        if self.current_theme == "dark":
            return "color: #4a9eff; font-size: 12px; font-weight: bold;"
        else:
            return "color: #3498db; font-size: 12px; font-weight: bold;"
    
    def get_preview_style(self):
        """获取预览样式"""
        if self.current_theme == "dark":
            return """
                color: #c0c0c0; 
                font-size: 11px; 
                padding: 8px;
                background-color: #3c3c3c;
                border-radius: 4px;
                border: 1px solid #555555;
            """
        else:
            return """
                color: #2c3e50; 
                font-size: 11px; 
                padding: 8px;
                background-color: #f8f9fa;
                border-radius: 4px;
                border: 1px solid #dee2e6;
            """
    
    def select_instructions(self):
        """打开指令选择对话框"""
        # 获取其他值已选的指令
        disabled_instructions = set()
        if self.get_disabled_instructions_func:
            disabled_instructions = self.get_disabled_instructions_func()
        
        # 获取指令到值的映射
        value_mapping = {}
        if self.get_value_mapping_func:
            value_mapping = self.get_value_mapping_func()
        
        # 过滤当前已选指令，移除已被其他值选中的指令
        filtered_selected = [inst for inst in self.selected_instructions 
                           if inst not in disabled_instructions]
        
        # 如果过滤后有变化，更新当前值
        if len(filtered_selected) != len(self.selected_instructions):
            self.selected_instructions = filtered_selected
            self.update_preview()
            self.config_changed.emit()
        
        dialog = InstructionSelectDialog(
            self,
            self.instructions,
            self.selected_instructions,
            disabled_instructions,
            value_mapping
        )
        
        if dialog.exec():
            new_selected = dialog.get_selected_instructions()
            
            # 检查是否有指令冲突
            conflict_instructions = set(new_selected) & disabled_instructions
            if conflict_instructions:
                # 获取冲突指令的绑定信息
                conflict_info = []
                for inst in conflict_instructions:
                    if inst in value_mapping:
                        bound_values = value_mapping[inst]
                        if bound_values:
                            bound_text = ", ".join(bound_values[:3])
                            if len(bound_values) > 3:
                                bound_text += f" 等{len(bound_values)}个值"
                            conflict_info.append(f"{inst} (已绑定到: {bound_text})")
                        else:
                            conflict_info.append(inst)
                    else:
                        conflict_info.append(inst)
                
                conflict_list = "\n".join(conflict_info[:3])
                if len(conflict_info) > 3:
                    conflict_list += f"\n... 等 {len(conflict_info)} 条指令"
                
                reply = QMessageBox.question(
                    self,
                    "指令冲突",
                    f"以下指令已被其他值使用:\n\n{conflict_list}\n\n是否要移除这些指令？",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                
                if reply == QMessageBox.StandardButton.Yes:
                    new_selected = [inst for inst in new_selected 
                                   if inst not in conflict_instructions]
                else:
                    return  # 保持原选择
            
            self.selected_instructions = new_selected
            self.update_preview()
            self.config_changed.emit()
    
    def update_preview(self):
        """更新预览"""
        count = len(self.selected_instructions)
        self.inst_label.setText(f"✅ 已选择 {count} 条指令")
        
        if count > 0:
            preview_text = ", ".join(self.selected_instructions[:5])
            if count > 5:
                preview_text += f" ... 等{count}条指令"
            self.preview_label.setText(preview_text)
        else:
            self.preview_label.setText("暂未选择指令")
    
    def get_config(self):
        """获取配置"""
        return {
            'name': self.name_edit.text().strip(),
            'instructions': self.selected_instructions.copy()
        }
    
    def set_config(self, name, instructions):
        """设置配置"""
        self.name_edit.setText(name)
        self.selected_instructions = instructions.copy()
        self.update_preview()
    
    def is_valid(self):
        """检查是否有效"""
        name = self.name_edit.text().strip()
        return bool(name)  # 修改为：只要名称不为空就有效，允许没有指令

class TemplateManagerDialog(QDialog):
    """模板管理对话框"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = QSettings("rvctrl-gender", "settings")
        
        self.setWindowTitle("Chisel代码模板管理")
        self.setModal(True)
        self.resize(900, 700)
        
        # 加载当前主题
        self.current_theme = self.settings.value("current_theme", "light", type=str)
        
        self.init_ui()
        self.load_templates()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # 创建标签页
        self.tab_widget = QTabWidget()
        
        # Ctrl模板标签页
        ctrl_tab = QWidget()
        ctrl_layout = QVBoxLayout()
        
        ctrl_desc_label = QLabel(
            "📝 Ctrl模板 - 控制信号枚举类模板\n"
            "使用以下占位符：\n"
            "  {signal_name} - 信号名称\n"
            "  {encoding_type} - 编码类型\n"
            "  {values_list} - 值定义列表\n"
            "  {methods_list} - 指令方法列表\n"
            "  {signal_width} - 信号宽度\n"
            "  {generation_time} - 生成时间"
        )
        ctrl_desc_label.setStyleSheet(self.get_desc_style())
        ctrl_layout.addWidget(ctrl_desc_label)
        
        self.ctrl_template_edit = QPlainTextEdit()
        self.ctrl_template_edit.setFont(QFont("Monospace", 11))
        self.ctrl_template_edit.setPlaceholderText("在此输入Ctrl类代码模板...")
        ctrl_layout.addWidget(self.ctrl_template_edit)
        
        # Ctrl模板按钮
        ctrl_btn_layout = QHBoxLayout()
        ctrl_default_btn = QPushButton("🔄 加载默认Ctrl模板")
        ctrl_default_btn.clicked.connect(self.load_default_ctrl_template)
        ctrl_btn_layout.addWidget(ctrl_default_btn)
        
        ctrl_save_btn = QPushButton("💾 保存Ctrl模板")
        ctrl_save_btn.clicked.connect(self.save_ctrl_template)
        ctrl_btn_layout.addWidget(ctrl_save_btn)
        
        ctrl_layout.addLayout(ctrl_btn_layout)
        ctrl_tab.setLayout(ctrl_layout)
        
        # Field模板标签页
        field_tab = QWidget()
        field_layout = QVBoxLayout()
        
        field_desc_label = QLabel(
            "📝 Field模板 - 解码字段类模板\n"
            "使用以下占位符：\n"
            "  {signal_name} - 信号名称\n"
            "  {encoding_type} - 编码类型\n"
            "  {signal_width} - 信号宽度\n"
            "  {values_list} - 值列表\n"
            "  {value_mappings} - 值映射列表\n"
            "  {generation_time} - 生成时间"
        )
        field_desc_label.setStyleSheet(self.get_desc_style())
        field_layout.addWidget(field_desc_label)
        
        self.field_template_edit = QPlainTextEdit()
        self.field_template_edit.setFont(QFont("Monospace", 11))
        self.field_template_edit.setPlaceholderText("在此输入Field类代码模板...")
        field_layout.addWidget(self.field_template_edit)
        
        # Field模板按钮
        field_btn_layout = QHBoxLayout()
        field_default_btn = QPushButton("🔄 加载默认Field模板")
        field_default_btn.clicked.connect(self.load_default_field_template)
        field_btn_layout.addWidget(field_default_btn)
        
        field_save_btn = QPushButton("💾 保存Field模板")
        field_save_btn.clicked.connect(self.save_field_template)
        field_btn_layout.addWidget(field_save_btn)
        
        field_layout.addLayout(field_btn_layout)
        field_tab.setLayout(field_layout)
        
        # 添加标签页
        self.tab_widget.addTab(ctrl_tab, "Ctrl模板")
        self.tab_widget.addTab(field_tab, "Field模板")
        
        layout.addWidget(self.tab_widget)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        # 示例按钮
        example_btn = QPushButton("📋 加载示例模板")
        example_btn.clicked.connect(self.load_example_templates)
        button_layout.addWidget(example_btn)
        
        button_layout.addStretch()
        
        # 应用按钮
        apply_btn = QPushButton("✅ 应用并关闭")
        apply_btn.clicked.connect(self.apply_and_close)
        button_layout.addWidget(apply_btn)
        
        # 取消按钮
        cancel_btn = QPushButton("❌ 取消")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def get_desc_style(self):
        """获取描述样式"""
        if self.current_theme == "dark":
            return """
                color: #e0e0e0; 
                background-color: #3c3c3c; 
                padding: 12px; 
                border-radius: 6px;
                border: 2px solid #555555;
                font-weight: bold;
                font-size: 13px;
            """
        else:
            return """
                color: #2c3e50; 
                background-color: #f8f9fa; 
                padding: 12px; 
                border-radius: 6px;
                border: 2px solid #dee2e6;
                font-weight: bold;
                font-size: 13px;
            """
    
    def load_templates(self):
        """加载模板"""
        # 加载Ctrl模板
        ctrl_template = self.settings.value("chisel_ctrl_template", "")
        if not ctrl_template:
            self.load_default_ctrl_template()
        else:
            self.ctrl_template_edit.setPlainText(ctrl_template)
        
        # 加载Field模板
        field_template = self.settings.value("chisel_field_template", "")
        if not field_template:
            self.load_default_field_template()
        else:
            self.field_template_edit.setPlainText(field_template)
    
    def load_default_ctrl_template(self):
        """加载默认Ctrl模板"""
        default_ctrl_template = """// ===========================================
// 自动生成的Chisel控制信号枚举类
// 生成时间: {generation_time}
// ===========================================

package rv.util.decoder

import chisel3._
import chisel3.util._
import rv.util.CtrlEnum

/**
  * {signal_name}Ctrl - 控制信号枚举类
  * 编码类型: {encoding_type}
  * 信号宽度: {signal_width} bits
  */
object {signal_name}Ctrl extends CtrlEnum(CtrlEnum.{encoding_type}) {
  // 值定义
{values_list}
  
  // 指令分类方法
{methods_list}
  
  // 辅助方法
  def getAllValues: Seq[UInt] = this.Values
  
  def getWidth: Int = this.getWidth
}"""
        self.ctrl_template_edit.setPlainText(default_ctrl_template)
    
    def load_default_field_template(self):
        """加载默认Field模板"""
        default_field_template = """package rv.util.decoder

import chisel3._
import chisel3.util._
import chisel3.util.experimental.decode._

object {signal_name}Field extends DecodeField[InstructionPattern, UInt] {
  override def name: String = "{signal_name}Field"
  override def chiselType: UInt = UInt({signal_name}Ctrl.getWidth.W)
  private def map: Seq[(Seq[String], UInt)] = Seq(
{value_mappings}
  )
  override def genTable(op: InstructionPattern): BitPat = {
    BitPat(op.nameMatch(map, 0.U({signal_name}Ctrl.getWidth.W)))
  }
}"""
        self.field_template_edit.setPlainText(default_field_template)
    
    def load_example_templates(self):
        """加载示例模板"""
        # 加载示例Ctrl模板
        example_ctrl_template = """// ===========================================
// 自动生成的Chisel控制信号枚举类
// 生成时间: {generation_time}
// ===========================================

package rv.util.decoder

import chisel3._
import chisel3.util._
import rv.util.CtrlEnum

/**
  * {signal_name}Ctrl - 控制信号枚举类
  * 编码类型: {encoding_type}
  * 信号宽度: {signal_width} bits
  */
object {signal_name}Ctrl extends CtrlEnum(CtrlEnum.{encoding_type}) {
  // 值定义
{values_list}
  
  // 指令分类方法
{methods_list}
  
  // 辅助方法
  def getAllValues: Seq[UInt] = this.Values
  
  def getWidth: Int = this.getWidth
  
  // 默认值
  def default: UInt = this.Values.head
  
  // 值到索引的映射
  def valueToIndex(value: UInt): Int = {
    this.Values.indexWhere(_ === value)
  }
}"""
        self.ctrl_template_edit.setPlainText(example_ctrl_template)
        
        # 加载示例Field模板
        example_field_template = """// ===========================================
// 自动生成的Chisel解码字段类
// 生成时间: {generation_time}
// ===========================================

package rv.util.decoder

import chisel3._
import chisel3.util._
import chisel3.util.experimental.decode._

/**
  * {signal_name}Field - 解码字段类
  * 信号宽度: {signal_width} bits
  */
object {signal_name}Field extends DecodeField[InstructionPattern, UInt] {
  override def name: String = "{signal_name}Field"
  override def chiselType: UInt = UInt({signal_name}Ctrl.getWidth.W)
  
  // 指令到值的映射表
  private def map: Seq[(Seq[String], UInt)] = Seq(
{value_mappings}
  )
  
  override def genTable(op: InstructionPattern): BitPat = {
    // 使用名称匹配生成对应的值
    BitPat(op.nameMatch(map, {signal_name}Ctrl.default))
  }
  
  // 辅助方法：获取所有可能的映射
  def getAllMappings: Seq[(Seq[String], UInt)] = map
}"""
        self.field_template_edit.setPlainText(example_field_template)
        
        QMessageBox.information(self, "提示", "已加载示例模板")
    
    def save_ctrl_template(self):
        """保存Ctrl模板"""
        template = self.ctrl_template_edit.toPlainText()
        self.settings.setValue("chisel_ctrl_template", template)
        self.settings.sync()
        QMessageBox.information(self, "成功", "Ctrl模板已保存！")
    
    def save_field_template(self):
        """保存Field模板"""
        template = self.field_template_edit.toPlainText()
        self.settings.setValue("chisel_field_template", template)
        self.settings.sync()
        QMessageBox.information(self, "成功", "Field模板已保存！")
    
    def save_templates(self):
        """保存所有模板"""
        self.save_ctrl_template()
        self.save_field_template()
    
    def apply_and_close(self):
        """应用并关闭"""
        self.save_templates()
        self.accept()
    
    def get_ctrl_template(self):
        """获取Ctrl模板"""
        return self.ctrl_template_edit.toPlainText()
    
    def get_field_template(self):
        """获取Field模板"""
        return self.field_template_edit.toPlainText()

class SettingsDialog(QDialog):
    """设置对话框"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = QSettings("rvctrl-gender", "settings")
        
        self.setWindowTitle("设置")
        self.setModal(True)
        self.resize(600, 500)
        
        # 加载当前主题
        self.current_theme = self.settings.value("current_theme", "light", type=str)
        
        self.init_ui()
        self.load_settings()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # 文件路径设置
        path_group = QGroupBox("文件路径设置")
        path_group.setStyleSheet(self.get_groupbox_style())
        path_layout = QFormLayout()
        
        # CSV文件路径
        csv_layout = QHBoxLayout()
        self.csv_edit = QLineEdit()
        csv_layout.addWidget(self.csv_edit)
        csv_btn = QPushButton("📂 浏览...")
        csv_btn.clicked.connect(self.browse_csv)
        csv_layout.addWidget(csv_btn)
        path_layout.addRow("📄 默认CSV文件:", csv_layout)
        
        # Ctrl文件保存路径
        ctrl_layout = QHBoxLayout()
        self.ctrl_edit = QLineEdit()
        ctrl_layout.addWidget(self.ctrl_edit)
        ctrl_btn = QPushButton("📂 浏览...")
        ctrl_btn.clicked.connect(lambda: self.browse_directory("ctrl"))
        ctrl_layout.addWidget(ctrl_btn)
        path_layout.addRow("💾 Ctrl保存路径:", ctrl_layout)
        
        # Field文件保存路径
        field_layout = QHBoxLayout()
        self.field_edit = QLineEdit()
        field_layout.addWidget(self.field_edit)
        field_btn = QPushButton("📂 浏览...")
        field_btn.clicked.connect(lambda: self.browse_directory("field"))
        field_layout.addWidget(field_btn)
        path_layout.addRow("💾 Field保存路径:", field_layout)
        
        path_group.setLayout(path_layout)
        layout.addWidget(path_group)
        
        # 代码生成设置
        code_group = QGroupBox("代码生成设置")
        code_group.setStyleSheet(self.get_groupbox_style())
        code_layout = QVBoxLayout()
        
        # 模板管理按钮
        template_btn = QPushButton("📝 管理Chisel代码模板...")
        template_btn.clicked.connect(self.manage_templates)
        template_btn.setToolTip("自定义生成的Chisel代码框架")
        code_layout.addWidget(template_btn)
        
        # 自动格式化代码
        self.auto_format_check = QCheckBox("自动格式化生成的代码")
        self.auto_format_check.setStyleSheet(self.get_checkbox_style())
        code_layout.addWidget(self.auto_format_check)
        
        # 自动生成Field文件
        self.auto_field_check = QCheckBox("自动生成Field文件")
        self.auto_field_check.setStyleSheet(self.get_checkbox_style())
        self.auto_field_check.setChecked(True)
        self.auto_field_check.setToolTip("生成Ctrl文件时自动生成对应的Field文件")
        code_layout.addWidget(self.auto_field_check)
        
        code_group.setLayout(code_layout)
        layout.addWidget(code_group)
        
        # 自动保存设置
        auto_group = QGroupBox("自动保存设置")
        auto_group.setStyleSheet(self.get_groupbox_style())
        auto_layout = QFormLayout()
        
        self.auto_save_check = QCheckBox("自动保存生成记录")
        self.auto_save_check.setStyleSheet(self.get_checkbox_style())
        auto_layout.addRow(self.auto_save_check)
        
        self.auto_load_check = QCheckBox("启动时自动加载默认CSV")
        self.auto_load_check.setStyleSheet(self.get_checkbox_style())
        auto_layout.addRow(self.auto_load_check)
        
        auto_group.setLayout(auto_layout)
        layout.addWidget(auto_group)
        
        # 按钮
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel |
            QDialogButtonBox.StandardButton.Apply
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        button_box.button(QDialogButtonBox.StandardButton.Apply).clicked.connect(self.apply_settings)
        
        layout.addWidget(button_box)
        self.setLayout(layout)
    
    def get_groupbox_style(self):
        """获取分组框样式"""
        if self.current_theme == "dark":
            return """
                QGroupBox {
                    font-weight: bold;
                    color: #e0e0e0;
                    border: 2px solid #555555;
                    border-radius: 6px;
                    margin-top: 12px;
                    padding-top: 12px;
                    background-color: #3c3c3c;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 12px;
                    padding: 0 6px 0 6px;
                    color: #4a9eff;
                }
            """
        else:
            return """
                QGroupBox {
                    font-weight: bold;
                    color: #2c3e50;
                    border: 2px solid #dee2e6;
                    border-radius: 6px;
                    margin-top: 12px;
                    padding-top: 12px;
                    background-color: #ffffff;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 12px;
                    padding: 0 6px 0 6px;
                    color: #3498db;
                }
            """
    
    def get_checkbox_style(self):
        """获取复选框样式"""
        if self.current_theme == "dark":
            return "color: #e0e0e0;"
        else:
            return "color: #2c3e50;"
    
    def browse_csv(self):
        """浏览CSV文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择CSV文件",
            self.csv_edit.text(),
            "CSV文件 (*.csv);;所有文件 (*.*)"
        )
        if file_path:
            self.csv_edit.setText(file_path)
    
    def browse_directory(self, dir_type):
        """浏览目录"""
        if dir_type == "ctrl":
            current_path = self.ctrl_edit.text()
        else:
            current_path = self.field_edit.text()
            
        dir_path = QFileDialog.getExistingDirectory(
            self,
            f"选择{dir_type.upper()}保存路径",
            current_path
        )
        if dir_path:
            if dir_type == "ctrl":
                self.ctrl_edit.setText(dir_path)
            else:
                self.field_edit.setText(dir_path)
    
    def manage_templates(self):
        """管理代码模板"""
        dialog = TemplateManagerDialog(self)
        dialog.exec()
    
    def load_settings(self):
        """加载设置"""
        self.csv_edit.setText(self.settings.value("default_csv", ""))
        
        # Ctrl文件保存路径
        ctrl_path = self.settings.value("ctrl_save_path", "")
        if not ctrl_path:
            ctrl_path = str(Path.home() / "riscv-scala" / "ctrl")
        self.ctrl_edit.setText(ctrl_path)
        
        # Field文件保存路径
        field_path = self.settings.value("field_save_path", "")
        if not field_path:
            field_path = str(Path.home() / "riscv-scala" / "field")
        self.field_edit.setText(field_path)
        
        self.auto_save_check.setChecked(self.settings.value("auto_save", True, type=bool))
        self.auto_load_check.setChecked(self.settings.value("auto_load", True, type=bool))
        self.auto_format_check.setChecked(self.settings.value("auto_format", True, type=bool))
        self.auto_field_check.setChecked(self.settings.value("auto_field", True, type=bool))
    
    def save_settings(self):
        """保存设置"""
        self.settings.setValue("default_csv", self.csv_edit.text())
        self.settings.setValue("ctrl_save_path", self.ctrl_edit.text())
        self.settings.setValue("field_save_path", self.field_edit.text())
        self.settings.setValue("auto_save", self.auto_save_check.isChecked())
        self.settings.setValue("auto_load", self.auto_load_check.isChecked())
        self.settings.setValue("auto_format", self.auto_format_check.isChecked())
        self.settings.setValue("auto_field", self.auto_field_check.isChecked())
        self.settings.sync()
    
    def apply_settings(self):
        """应用设置"""
        self.save_settings()
        QMessageBox.information(self, "成功", "设置已保存！")
    
    def accept(self):
        """确定按钮"""
        self.apply_settings()
        super().accept()

class RecordManagerDialog(QDialog):
    """记录管理器对话框"""
    record_selected = pyqtSignal(dict)  # 当选择编辑记录时发射
    
    def __init__(self, parent=None, generator=None):
        super().__init__(parent)
        self.generator = generator
        
        self.setWindowTitle("生成记录")
        self.setModal(True)
        self.resize(950, 650)
        
        # 加载当前主题
        self.settings = QSettings("rvctrl-gender", "settings")
        self.current_theme = self.settings.value("current_theme", "light", type=str)
        
        self.init_ui()
        self.load_records()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # 工具栏
        toolbar = QHBoxLayout()
        
        self.refresh_btn = QPushButton("🔄 刷新")
        self.refresh_btn.clicked.connect(self.load_records)
        toolbar.addWidget(self.refresh_btn)
        
        self.edit_btn = QPushButton("✏️ 编辑")
        self.edit_btn.clicked.connect(self.edit_record)
        toolbar.addWidget(self.edit_btn)
        
        self.delete_btn = QPushButton("🗑️ 删除")
        self.delete_btn.clicked.connect(self.delete_record)
        toolbar.addWidget(self.delete_btn)
        
        self.regenerate_btn = QPushButton("⚡ 重新生成代码")
        self.regenerate_btn.clicked.connect(self.regenerate_code)
        toolbar.addWidget(self.regenerate_btn)
        
        toolbar.addStretch()
        
        self.close_btn = QPushButton("❌ 关闭")
        self.close_btn.clicked.connect(self.reject)
        toolbar.addWidget(self.close_btn)
        
        layout.addLayout(toolbar)
        
        # 记录表格
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "ID", "名称", "编码类型", "宽度", "创建时间", 
            "指令数", "值数量"
        ])
        
        # 设置列宽
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)
        
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        
        layout.addWidget(self.table)
        
        # 详细信息
        detail_group = QGroupBox("详细信息")
        detail_group.setStyleSheet(self.get_groupbox_style())
        detail_layout = QVBoxLayout()
        
        self.detail_text = QTextEdit()
        self.detail_text.setReadOnly(True)
        self.detail_text.setMaximumHeight(160)
        detail_layout.addWidget(self.detail_text)
        
        detail_group.setLayout(detail_layout)
        layout.addWidget(detail_group)
        
        self.setLayout(layout)
        
        # 连接信号
        self.table.itemSelectionChanged.connect(self.show_details)
    
    def get_groupbox_style(self):
        """获取分组框样式"""
        if self.current_theme == "dark":
            return """
                QGroupBox {
                    font-weight: bold;
                    color: #e0e0e0;
                    border: 2px solid #555555;
                    border-radius: 6px;
                    margin-top: 12px;
                    padding-top: 12px;
                    background-color: #3c3c3c;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 12px;
                    padding: 0 6px 0 6px;
                    color: #4a9eff;
                }
            """
        else:
            return """
                QGroupBox {
                    font-weight: bold;
                    color: #2c3e50;
                    border: 2px solid #dee2e6;
                    border-radius: 6px;
                    margin-top: 12px;
                    padding-top: 12px;
                    background-color: #ffffff;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 12px;
                    padding: 0 6px 0 6px;
                    color: #3498db;
                }
            """
    
    def load_records(self):
        """加载记录 - 修改时间从近到远排序"""
        self.table.setRowCount(0)
        
        records = self.generator.load_records()
        
        # 按修改时间排序（从近到远）
        # 将字符串时间转换为datetime对象进行比较
        def parse_time(time_str):
            try:
                return datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
            except:
                return datetime.min
        
        # 按创建时间降序排序（最新的在前）
        records.sort(key=lambda x: parse_time(x.get('created_at', '')), reverse=True)
        
        for record in records:
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            # 填充数据
            self.table.setItem(row, 0, QTableWidgetItem(record.get('signal_id', '')))
            self.table.setItem(row, 1, QTableWidgetItem(record.get('name', '')))
            self.table.setItem(row, 2, QTableWidgetItem(record.get('encoding_type', '')))
            self.table.setItem(row, 3, QTableWidgetItem(str(record.get('width', 0))))
            self.table.setItem(row, 4, QTableWidgetItem(record.get('created_at', '')))
            self.table.setItem(row, 5, QTableWidgetItem(str(len(record.get('instructions', [])))))
            self.table.setItem(row, 6, QTableWidgetItem(str(len(record.get('values', {})))))
    
    def get_selected_record(self):
        """获取选中的记录"""
        selected_rows = self.table.selectedItems()
        if not selected_rows:
            return None
        
        row = selected_rows[0].row()
        record_id = self.table.item(row, 0).text()
        
        # 从生成器中查找记录
        records = self.generator.load_records()
        for record in records:
            if record.get('signal_id') == record_id:
                return record
        return None
    
    def show_details(self):
        """显示详细信息"""
        record = self.get_selected_record()
        if not record:
            self.detail_text.clear()
            return
        
        # 格式化详细信息
        details = f"📊 信号名称: {record['name']}\n"
        details += f"🔢 编码类型: {record['encoding_type']}\n"
        details += f"📏 宽度: {record['width']} 位\n"
        details += f"🕐 创建时间: {record['created_at']}\n"
        details += f"📋 指令数量: {len(record['instructions'])}\n"
        details += f"🎯 值数量: {len(record['values'])}\n\n"
        details += "📝 值映射:\n"
        
        for value_name, instructions in record.get('values', {}).items():
            if isinstance(instructions, list):
                inst_str = ", ".join(instructions[:3])  # 只显示前3个指令
                if len(instructions) > 3:
                    inst_str += f" ... 等{len(instructions)}条指令"
                details += f"  • {value_name}: {inst_str}\n"
        
        self.detail_text.setText(details)
    
    def edit_record(self):
        """编辑选中的记录"""
        record = self.get_selected_record()
        if not record:
            QMessageBox.warning(self, "警告", "请先选择一条记录！")
            return
        
        # 发射信号并关闭对话框
        self.record_selected.emit(record)
        self.accept()
    
    def delete_record(self):
        """删除选中的记录"""
        record = self.get_selected_record()
        if not record:
            QMessageBox.warning(self, "警告", "请先选择一条记录！")
            return
        
        reply = QMessageBox.question(
            self,
            "确认删除",
            f"确定要删除记录 '{record['name']}' 吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.generator.delete_record(record.get('signal_id')):
                QMessageBox.information(self, "成功", "记录已删除！")
                self.load_records()
            else:
                QMessageBox.warning(self, "错误", "删除记录失败！")
    
    def regenerate_code(self):
        """重新生成代码"""
        record = self.get_selected_record()
        if not record:
            QMessageBox.warning(self, "警告", "请先选择一条记录！")
            return
        
        # 生成代码 - 这里获取的是元组(ctrl_code, field_code)
        code_tuple = self.generator.generate_chisel_code(record)
        
        # 显示代码对话框 - 传入元组
        dialog = CodePreviewDialog(self, record['name'], code_tuple)
        dialog.exec()

class CodePreviewDialog(QDialog):
    """代码预览对话框"""
    def __init__(self, parent=None, title="", code=""):
        super().__init__(parent)
        
        # 处理传入的code参数
        # 如果传入的是元组(ctrl_code, field_code)，则分别处理
        # 如果传入的是字符串，则视为ctrl_code
        if isinstance(code, tuple) and len(code) == 2:
            self.ctrl_code = code[0]
            self.field_code = code[1]
        else:
            self.ctrl_code = code if isinstance(code, str) else ""
            self.field_code = ""
        
        self.setWindowTitle(f"代码预览 - {title}")
        self.setModal(True)
        self.resize(950, 700)  # 增加宽度以容纳两个标签页
        
        # 加载当前主题
        self.settings = QSettings("rvctrl-gender", "settings")
        self.current_theme = self.settings.value("current_theme", "light", type=str)
        
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # 创建标签页
        self.tab_widget = QTabWidget()
        
        # Ctrl代码标签页
        ctrl_tab = QWidget()
        ctrl_layout = QVBoxLayout()
        
        self.ctrl_code_edit = QTextEdit()
        self.ctrl_code_edit.setFont(QFont("Monospace", 11))
        self.ctrl_code_edit.setText(self.ctrl_code)
        ctrl_layout.addWidget(self.ctrl_code_edit)
        
        ctrl_tab.setLayout(ctrl_layout)
        self.tab_widget.addTab(ctrl_tab, "Ctrl代码")
        
        # Field代码标签页（如果有Field代码）
        if self.field_code:
            field_tab = QWidget()
            field_layout = QVBoxLayout()
            
            self.field_code_edit = QTextEdit()
            self.field_code_edit.setFont(QFont("Monospace", 11))
            self.field_code_edit.setText(self.field_code)
            field_layout.addWidget(self.field_code_edit)
            
            field_tab.setLayout(field_layout)
            self.tab_widget.addTab(field_tab, "Field代码")
        
        layout.addWidget(self.tab_widget)
        
        # 按钮
        button_layout = QHBoxLayout()
        
        copy_btn = QPushButton("📋 复制当前代码")
        copy_btn.clicked.connect(self.copy_current_code)
        button_layout.addWidget(copy_btn)
        
        save_btn = QPushButton("💾 保存所有文件")
        save_btn.clicked.connect(self.save_all_files)
        button_layout.addWidget(save_btn)
        
        button_layout.addStretch()
        
        close_btn = QPushButton("❌ 关闭")
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def get_current_code(self):
        """获取当前标签页的代码"""
        current_index = self.tab_widget.currentIndex()
        if current_index == 0:  # Ctrl代码标签页
            return self.ctrl_code_edit.toPlainText()
        elif current_index == 1 and hasattr(self, 'field_code_edit'):  # Field代码标签页
            return self.field_code_edit.toPlainText()
        return self.ctrl_code_edit.toPlainText()
    
    def copy_current_code(self):
        """复制当前标签页的代码到剪贴板"""
        code = self.get_current_code()
        if not code.strip():
            QMessageBox.warning(self, "警告", "没有代码可复制！")
            return
        
        clipboard = QApplication.clipboard()
        clipboard.setText(code)
        QMessageBox.information(self, "成功", "代码已复制到剪贴板！")
    
    def save_all_files(self):
        """保存所有代码到文件"""
        # 保存Ctrl代码
        if self.ctrl_code_edit.toPlainText().strip():
            self.save_code_file(self.ctrl_code_edit.toPlainText(), "Ctrl")
        
        # 保存Field代码（如果存在）
        if hasattr(self, 'field_code_edit') and self.field_code_edit.toPlainText().strip():
            self.save_code_file(self.field_code_edit.toPlainText(), "Field")
    
    def save_code_file(self, code, file_type):
        """保存代码到文件 - 提供覆盖选项"""
        # 从代码中提取类名
        class_name = self.extract_class_name(code)
        
        if not class_name:
            class_name = f"ControlSignal{file_type}"
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            f"保存{file_type}文件",
            f"{class_name}.scala",
            f"Scala文件 (*.scala);;所有文件 (*.*)"
        )
        
        if file_path:
            # 确保文件扩展名为.scala
            if not file_path.endswith('.scala'):
                file_path += '.scala'
            
            # 检查文件是否存在
            if os.path.exists(file_path):
                reply = QMessageBox.question(
                    self,
                    "文件已存在",
                    f"文件 {os.path.basename(file_path)} 已存在，是否覆盖？",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                
                if reply == QMessageBox.StandardButton.No:
                    return  # 用户选择不覆盖，取消保存
            
            try:
                # 创建目录（如果需要）
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                
                with open(file_path, 'w') as f:
                    f.write(code)
                
                QMessageBox.information(self, "成功", f"{file_type}代码已保存到:\n{file_path}")
            except PermissionError:
                QMessageBox.critical(
                    self,
                    "权限错误",
                    "没有权限保存文件！请尝试使用管理员权限运行程序。"
                )
            except Exception as e:
                QMessageBox.critical(self, "错误", f"保存文件失败:\n{str(e)}")
    
    def extract_class_name(self, code):
        """从Scala代码中提取类名"""
        # 查找 object 声明
        lines = code.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('object '):
                # 提取 object 名称
                parts = line.split()
                if len(parts) >= 2:
                    name = parts[1]
                    # 移除可能的后缀
                    if 'extends' in name:
                        name = name.split('extends')[0].strip()
                    if '(' in name:
                        name = name.split('(')[0].strip()
                    return name.strip()
        return None

class RISCVCtrlGenerator:
    """RISC-V 控制信号生成器核心逻辑"""
    
    def __init__(self):
        self.instructions: List[Instruction] = []
        
        # 获取配置目录路径
        self.settings = QSettings("rvctrl-gender", "settings")
        
        # 在配置目录下创建records.json文件
        config_dir = Path(self.settings.fileName()).parent
        os.makedirs(config_dir, exist_ok=True)
        self.records_file = str(config_dir / "records.json")
        
        # 确保记录目录存在
        os.makedirs(os.path.dirname(self.records_file), exist_ok=True)
    
    def load_csv(self, filepath: str) -> bool:
        """加载CSV文件"""
        self.instructions.clear()
        try:
            with open(filepath, 'r') as f:
                reader = csv.reader(f, delimiter=' ')
                for row in reader:
                    if len(row) >= 3:
                        name = row[0]
                        extension = row[1]
                        encode = row[2]
                        args = row[3:] if len(row) > 3 else []
                        self.instructions.append(Instruction(name, extension, encode, args))
            return True
        except Exception as e:
            raise Exception(f"加载CSV文件失败: {str(e)}")
    
    def create_control_signal(self, name: str, encoding_type: str, 
                            value_mapping: Dict[str, List[str]]) -> Dict[str, Any]:
        """创建控制信号"""
        # 检查指令是否重复
        all_instructions = []
        for inst_list in value_mapping.values():
            all_instructions.extend(inst_list)
        
        # 检查是否有重复指令
        if len(all_instructions) != len(set(all_instructions)):
            duplicate_instructions = []
            seen = set()
            for inst in all_instructions:
                if inst in seen:
                    duplicate_instructions.append(inst)
                seen.add(inst)
            
            if duplicate_instructions:
                duplicate_list = ", ".join(sorted(duplicate_instructions)[:5])
                if len(duplicate_instructions) > 5:
                    duplicate_list += f" 等 {len(duplicate_instructions)} 条指令"
                raise Exception(f"指令在多个值中重复出现: {duplicate_list}")
        
        # 计算宽度
        if encoding_type == "OneHot":
            width = len(value_mapping)
        else:  # Binary 或 Gray
            width = (len(value_mapping) - 1).bit_length() if len(value_mapping) > 0 else 0
        
        # 创建信号记录
        signal = {
            'name': name,
            'encoding_type': encoding_type,
            'width': width,
            'values': value_mapping,
            'instructions': list(set(all_instructions)),  # 去重
            'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'signal_id': datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        }
        
        # 保存记录
        self.save_record(signal)
        
        return signal
    
    def save_record(self, record: Dict[str, Any]):
        """保存记录"""
        try:
            # 加载现有记录
            records = self.load_records()
            
            # 添加新记录
            records.append(record)
            
            # 保存回文件
            with open(self.records_file, 'w') as f:
                json.dump(records, f, indent=2, ensure_ascii=False)
            
        except Exception as e:
            print(f"保存记录失败: {e}")
    
    def load_records(self) -> List[Dict[str, Any]]:
        """加载所有记录 - 按创建时间排序（从近到远）"""
        if not os.path.exists(self.records_file):
            return []
        
        try:
            with open(self.records_file, 'r') as f:
                records = json.load(f)
            
            # 将字符串时间转换为datetime对象进行比较
            def parse_time(time_str):
                try:
                    return datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
                except:
                    return datetime.min
            
            # 按创建时间降序排序（最新的在前）
            records.sort(key=lambda x: parse_time(x.get('created_at', '')), reverse=True)
            
            return records
        except:
            return []
    
    def delete_record(self, record_id: str) -> bool:
        """删除记录"""
        try:
            records = self.load_records()
            new_records = [r for r in records if r.get('signal_id') != record_id]
            
            with open(self.records_file, 'w') as f:
                json.dump(new_records, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"删除记录失败: {e}")
            return False
    
    def generate_ctrl_code(self, signal: Dict[str, Any]) -> str:
        """生成Ctrl类代码，使用自定义模板"""
        name = signal['name']
        encoding_type = signal['encoding_type']
        values = signal['values']
        width = signal['width']
        
        # 获取自定义模板
        template = self.settings.value("chisel_ctrl_template", "")
        
        # 如果没有自定义模板，使用默认模板
        if not template:
            template = """// ===========================================
// 自动生成的Chisel控制信号枚举类
// 生成时间: {generation_time}
// ===========================================

package rv.util.decoder

import chisel3._
import chisel3.util._
import rv.util.CtrlEnum

/**
  * {signal_name}Ctrl - 控制信号枚举类
  * 编码类型: {encoding_type}
  * 信号宽度: {signal_width} bits
  */
object {signal_name}Ctrl extends CtrlEnum(CtrlEnum.{encoding_type}) {
  // 值定义
{values_list}
  
  // 指令分类方法
{methods_list}
  
  // 辅助方法
  def getAllValues: Seq[UInt] = this.Values
  
  def getWidth: Int = this.getWidth
}"""
        
        # 生成值列表
        values_list = ""
        for value_name in values.keys():
            values_list += f"  val {value_name} = Value\n"
        
        # 生成方法列表 - 即使没有指令也生成方法
        methods_list = ""
        for value_name, inst_list in values.items():
            if inst_list:
                # 每行显示5个指令
                inst_str_parts = []
                for i in range(0, len(inst_list), 5):
                    line_insts = inst_list[i:i+5]
                    inst_str = ', '.join(f'"{inst}"' for inst in line_insts)
                    if i == 0:
                        inst_str_parts.append(f"    {inst_str}")
                    else:
                        inst_str_parts.append(f"    {inst_str}")
                
                inst_str = ',\n'.join(inst_str_parts)
                methods_list += f"  def is{value_name}: Seq[String] = Seq(\n"
                methods_list += f"{inst_str}\n"
                methods_list += "  )\n\n"
            else:
                # 没有指令的情况，返回空序列
                methods_list += f"  def is{value_name}: Seq[String] = Seq()\n\n"
        
        # 替换模板中的占位符
        code = template.replace('{signal_name}', name)
        code = code.replace('{encoding_type}', encoding_type)
        code = code.replace('{values_list}', values_list)
        code = code.replace('{methods_list}', methods_list)
        code = code.replace('{signal_width}', str(width))
        code = code.replace('{generation_time}', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        
        # 如果启用了自动格式化，格式化代码
        if self.settings.value("auto_format", True, type=bool):
            code = self.format_code(code)
        
        return code
    
    def generate_field_code(self, signal: Dict[str, Any]) -> str:
        """生成Field类代码，使用自定义模板"""
        name = signal['name']
        encoding_type = signal['encoding_type']
        values = signal['values']
        width = signal['width']
        
        # 获取自定义模板
        template = self.settings.value("chisel_field_template", "")
        
        # 如果没有自定义模板，使用默认模板
        if not template:
            template = """package rv.util.decoder

import chisel3._
import chisel3.util._
import chisel3.util.experimental.decode._

object {signal_name}Field extends DecodeField[InstructionPattern, UInt] {
  override def name: String = "{signal_name}Field"
  override def chiselType: UInt = UInt({signal_name}Ctrl.getWidth.W)
  private def map: Seq[(Seq[String], UInt)] = Seq(
{value_mappings}
  )
  override def genTable(op: InstructionPattern): BitPat = {
    BitPat(op.nameMatch(map, 0.U({signal_name}Ctrl.getWidth.W)))
  }
}"""
        
        # 生成值映射列表
        value_mappings = ""
        for i, (value_name, inst_list) in enumerate(values.items()):
            if inst_list:
                # 每行显示5个指令
                inst_str_parts = []
                for j in range(0, len(inst_list), 5):
                    line_insts = inst_list[j:j+5]
                    inst_str = ', '.join(f'"{inst}"' for inst in line_insts)
                    if j == 0:
                        inst_str_parts.append(f"    {inst_str}")
                    else:
                        inst_str_parts.append(f"    {inst_str}")
                
                inst_str = ',\n'.join(inst_str_parts)
                value_mappings += f"    {name}.is{value_name} -> {name}.Values({name}.{value_name})"
            else:
                # 没有指令的情况，使用空序列
                value_mappings += f"    Seq() -> {name}.Values({name}.{value_name})"
            
            # 如果不是最后一个，添加逗号
            if i < len(values) - 1:
                value_mappings += ",\n"
        
        # 替换模板中的占位符
        code = template.replace('{signal_name}', name)
        code = code.replace('{encoding_type}', encoding_type)
        code = code.replace('{signal_width}', str(width))
        code = code.replace('{value_mappings}', value_mappings)
        code = code.replace('{generation_time}', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        
        # 如果启用了自动格式化，格式化代码
        if self.settings.value("auto_format", True, type=bool):
            code = self.format_code(code)
        
        return code
    
    def generate_chisel_code(self, signal: Dict[str, Any]) -> Tuple[str, str]:
        """生成Chisel代码，返回(ctrl_code, field_code)"""
        ctrl_code = self.generate_ctrl_code(signal)
        
        # 检查是否自动生成Field文件
        if self.settings.value("auto_field", True, type=bool):
            field_code = self.generate_field_code(signal)
        else:
            field_code = ""
            
        return ctrl_code, field_code
    
    def format_code(self, code: str) -> str:
        """格式化代码（简单的格式化）"""
        lines = code.split('\n')
        formatted_lines = []
        
        indent_level = 0
        for line in lines:
            line = line.rstrip()
            
            # 减少缩进
            if line.strip().startswith('}') or line.strip().endswith('}'):
                indent_level = max(0, indent_level - 1)
            
            # 添加当前行的缩进
            if line.strip():
                formatted_lines.append('  ' * indent_level + line)
            else:
                formatted_lines.append('')
            
            # 增加缩进
            if line.strip().endswith('{') or line.strip().endswith('=>'):
                indent_level += 1
        
        return '\n'.join(formatted_lines)
    
    def save_ctrl_file(self, code: str, signal_name: str = None, overwrite: bool = False) -> str:
        """保存Ctrl文件 - 提供覆盖选项"""
        save_path = self.settings.value("ctrl_save_path", str(Path.home() / "riscv-scala" / "ctrl"))
        
        # 确保目录存在
        try:
            os.makedirs(save_path, exist_ok=True)
        except PermissionError:
            raise PermissionError(f"没有权限创建目录: {save_path}")
        
        # 提取类名
        if signal_name:
            class_name = signal_name
        else:
            # 从代码中提取类名
            lines = code.split('\n')
            for line in lines:
                line = line.strip()
                if line.startswith('object '):
                    # 提取 object 名称
                    parts = line.split()
                    if len(parts) >= 2:
                        name = parts[1]
                        # 移除可能的后缀
                        if 'extends' in name:
                            name = name.split('extends')[0].strip()
                        if '(' in name:
                            name = name.split('(')[0].strip()
                        class_name = name.strip()
                        break
            else:
                # 如果没有找到object定义，使用默认名称
                class_name = "ControlSignal"

        if not class_name.endswith('Ctrl'):
            class_name = f"{class_name}Ctrl"
        
        # 生成文件名
        file_path = os.path.join(save_path, f"{class_name}.scala")
        
        # 如果文件已存在且不覆盖，添加序号
        if os.path.exists(file_path) and not overwrite:
            counter = 1
            while os.path.exists(file_path):
                file_path = os.path.join(save_path, f"{class_name}_{counter}.scala")
                counter += 1
        
        # 保存文件
        with open(file_path, 'w') as f:
            f.write(code)
        
        return file_path
    
    def save_field_file(self, code: str, signal_name: str = None, overwrite: bool = False) -> str:
        """保存Field文件 - 提供覆盖选项"""
        if not code:  # 如果没有生成field代码
            return ""
            
        save_path = self.settings.value("field_save_path", str(Path.home() / "riscv-scala" / "field"))
        
        # 确保目录存在
        try:
            os.makedirs(save_path, exist_ok=True)
        except PermissionError:
            raise PermissionError(f"没有权限创建目录: {save_path}")
        
        # 提取类名
        if signal_name:
            class_name = signal_name
        else:
            # 从代码中提取类名
            lines = code.split('\n')
            for line in lines:
                line = line.strip()
                if line.startswith('object '):
                    # 提取 object 名称
                    parts = line.split()
                    if len(parts) >= 2:
                        name = parts[1]
                        # 移除可能的后缀
                        if 'extends' in name:
                            name = name.split('extends')[0].strip()
                        if '(' in name:
                            name = name.split('(')[0].strip()
                        class_name = name.strip()
                        break
            else:
                # 如果没有找到object定义，使用默认名称
                class_name = "ControlSignalField"

        if not class_name.endswith('Field'):
            class_name = f"{class_name}Ctrl"
        
        # 生成文件名
        file_path = os.path.join(save_path, f"{class_name}.scala")
        
        # 如果文件已存在且不覆盖，添加序号
        if os.path.exists(file_path) and not overwrite:
            counter = 1
            while os.path.exists(file_path):
                file_path = os.path.join(save_path, f"{class_name}_{counter}.scala")
                counter += 1
        
        # 保存文件
        with open(file_path, 'w') as f:
            f.write(code)
        
        return file_path
    
    def save_scala_files(self, ctrl_code: str, field_code: str, signal_name: str = None, overwrite: bool = False) -> Tuple[str, str]:
        """保存Scala文件，返回(ctrl_file_path, field_file_path) - 提供覆盖选项"""
        ctrl_file_path = self.save_ctrl_file(ctrl_code, signal_name, overwrite)
        
        field_file_path = ""
        if field_code:
            field_file_path = self.save_field_file(field_code, signal_name, overwrite)
        
        return ctrl_file_path, field_file_path

class MainWindow(QMainWindow):
    """主窗口"""
    
    def __init__(self):
        super().__init__()
        self.generator = RISCVCtrlGenerator()
        self.value_widgets = []
        self.current_record = None
        
        # 加载设置
        self.settings = QSettings("rvctrl-gender", "settings")
        self.current_theme = self.settings.value("current_theme", "light", type=str)
        
        self.setWindowTitle("RISC-V Ctrl Generator")
        self.setGeometry(100, 100, 1400, 900)
        
        # 应用当前主题
        self.apply_theme()
        
        self.init_ui()
        self.load_default_csv()
    
    def apply_theme(self):
        """应用当前主题"""
        if self.current_theme == "dark":
            self.setStyleSheet(self.get_dark_theme_stylesheet())
        else:
            self.setStyleSheet(self.get_light_theme_stylesheet())
    
    def get_light_theme_stylesheet(self):
        """获取亮色主题样式表"""
        return """
        /* 主窗口 */
        QMainWindow {
            background-color: #ffffff;
            color: #2c3e50;
        }
        
        /* 菜单栏 */
        QMenuBar {
            background-color: #f8f9fa;
            color: #2c3e50;
            border-bottom: 2px solid #dee2e6;
            font-weight: bold;
        }
        QMenuBar::item {
            background-color: transparent;
            color: #2c3e50;
            padding: 6px 12px;
        }
        QMenuBar::item:selected {
            background-color: #e9ecef;
            color: #3498db;
            border-radius: 4px;
        }
        QMenuBar::item:pressed {
            background-color: #dee2e6;
        }
        QMenu {
            background-color: #ffffff;
            color: #2c3e50;
            border: 2px solid #dee2e6;
            border-radius: 4px;
        }
        QMenu::item {
            background-color: transparent;
            color: #2c3e50;
            padding: 6px 24px;
        }
        QMenu::item:selected {
            background-color: #e9ecef;
            color: #3498db;
            border-radius: 3px;
        }
        
        /* 工具栏 */
        QToolBar {
            background-color: #f8f9fa;
            border: 2px solid #dee2e6;
            spacing: 6px;
            padding: 6px;
            border-radius: 4px;
            margin: 4px;
        }
        
        /* 按钮 */
        QPushButton {
            background-color: #f8f9fa;
            color: #2c3e50;
            border: 2px solid #dee2e6;
            border-radius: 5px;
            padding: 8px 16px;
            font-weight: bold;
            min-height: 28px;
            font-size: 13px;
        }
        QPushButton:hover {
            background-color: #e9ecef;
            border: 2px solid #3498db;
            color: #3498db;
        }
        QPushButton:pressed {
            background-color: #dee2e6;
            border: 2px solid #dee2e6;
        }
        QPushButton:disabled {
            background-color: #f8f9fa;
            color: #adb5bd;
            border: 2px solid #e9ecef;
        }
        
        /* 特殊按钮 */
        QPushButton[special="true"] {
            background-color: #e3f2fd;
            color: #1565c0;
            border: 2px solid #bbdefb;
        }
        QPushButton[special="true"]:hover {
            background-color: #bbdefb;
            border: 2px solid #3498db;
        }
        
        /* 标签 */
        QLabel {
            color: #2c3e50;
        }
        QLabel[title="true"] {
            font-size: 17px;
            font-weight: bold;
            color: #3498db;
        }
        
        /* 输入框 */
        QLineEdit, QComboBox {
            background-color: #ffffff;
            color: #2c3e50;
            border: 2px solid #dee2e6;
            border-radius: 5px;
            padding: 7px;
            selection-background-color: #3498db;
            selection-color: #ffffff;
            font-size: 13px;
        }
        QLineEdit:focus, QComboBox:focus {
            border: 2px solid #3498db;
        }
        QComboBox::drop-down {
            border: none;
            background-color: #f8f9fa;
            border-radius: 0 5px 5px 0;
        }
        QComboBox::down-arrow {
            image: none;
            border-left: 6px solid transparent;
            border-right: 6px solid transparent;
            border-top: 6px solid #2c3e50;
        }
        QComboBox QAbstractItemView {
            background-color: #ffffff;
            color: #2c3e50;
            border: 2px solid #dee2e6;
            selection-background-color: #3498db;
            selection-color: #ffffff;
            border-radius: 5px;
        }
        
        /* 列表 */
        QListWidget {
            background-color: #ffffff;
            color: #2c3e50;
            border: 2px solid #dee2e6;
            border-radius: 5px;
            alternate-background-color: #f8f9fa;
            font-size: 13px;
        }
        QListWidget::item {
            padding: 6px;
            border-bottom: 1px solid #dee2e6;
        }
        QListWidget::item:selected {
            background-color: #3498db;
            color: #ffffff;
            font-weight: bold;
        }
        QListWidget::item:hover {
            background-color: #e9ecef;
        }
        
        /* 文本框 */
        QTextEdit, QPlainTextEdit {
            background-color: #ffffff;
            color: #2c3e50;
            border: 2px solid #dee2e6;
            border-radius: 5px;
            font-family: 'Monospace';
            font-size: 13px;
            selection-background-color: #3498db;
            selection-color: #ffffff;
        }
        
        /* 分组框 */
        QGroupBox {
            font-weight: bold;
            color: #2c3e50;
            border: 2px solid #dee2e6;
            border-radius: 6px;
            margin-top: 12px;
            padding-top: 12px;
            background-color: #ffffff;
            font-size: 13px;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 12px;
            padding: 0 6px 0 6px;
            color: #3498db;
            font-size: 14px;
        }
        
        /* 状态栏 */
        QStatusBar {
            background-color: #f8f9fa;
            color: #2c3e50;
            border-top: 2px solid #dee2e6;
            font-weight: bold;
        }
        QStatusBar::item {
            border: none;
        }
        
        /* 表格 */
        QTableWidget {
            background-color: #ffffff;
            color: #2c3e50;
            border: 2px solid #dee2e6;
            gridline-color: #dee2e6;
            alternate-background-color: #f8f9fa;
            font-size: 13px;
        }
        QTableWidget::item {
            padding: 6px;
        }
        QTableWidget::item:selected {
            background-color: #3498db;
            color: #ffffff;
            font-weight: bold;
        }
        QHeaderView::section {
            background-color: #f8f9fa;
            color: #2c3e50;
            padding: 10px;
            border: 1px solid #dee2e6;
            font-weight: bold;
            font-size: 13px;
        }
        QHeaderView::section:checked {
            background-color: #3498db;
            color: #ffffff;
        }
        
        /* 滚动条 */
        QScrollBar:vertical {
            background-color: #f8f9fa;
            width: 14px;
            border: 1px solid #dee2e6;
            border-radius: 7px;
        }
        QScrollBar::handle:vertical {
            background-color: #adb5bd;
            border-radius: 6px;
            min-height: 24px;
        }
        QScrollBar::handle:vertical:hover {
            background-color: #3498db;
        }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            height: 0px;
        }
        QScrollBar:horizontal {
            background-color: #f8f9fa;
            height: 14px;
            border: 1px solid #dee2e6;
            border-radius: 7px;
        }
        QScrollBar::handle:horizontal {
            background-color: #adb5bd;
            border-radius: 6px;
            min-width: 24px;
        }
        QScrollBar::handle:horizontal:hover {
            background-color: #3498db;
        }
        
        /* 复选框 */
        QCheckBox {
            color: #2c3e50;
            spacing: 8px;
            font-size: 13px;
        }
        QCheckBox::indicator {
            width: 18px;
            height: 18px;
            border: 2px solid #adb5bd;
            border-radius: 4px;
            background-color: #ffffff;
        }
        QCheckBox::indicator:checked {
            background-color: #3498db;
            border: 2px solid #3498db;
        }
        QCheckBox::indicator:checked:hover {
            background-color: #2980b9;
        }
        
        /* 对话框按钮盒 */
        QDialogButtonBox {
            background-color: transparent;
        }
        
        /* 选项卡 */
        QTabWidget::pane {
            border: 2px solid #dee2e6;
            background-color: #ffffff;
            border-radius: 5px;
        }
        QTabBar::tab {
            background-color: #f8f9fa;
            color: #2c3e50;
            padding: 10px 20px;
            margin-right: 3px;
            border-top-left-radius: 5px;
            border-top-right-radius: 5px;
            font-weight: bold;
        }
        QTabBar::tab:selected {
            background-color: #3498db;
            color: #ffffff;
        }
        QTabBar::tab:hover {
            background-color: #e9ecef;
        }
        
        /* 分隔符 */
        QSplitter::handle {
            background-color: #dee2e6;
            border-radius: 3px;
        }
        QSplitter::handle:hover {
            background-color: #3498db;
        }
        
        /* 框架 */
        QFrame {
            background-color: #ffffff;
            border: 2px solid #dee2e6;
            border-radius: 5px;
        }
        QFrame[highlight="true"] {
            border: 3px solid #3498db;
            background-color: #f8f9fa;
        }
        
        /* 工具提示 */
        QToolTip {
            background-color: #ffffff;
            color: #2c3e50;
            border: 2px solid #dee2e6;
            padding: 6px;
            border-radius: 4px;
            opacity: 240;
            font-size: 12px;
        }
        """
    
    def get_dark_theme_stylesheet(self):
        """获取暗色主题样式表"""
        return """
        /* 主窗口 */
        QMainWindow {
            background-color: #2d2d2d;
            color: #e0e0e0;
        }
        
        /* 菜单栏 */
        QMenuBar {
            background-color: #3c3c3c;
            color: #e0e0e0;
            border-bottom: 2px solid #555555;
            font-weight: bold;
        }
        QMenuBar::item {
            background-color: transparent;
            color: #e0e0e0;
            padding: 6px 12px;
        }
        QMenuBar::item:selected {
            background-color: #4c4c4c;
            color: #4a9eff;
            border-radius: 4px;
        }
        QMenuBar::item:pressed {
            background-color: #2c2c2c;
        }
        QMenu {
            background-color: #3c3c3c;
            color: #e0e0e0;
            border: 2px solid #555555;
            border-radius: 4px;
        }
        QMenu::item {
            background-color: transparent;
            color: #e0e0e0;
            padding: 6px 24px;
        }
        QMenu::item:selected {
            background-color: #4c4c4c;
            color: #4a9eff;
            border-radius: 3px;
        }
        
        /* 工具栏 */
        QToolBar {
            background-color: #3c3c3c;
            border: 2px solid #555555;
            spacing: 6px;
            padding: 6px;
            border-radius: 4px;
            margin: 4px;
        }
        
        /* 按钮 */
        QPushButton {
            background-color: #3c3c3c;
            color: #e0e0e0;
            border: 2px solid #555555;
            border-radius: 5px;
            padding: 8px 16px;
            font-weight: bold;
            min-height: 28px;
            font-size: 13px;
        }
        QPushButton:hover {
            background-color: #4c4c4c;
            border: 2px solid #4a9eff;
            color: #4a9eff;
        }
        QPushButton:pressed {
            background-color: #2c2c2c;
            border: 2px solid #555555;
        }
        QPushButton:disabled {
            background-color: #3c3c3c;
            color: #777777;
            border: 2px solid #555555;
        }
        
        /* 特殊按钮 */
        QPushButton[special="true"] {
            background-color: #1e3a5f;
            color: #90caf9;
            border: 2px solid #1565c0;
        }
        QPushButton[special="true"]:hover {
            background-color: #1565c0;
            border: 2px solid #4a9eff;
        }
        
        /* 标签 */
        QLabel {
            color: #e0e0e0;
        }
        QLabel[title="true"] {
            font-size: 17px;
            font-weight: bold;
            color: #4a9eff;
        }
        
        /* 输入框 */
        QLineEdit, QComboBox {
            background-color: #3c3c3c;
            color: #e0e0e0;
            border: 2px solid #555555;
            border-radius: 5px;
            padding: 7px;
            selection-background-color: #4a9eff;
            selection-color: #ffffff;
            font-size: 13px;
        }
        QLineEdit:focus, QComboBox:focus {
            border: 2px solid #4a9eff;
        }
        QComboBox::drop-down {
            border: none;
            background-color: #4c4c4c;
            border-radius: 0 5px 5px 0;
        }
        QComboBox::down-arrow {
            image: none;
            border-left: 6px solid transparent;
            border-right: 6px solid transparent;
            border-top: 6px solid #e0e0e0;
        }
        QComboBox QAbstractItemView {
            background-color: #3c3c3c;
            color: #e0e0e0;
            border: 2px solid #555555;
            selection-background-color: #4a9eff;
            selection-color: #ffffff;
            border-radius: 5px;
        }
        
        /* 列表 */
        QListWidget {
            background-color: #3c3c3c;
            color: #e0e0e0;
            border: 2px solid #555555;
            border-radius: 5px;
            alternate-background-color: #333333;
            font-size: 13px;
        }
        QListWidget::item {
            padding: 6px;
            border-bottom: 1px solid #555555;
        }
        QListWidget::item:selected {
            background-color: #4a9eff;
            color: #ffffff;
            font-weight: bold;
        }
        QListWidget::item:hover {
            background-color: #4c4c4c;
        }
        
        /* 文本框 */
        QTextEdit, QPlainTextEdit {
            background-color: #3c3c3c;
            color: #e0e0e0;
            border: 2px solid #555555;
            border-radius: 5px;
            font-family: 'Monospace';
            font-size: 13px;
            selection-background-color: #4a9eff;
            selection-color: #ffffff;
        }
        
        /* 分组框 */
        QGroupBox {
            font-weight: bold;
            color: #e0e0e0;
            border: 2px solid #555555;
            border-radius: 6px;
            margin-top: 12px;
            padding-top: 12px;
            background-color: #3c3c3c;
            font-size: 13px;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 12px;
            padding: 0 6px 0 6px;
            color: #4a9eff;
            font-size: 14px;
        }
        
        /* 状态栏 */
        QStatusBar {
            background-color: #3c3c3c;
            color: #e0e0e0;
            border-top: 2px solid #555555;
            font-weight: bold;
        }
        QStatusBar::item {
            border: none;
        }
        
        /* 表格 */
        QTableWidget {
            background-color: #3c3c3c;
            color: #e0e0e0;
            border: 2px solid #555555;
            gridline-color: #555555;
            alternate-background-color: #333333;
            font-size: 13px;
        }
        QTableWidget::item {
            padding: 6px;
        }
        QTableWidget::item:selected {
            background-color: #4a9eff;
            color: #ffffff;
            font-weight: bold;
        }
        QHeaderView::section {
            background-color: #4c4c4c;
            color: #e0e0e0;
            padding: 10px;
            border: 1px solid #555555;
            font-weight: bold;
            font-size: 13px;
        }
        QHeaderView::section:checked {
            background-color: #4a9eff;
            color: #ffffff;
        }
        
        /* 滚动条 */
        QScrollBar:vertical {
            background-color: #3c3c3c;
            width: 14px;
            border: 1px solid #555555;
            border-radius: 7px;
        }
        QScrollBar::handle:vertical {
            background-color: #666666;
            border-radius: 6px;
            min-height: 24px;
        }
        QScrollBar::handle:vertical:hover {
            background-color: #4a9eff;
        }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            height: 0px;
        }
        QScrollBar:horizontal {
            background-color: #3c3c3c;
            height: 14px;
            border: 1px solid #555555;
            border-radius: 7px;
        }
        QScrollBar::handle:horizontal {
            background-color: #666666;
            border-radius: 6px;
            min-width: 24px;
        }
        QScrollBar::handle:horizontal:hover {
            background-color: #4a9eff;
        }
        
        /* 复选框 */
        QCheckBox {
            color: #e0e0e0;
            spacing: 8px;
            font-size: 13px;
        }
        QCheckBox::indicator {
            width: 18px;
            height: 18px;
            border: 2px solid #777777;
            border-radius: 4px;
            background-color: #3c3c3c;
        }
        QCheckBox::indicator:checked {
            background-color: #4a9eff;
            border: 2px solid #4a9eff;
        }
        QCheckBox::indicator:checked:hover {
            background-color: #3a7eff;
        }
        
        /* 对话框按钮盒 */
        QDialogButtonBox {
            background-color: transparent;
        }
        
        /* 选项卡 */
        QTabWidget::pane {
            border: 2px solid #555555;
            background-color: #3c3c3c;
            border-radius: 5px;
        }
        QTabBar::tab {
            background-color: #4c4c4c;
            color: #e0e0e0;
            padding: 10px 20px;
            margin-right: 3px;
            border-top-left-radius: 5px;
            border-top-right-radius: 5px;
            font-weight: bold;
        }
        QTabBar::tab:selected {
            background-color: #4a9eff;
            color: #ffffff;
        }
        QTabBar::tab:hover {
            background-color: #5c5c5c;
        }
        
        /* 分隔符 */
        QSplitter::handle {
            background-color: #555555;
            border-radius: 3px;
        }
        QSplitter::handle:hover {
            background-color: #4a9eff;
        }
        
        /* 框架 */
        QFrame {
            background-color: #3c3c3c;
            border: 2px solid #555555;
            border-radius: 5px;
        }
        QFrame[highlight="true"] {
            border: 3px solid #4a9eff;
            background-color: #4c4c4c;
        }
        
        /* 工具提示 */
        QToolTip {
            background-color: #3c3c3c;
            color: #e0e0e0;
            border: 2px solid #555555;
            padding: 6px;
            border-radius: 4px;
            opacity: 240;
            font-size: 12px;
        }
        """
    
    def init_ui(self):
        """初始化UI"""
        # 创建菜单栏
        self.create_menu_bar()
        
        # 创建工具栏
        self.create_tool_bar()
        
        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)
        
        # 创建左侧面板（指令列表）
        left_panel = self.create_left_panel()
        main_layout.addWidget(left_panel, 1)
        
        # 创建中间面板（配置）
        center_panel = self.create_center_panel()
        main_layout.addWidget(center_panel, 2)
        
        # 创建右侧面板（代码预览）
        right_panel = self.create_right_panel()
        main_layout.addWidget(right_panel, 1)
        
        # 创建状态栏
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        if self.current_theme == "dark":
            self.status_bar.showMessage("✅ 就绪 - 暗色主题")
        else:
            self.status_bar.showMessage("✅ 就绪 - 亮色主题")
    
    def create_menu_bar(self):
        """创建菜单栏"""
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu("📁 文件")
        
        load_csv_action = QAction("📄 加载CSV文件", self)
        load_csv_action.triggered.connect(self.load_csv_file)
        file_menu.addAction(load_csv_action)
        
        # 模板菜单
        template_action = QAction("📝 管理代码模板", self)
        template_action.triggered.connect(self.show_template_manager)
        file_menu.addAction(template_action)
        
        file_menu.addSeparator()
        
        settings_action = QAction("⚙️ 设置", self)
        settings_action.triggered.connect(self.show_settings)
        file_menu.addAction(settings_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("❌ 退出", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 工具菜单
        tools_menu = menubar.addMenu("🔧 工具")
        
        records_action = QAction("📋 生成记录", self)
        records_action.triggered.connect(self.show_record_manager)
        tools_menu.addAction(records_action)
        
        # 主题菜单
        theme_menu = menubar.addMenu("🎨 主题")
        
        light_action = QAction("🌞 亮色主题", self)
        light_action.triggered.connect(lambda: self.set_theme("light"))
        if self.current_theme == "light":
            light_action.setEnabled(False)
        theme_menu.addAction(light_action)
        
        dark_action = QAction("🌙 暗色主题", self)
        dark_action.triggered.connect(lambda: self.set_theme("dark"))
        if self.current_theme == "dark":
            dark_action.setEnabled(False)
        theme_menu.addAction(dark_action)
    
    def set_theme(self, theme_name):
        """设置主题"""
        if theme_name == self.current_theme:
            return
        
        # 保存主题设置
        self.settings.setValue("current_theme", theme_name)
        self.current_theme = theme_name
        
        # 重新应用主题
        self.apply_theme()
        
        # 更新所有值部件的主题
        for widget in self.value_widgets:
            widget.current_theme = theme_name
            widget.init_ui(widget.name_edit.text())
        
        # 更新状态栏
        if theme_name == "dark":
            self.status_bar.showMessage("✅ 已切换到暗色主题")
        else:
            self.status_bar.showMessage("✅ 已切换到亮色主题")
        
        # 重新创建主题菜单
        self.menuBar().clear()
        self.create_menu_bar()
    
    def create_tool_bar(self):
        """创建工具栏"""
        toolbar = QToolBar("主工具栏")
        toolbar.setIconSize(QSize(26, 26))
        self.addToolBar(toolbar)
        
        # 加载CSV按钮
        load_btn = QPushButton("📂 加载CSV")
        load_btn.clicked.connect(self.load_csv_file)
        toolbar.addWidget(load_btn)
        
        toolbar.addSeparator()
        
        # 生成代码按钮
        generate_btn = QPushButton("⚡ 生成代码")
        generate_btn.clicked.connect(self.generate_code)
        toolbar.addWidget(generate_btn)
        
        toolbar.addSeparator()
        
        # 模板管理按钮
        template_btn = QPushButton("📝 代码模板")
        template_btn.clicked.connect(self.show_template_manager)
        toolbar.addWidget(template_btn)
        
        # 记录管理按钮
        records_btn = QPushButton("📋 生成记录")
        records_btn.clicked.connect(self.show_record_manager)
        toolbar.addWidget(records_btn)
        
        # 设置按钮
        settings_btn = QPushButton("⚙️ 设置")
        settings_btn.clicked.connect(self.show_settings)
        toolbar.addWidget(settings_btn)
    
    def create_left_panel(self):
        """创建左侧面板 - 只显示指令信息，无选择功能"""
        panel = QWidget()
        layout = QVBoxLayout()
        
        # 标题
        title = QLabel("📋 RISC-V 指令列表")
        title.setProperty("title", True)
        layout.addWidget(title)
        
        # 搜索框
        search_layout = QHBoxLayout()
        search_label = QLabel("🔍 搜索:")
        if self.current_theme == "dark":
            search_label.setStyleSheet("color: #e0e0e0; font-weight: bold;")
        else:
            search_label.setStyleSheet("color: #2c3e50; font-weight: bold;")
        search_layout.addWidget(search_label)
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("输入指令名、指令集或编码进行搜索...")
        self.search_edit.textChanged.connect(self.filter_instructions)
        search_layout.addWidget(self.search_edit)
        layout.addLayout(search_layout)
        
        # 指令数量标签
        self.inst_count_label = QLabel("指令总数: 0")
        if self.current_theme == "dark":
            self.inst_count_label.setStyleSheet("color: #4a9eff; font-weight: bold; padding: 5px;")
        else:
            self.inst_count_label.setStyleSheet("color: #3498db; font-weight: bold; padding: 5px;")
        layout.addWidget(self.inst_count_label)
        
        # 指令列表 - 设置为不可选择
        self.instruction_list = QListWidget()
        self.instruction_list.setSelectionMode(QListWidget.SelectionMode.NoSelection)  # 禁止选择
        layout.addWidget(self.instruction_list, 1)
        
        panel.setLayout(layout)
        return panel
    
    def create_center_panel(self):
        """创建中间面板"""
        panel = QWidget()
        layout = QVBoxLayout()
        
        # 标题
        title = QLabel("⚙️ 控制信号配置")
        title.setProperty("title", True)
        layout.addWidget(title)
        
        # 基本配置
        basic_group = QGroupBox("基本配置")
        basic_layout = QFormLayout()
        
        # 信号名称
        name_label = QLabel("信号名称:")
        if self.current_theme == "dark":
            name_label.setStyleSheet("color: #e0e0e0; font-weight: bold;")
        else:
            name_label.setStyleSheet("color: #2c3e50; font-weight: bold;")
        self.signal_name_edit = QLineEdit()
        self.signal_name_edit.setText("InstTypeCtrl")
        basic_layout.addRow(name_label, self.signal_name_edit)
        
        # 编码类型
        encoding_label = QLabel("编码类型:")
        if self.current_theme == "dark":
            encoding_label.setStyleSheet("color: #e0e0e0; font-weight: bold;")
        else:
            encoding_label.setStyleSheet("color: #2c3e50; font-weight: bold;")
        self.encoding_combo = QComboBox()
        self.encoding_combo.addItems(["OneHot", "Binary", "Gray"])
        basic_layout.addRow(encoding_label, self.encoding_combo)
        
        basic_group.setLayout(basic_layout)
        layout.addWidget(basic_group)
        
        # 值配置区域
        value_group = QGroupBox("值定义与指令绑定")
        value_layout = QVBoxLayout()
        
        # 滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_widget = QWidget()
        self.value_container_layout = QVBoxLayout()
        
        # 添加提示标签
        self.value_hint_label = QLabel("请添加值")
        self.value_hint_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        if self.current_theme == "dark":
            self.value_hint_label.setStyleSheet("""
                color: #888888;
                font-size: 14px;
                font-style: italic;
                padding: 40px;
            """)
        else:
            self.value_hint_label.setStyleSheet("""
                color: #999999;
                font-size: 14px;
                font-style: italic;
                padding: 40px;
            """)
        self.value_container_layout.addWidget(self.value_hint_label)
        
        scroll_widget.setLayout(self.value_container_layout)
        scroll_area.setWidget(scroll_widget)
        
        value_layout.addWidget(scroll_area)
        
        # 添加/删除值按钮
        btn_layout = QHBoxLayout()
        
        add_value_btn = QPushButton("➕ 添加值")
        add_value_btn.clicked.connect(self.add_value_widget)
        btn_layout.addWidget(add_value_btn)
        
        remove_value_btn = QPushButton("➖ 删除最后一个值")
        remove_value_btn.clicked.connect(self.remove_last_value_widget)
        btn_layout.addWidget(remove_value_btn)
        
        # 新增：清空所有值按钮
        clear_all_values_btn = QPushButton("🗑️ 清空所有值")
        clear_all_values_btn.clicked.connect(self.clear_all_value_widgets)
        btn_layout.addWidget(clear_all_values_btn)
        
        btn_layout.addStretch()
        value_layout.addLayout(btn_layout)
        
        value_group.setLayout(value_layout)
        layout.addWidget(value_group, 1)
        
        panel.setLayout(layout)
        
        # 初始不添加任何值部件
        self.value_widgets = []
        
        return panel
    
    def create_right_panel(self):
        """创建右侧面板"""
        panel = QWidget()
        layout = QVBoxLayout()
        
        # 创建标签页
        self.code_tab_widget = QTabWidget()
        
        # Ctrl代码标签页
        ctrl_tab = QWidget()
        ctrl_layout = QVBoxLayout()
        
        ctrl_title = QLabel("📄 Ctrl代码预览")
        ctrl_title.setProperty("title", True)
        ctrl_layout.addWidget(ctrl_title)
        
        self.ctrl_code_editor = QTextEdit()
        self.ctrl_code_editor.setFont(QFont("Monospace", 11))
        self.ctrl_code_editor.setReadOnly(True)
        ctrl_layout.addWidget(self.ctrl_code_editor, 1)
        
        ctrl_tab.setLayout(ctrl_layout)
        
        # Field代码标签页
        field_tab = QWidget()
        field_layout = QVBoxLayout()
        
        field_title = QLabel("📄 Field代码预览")
        field_title.setProperty("title", True)
        field_layout.addWidget(field_title)
        
        self.field_code_editor = QTextEdit()
        self.field_code_editor.setFont(QFont("Monospace", 11))
        self.field_code_editor.setReadOnly(True)
        field_layout.addWidget(self.field_code_editor, 1)
        
        field_tab.setLayout(field_layout)
        
        # 添加标签页
        self.code_tab_widget.addTab(ctrl_tab, "Ctrl代码")
        self.code_tab_widget.addTab(field_tab, "Field代码")
        
        layout.addWidget(self.code_tab_widget, 1)
        
        # 按钮
        btn_layout = QHBoxLayout()
        
        copy_btn = QPushButton("📋 复制代码")
        copy_btn.clicked.connect(self.copy_code)
        btn_layout.addWidget(copy_btn)
        
        save_btn = QPushButton("💾 保存所有文件")
        save_btn.clicked.connect(self.save_all_files)
        btn_layout.addWidget(save_btn)
        
        # 模板预览按钮
        template_btn = QPushButton("👁️ 预览模板")
        template_btn.clicked.connect(self.show_template_preview)
        btn_layout.addWidget(template_btn)
        
        btn_layout.addStretch()
        
        clear_btn = QPushButton("🗑️ 清空")
        clear_btn.clicked.connect(self.clear_code)
        btn_layout.addWidget(clear_btn)
        
        layout.addLayout(btn_layout)
        
        panel.setLayout(layout)
        return panel
    
    def load_default_csv(self):
        """加载默认CSV文件"""
        settings = QSettings("rvctrl-gender", "settings")
        csv_path = settings.value("default_csv", "")
        
        if csv_path and os.path.exists(csv_path):
            try:
                self.load_csv_data(csv_path)
            except Exception as e:
                QMessageBox.warning(self, "警告", f"加载默认CSV文件失败:\n{str(e)}")
    
    def load_csv_file(self):
        """加载CSV文件"""
        settings = QSettings("rvctrl-gender", "settings")
        last_dir = settings.value("last_csv_dir", "")
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择CSV文件",
            last_dir,
            "CSV文件 (*.csv);;所有文件 (*.*)"
        )
        
        if file_path:
            try:
                # 保存路径
                settings.setValue("last_csv_dir", os.path.dirname(file_path))
                
                # 加载数据
                self.load_csv_data(file_path)
                
                # 更新状态
                self.status_bar.showMessage(f"✅ 已加载 {len(self.generator.instructions)} 条指令")
                
            except Exception as e:
                QMessageBox.critical(self, "错误", f"加载CSV文件失败:\n{str(e)}")
    
    def load_csv_data(self, file_path):
        """加载CSV数据"""
        self.generator.load_csv(file_path)
        self.update_instruction_list()
        
        # 更新值部件的指令列表
        for widget in self.value_widgets:
            widget.instructions = self.generator.instructions
    
    def update_instruction_list(self):
        """更新指令列表 - 显示详细信息，无选择功能"""
        self.instruction_list.clear()
        
        # 更新指令数量标签
        count = len(self.generator.instructions)
        self.inst_count_label.setText(f"📊 指令总数: {count}")
        
        for inst in self.generator.instructions:
            # 创建显示文本：指令名 [指令集] 编码 (args)
            display_text = f"🔹 {inst.name}"
            
            # 添加指令集信息
            display_text += f"  [{inst.extension}]"
            
            # 添加编码信息（缩短显示）
            if inst.encode:
                # 如果编码太长，只显示前20个字符
                encode_display = inst.encode
                if len(encode_display) > 40:
                    encode_display = encode_display[:37] + "..."
                display_text += f"\n  编码: {encode_display}"
            
            # 添加参数信息
            if inst.args:
                args_str = " ".join(inst.args)
                if len(args_str) > 50:
                    args_str = args_str[:47] + "..."
                display_text += f"\n  参数: {args_str}"
            
            item = QListWidgetItem(display_text)
            item.setData(Qt.ItemDataRole.UserRole, inst.name)
            
            # 设置工具提示显示完整信息
            tooltip_text = f"指令: {inst.name}\n指令集: {inst.extension}\n编码: {inst.encode}"
            if inst.args:
                tooltip_text += f"\n参数: {' '.join(inst.args)}"
            item.setToolTip(tooltip_text)
            
            self.instruction_list.addItem(item)
    
    def filter_instructions(self, text):
        """过滤指令列表"""
        text = text.lower()
        visible_count = 0
        
        for i in range(self.instruction_list.count()):
            item = self.instruction_list.item(i)
            item_text = item.text().lower()
            item.setHidden(text not in item_text)
            
            if not item.isHidden():
                visible_count += 1
        
        # 更新显示的指令数量
        total_count = self.instruction_list.count()
        self.inst_count_label.setText(f"📊 指令总数: {total_count} (显示: {visible_count})")
    
    def add_value_widget(self):
        """添加值配置部件"""
        # 如果是第一个值部件，隐藏提示标签
        if len(self.value_widgets) == 0 and hasattr(self, 'value_hint_label'):
            self.value_hint_label.hide()
        
        widget = ValueConfigWidget(
            self,
            f"Value{len(self.value_widgets) + 1}",
            self.generator.instructions
        )
        widget.config_changed.connect(self.on_config_changed)
        
        # 设置获取禁用指令的函数
        widget.set_get_disabled_instructions_func(lambda: self.get_disabled_instructions_for_widget(widget))
        
        # 设置获取指令到值映射的函数
        widget.set_get_value_mapping_func(lambda: self.get_value_mapping_for_widget(widget))
        
        self.value_container_layout.addWidget(widget)
        self.value_widgets.append(widget)
        
        # 触发配置变化，以更新所有值部件的禁用状态
        self.on_config_changed()
    
    def get_disabled_instructions_for_widget(self, current_widget):
        """获取除了指定部件外的其他部件已选指令"""
        disabled = set()
        for widget in self.value_widgets:
            if widget is not current_widget:
                disabled.update(widget.selected_instructions)
        return disabled
    
    def get_value_mapping_for_widget(self, current_widget):
        """获取指令到值的映射（除了指定部件外）"""
        value_mapping = {}  # {指令名: [值名1, 值名2, ...]}
        
        for widget in self.value_widgets:
            if widget is not current_widget:
                value_name = widget.name_edit.text().strip()
                if value_name and widget.selected_instructions:
                    for inst in widget.selected_instructions:
                        if inst not in value_mapping:
                            value_mapping[inst] = []
                        value_mapping[inst].append(value_name)
        
        return value_mapping
    
    def on_config_changed(self):
        """配置变化时的处理"""
        # 更新所有值部件的禁用指令函数和值映射函数
        for widget in self.value_widgets:
            widget.set_get_disabled_instructions_func(lambda w=widget: self.get_disabled_instructions_for_widget(w))
            widget.set_get_value_mapping_func(lambda w=widget: self.get_value_mapping_for_widget(w))
    
    def remove_last_value_widget(self):
        """删除最后一个值配置部件"""
        if len(self.value_widgets) > 0:
            widget = self.value_widgets.pop()
            widget.deleteLater()
            
            # 如果没有值部件了，显示提示标签
            if len(self.value_widgets) == 0 and hasattr(self, 'value_hint_label'):
                self.value_hint_label.show()
            
            # 触发配置变化，以更新所有值部件的禁用状态
            self.on_config_changed()
    
    def clear_all_value_widgets(self):
        """清空所有值定义"""
        if len(self.value_widgets) == 0:
            return
            
        reply = QMessageBox.question(
            self,
            "确认清空",
            f"确定要清空所有 {len(self.value_widgets)} 个值定义吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # 删除所有值部件
            for widget in self.value_widgets:
                widget.deleteLater()
            self.value_widgets.clear()
            
            # 显示提示标签
            if hasattr(self, 'value_hint_label'):
                self.value_hint_label.show()
            
            # 更新状态栏
            self.status_bar.showMessage("🗑️ 已清空所有值定义")
            
            # 清空代码预览
            self.ctrl_code_editor.clear()
            self.field_code_editor.clear()
            
            # 触发配置变化
            self.on_config_changed()
    
    def load_record_data(self, record):
        """加载记录数据到界面"""
        self.current_record = record
        
        # 设置基本配置
        self.signal_name_edit.setText(record.get('name', ''))
        
        encoding_type = record.get('encoding_type', 'OneHot')
        index = self.encoding_combo.findText(encoding_type)
        if index >= 0:
            self.encoding_combo.setCurrentIndex(index)
        
        # 清空现有值部件
        for widget in self.value_widgets:
            widget.deleteLater()
        self.value_widgets.clear()
        
        # 显示提示标签
        if hasattr(self, 'value_hint_label'):
            self.value_hint_label.show()
        
        # 添加值部件
        values = record.get('values', {})
        for value_name, instructions in values.items():
            # 隐藏提示标签
            if hasattr(self, 'value_hint_label'):
                self.value_hint_label.hide()
                
            widget = ValueConfigWidget(
                self,
                value_name,
                self.generator.instructions
            )
            widget.set_config(value_name, instructions)
            widget.config_changed.connect(self.on_config_changed)
            
            # 设置获取禁用指令的函数
            widget.set_get_disabled_instructions_func(lambda w=widget: self.get_disabled_instructions_for_widget(w))
            
            # 设置获取指令到值映射的函数
            widget.set_get_value_mapping_func(lambda w=widget: self.get_value_mapping_for_widget(w))
            
            self.value_container_layout.addWidget(widget)
            self.value_widgets.append(widget)
        
        # 如果没有任何值部件，确保提示标签显示
        if not self.value_widgets and hasattr(self, 'value_hint_label'):
            self.value_hint_label.show()
        
        # 生成并显示代码
        ctrl_code, field_code = self.generator.generate_chisel_code(record)
        self.ctrl_code_editor.setPlainText(ctrl_code)
        self.field_code_editor.setPlainText(field_code)
        
        self.status_bar.showMessage(f"✅ 已加载记录: {record['name']}")
    
    def generate_code(self):
        """生成代码"""
        # 验证信号名称
        signal_name = self.signal_name_edit.text().strip()
        if not signal_name:
            QMessageBox.warning(self, "警告", "请输入信号名称！")
            return
        
        # 收集值配置
        value_mapping = {}
        invalid_widgets = []
        
        # 检查指令是否重复
        all_instructions = set()
        duplicate_instructions = set()
        
        for i, widget in enumerate(self.value_widgets):
            config = widget.get_config()
            if widget.is_valid():
                value_mapping[config['name']] = config['instructions']
                
                # 检查指令重复
                for inst in config['instructions']:
                    if inst in all_instructions:
                        duplicate_instructions.add(inst)
                    all_instructions.add(inst)
            else:
                invalid_widgets.append(i + 1)
        
        # 修改：允许值为空，只要名称不为空就接受
        if not value_mapping:
            QMessageBox.warning(self, "警告", "请至少配置一个值！")
            return
        
        # 检查是否有指令重复
        if duplicate_instructions:
            duplicate_list = ", ".join(sorted(duplicate_instructions)[:5])
            if len(duplicate_instructions) > 5:
                duplicate_list += f" 等 {len(duplicate_instructions)} 条指令"
            
            QMessageBox.critical(
                self,
                "指令重复错误",
                f"以下指令在多个值中重复出现:\n{duplicate_list}\n\n请确保每条指令只出现在一个值中！"
            )
            return
        
        if invalid_widgets:
            reply = QMessageBox.question(
                self,
                "确认",
                f"值 #{', '.join(map(str, invalid_widgets))} 配置不完整，\n是否继续生成？"
            )
            if reply != QMessageBox.StandardButton.Yes:
                return
        
        # 创建控制信号
        encoding_type = self.encoding_combo.currentText()
        
        try:
            signal = self.generator.create_control_signal(
                signal_name,
                encoding_type,
                value_mapping
            )
            
            # 生成代码
            ctrl_code, field_code = self.generator.generate_chisel_code(signal)
            
            # 显示代码
            self.ctrl_code_editor.setPlainText(ctrl_code)
            self.field_code_editor.setPlainText(field_code)
            
            # 更新状态
            self.status_bar.showMessage(
                f"✅ 已生成控制信号 '{signal_name}'，包含 {len(value_mapping)} 个值"
            )
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"生成代码失败:\n{str(e)}")
    
    def copy_code(self):
        """复制当前标签页的代码到剪贴板"""
        current_index = self.code_tab_widget.currentIndex()
        
        if current_index == 0:  # Ctrl代码标签页
            code = self.ctrl_code_editor.toPlainText()
            code_type = "Ctrl"
        else:  # Field代码标签页
            code = self.field_code_editor.toPlainText()
            code_type = "Field"
            
        if not code.strip():
            QMessageBox.warning(self, "警告", f"没有{code_type}代码可复制！")
            return
        
        clipboard = QApplication.clipboard()
        clipboard.setText(code)
        
        self.status_bar.showMessage(f"✅ {code_type}代码已复制到剪贴板！")
    
    def save_all_files(self):
        """保存所有代码到文件 - 修改：添加覆盖选项"""
        ctrl_code = self.ctrl_code_editor.toPlainText()
        if not ctrl_code.strip():
            QMessageBox.warning(self, "警告", "没有Ctrl代码可保存！")
            return
        
        try:
            # 获取信号名称
            signal_name = self.signal_name_edit.text().strip()
            if not signal_name:
                signal_name = None
            
            # 获取Field代码
            field_code = self.field_code_editor.toPlainText()
            
            # 首先预测文件路径
            save_path = self.settings.value("ctrl_save_path", str(Path.home() / "riscv-scala" / "ctrl"))
            
            # 提取类名
            if signal_name:
                class_name = signal_name
            else:
                # 从代码中提取类名
                lines = ctrl_code.split('\n')
                for line in lines:
                    line = line.strip()
                    if line.startswith('object '):
                        parts = line.split()
                        if len(parts) >= 2:
                            name = parts[1]
                            if 'extends' in name:
                                name = name.split('extends')[0].strip()
                            if '(' in name:
                                name = name.split('(')[0].strip()
                            class_name = name.strip()
                            break
                else:
                    class_name = "ControlSignal"
            
            # 预测Ctrl文件路径
            ctrl_file_path = os.path.join(save_path, f"{class_name}.scala")
            
            # 检查文件是否存在
            overwrite = False
            if os.path.exists(ctrl_file_path):
                reply = QMessageBox.question(
                    self,
                    "文件已存在",
                    f"文件 {class_name}.scala 已存在，是否覆盖？\n选择'是'将覆盖原文件，选择'否'将生成新文件。",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel
                )
                
                if reply == QMessageBox.StandardButton.Cancel:
                    return  # 用户取消
                elif reply == QMessageBox.StandardButton.Yes:
                    overwrite = True
                else:
                    overwrite = False  # 不覆盖，生成新文件
            
            # 使用生成器保存文件
            ctrl_file_path, field_file_path = self.generator.save_scala_files(
                ctrl_code, field_code, signal_name, overwrite
            )
            
            # 显示保存结果
            message = f"✅ Ctrl文件已保存到:\n{ctrl_file_path}"
            if field_file_path:
                message += f"\n\n✅ Field文件已保存到:\n{field_file_path}"
            else:
                message += "\n\n⚠️ Field文件未生成（可能未启用自动生成Field文件）"
            
            QMessageBox.information(self, "成功", message)
            
            self.status_bar.showMessage(f"✅ 文件已保存: {ctrl_file_path}")
            
        except PermissionError as e:
            QMessageBox.critical(
                self,
                "权限错误",
                f"{str(e)}\n请尝试使用管理员权限运行程序。"
            )
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存文件失败:\n{str(e)}")
    
    def clear_code(self):
        """清空代码编辑器"""
        reply = QMessageBox.question(
            self,
            "确认清空",
            "确定要清空所有代码编辑器吗？"
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.ctrl_code_editor.clear()
            self.field_code_editor.clear()
            self.status_bar.showMessage("🗑️ 代码编辑器已清空")
    
    def show_settings(self):
        """显示设置对话框"""
        dialog = SettingsDialog(self)
        dialog.exec()
    
    def show_template_manager(self):
        """显示模板管理器"""
        dialog = TemplateManagerDialog(self)
        dialog.exec()
    
    def show_template_preview(self):
        """显示当前模板预览"""
        settings = QSettings("rvctrl-gender", "settings")
        ctrl_template = settings.value("chisel_ctrl_template", "")
        field_template = settings.value("chisel_field_template", "")
        
        if not ctrl_template:
            ctrl_template = """// ===========================================
// 自动生成的Chisel控制信号枚举类
// 生成时间: {generation_time}
// ===========================================

package rv.util.decoder

import chisel3._
import chisel3.util._
import rv.util.CtrlEnum

/**
  * {signal_name}Ctrl - 控制信号枚举类
  * 编码类型: {encoding_type}
  * 信号宽度: {signal_width} bits
  */
object {signal_name}Ctrl extends CtrlEnum(CtrlEnum.{encoding_type}) {
  // 值定义
{values_list}
  
  // 指令分类方法
{methods_list}
  
  // 辅助方法
  def getAllValues: Seq[UInt] = this.Values
  
  def getWidth: Int = this.getWidth
}"""
        
        if not field_template:
            field_template = """package rv.util.decoder

import chisel3._
import chisel3.util._
import chisel3.util.experimental.decode._

object {signal_name}Field extends DecodeField[InstructionPattern, UInt] {
  override def name: String = "{signal_name}Field"
  override def chiselType: UInt = UInt({signal_name}Ctrl.getWidth.W)
  private def map: Seq[(Seq[String], UInt)] = Seq(
{value_mappings}
  )
  override def genTable(op: InstructionPattern): BitPat = {
    BitPat(op.nameMatch(map, 0.U({signal_name}Ctrl.getWidth.W)))
  }
}"""
        
        dialog = QDialog(self)
        dialog.setWindowTitle("当前代码模板")
        dialog.setModal(True)
        dialog.resize(750, 550)
        
        # 加载当前主题
        current_theme = self.settings.value("current_theme", "light", type=str)
        
        layout = QVBoxLayout()
        
        # 创建标签页
        tab_widget = QTabWidget()
        
        # Ctrl模板标签页
        ctrl_tab = QWidget()
        ctrl_layout = QVBoxLayout()
        
        ctrl_template_edit = QPlainTextEdit()
        ctrl_template_edit.setFont(QFont("Monospace", 11))
        ctrl_template_edit.setPlainText(ctrl_template)
        ctrl_template_edit.setReadOnly(True)
        ctrl_layout.addWidget(ctrl_template_edit)
        
        # Ctrl占位符说明
        ctrl_desc_label = QLabel(
            "📝 Ctrl模板可用占位符:\n"
            "  {signal_name} - 信号名称\n"
            "  {encoding_type} - 编码类型\n"
            "  {values_list} - 值定义列表\n"
            "  {methods_list} - 指令方法列表\n"
            "  {signal_width} - 信号宽度\n"
            "  {generation_time} - 生成时间"
        )
        if current_theme == "dark":
            ctrl_desc_label.setStyleSheet("""
                color: #e0e0e0; 
                background-color: #3c3c3c; 
                padding: 12px; 
                border-radius: 6px;
                border: 2px solid #555555;
                font-weight: bold;
                font-size: 13px;
            """)
        else:
            ctrl_desc_label.setStyleSheet("""
                color: #2c3e50; 
                background-color: #f8f9fa; 
                padding: 12px; 
                border-radius: 6px;
                border: 2px solid #dee2e6;
                font-weight: bold;
                font-size: 13px;
            """)
        ctrl_layout.addWidget(ctrl_desc_label)
        
        ctrl_tab.setLayout(ctrl_layout)
        
        # Field模板标签页
        field_tab = QWidget()
        field_layout = QVBoxLayout()
        
        field_template_edit = QPlainTextEdit()
        field_template_edit.setFont(QFont("Monospace", 11))
        field_template_edit.setPlainText(field_template)
        field_template_edit.setReadOnly(True)
        field_layout.addWidget(field_template_edit)
        
        # Field占位符说明
        field_desc_label = QLabel(
            "📝 Field模板可用占位符:\n"
            "  {signal_name} - 信号名称\n"
            "  {encoding_type} - 编码类型\n"
            "  {signal_width} - 信号宽度\n"
            "  {values_list} - 值列表\n"
            "  {value_mappings} - 值映射列表\n"
            "  {generation_time} - 生成时间"
        )
        if current_theme == "dark":
            field_desc_label.setStyleSheet("""
                color: #e0e0e0; 
                background-color: #3c3c3c; 
                padding: 12px; 
                border-radius: 6px;
                border: 2px solid #555555;
                font-weight: bold;
                font-size: 13px;
            """)
        else:
            field_desc_label.setStyleSheet("""
                color: #2c3e50; 
                background-color: #f8f9fa; 
                padding: 12px; 
                border-radius: 6px;
                border: 2px solid #dee2e6;
                font-weight: bold;
                font-size: 13px;
            """)
        field_layout.addWidget(field_desc_label)
        
        field_tab.setLayout(field_layout)
        
        # 添加标签页
        tab_widget.addTab(ctrl_tab, "Ctrl模板")
        tab_widget.addTab(field_tab, "Field模板")
        
        layout.addWidget(tab_widget)
        
        # 按钮
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)
        
        dialog.setLayout(layout)
        dialog.exec()
    
    def show_record_manager(self):
        """显示记录管理器"""
        dialog = RecordManagerDialog(self, self.generator)
        dialog.record_selected.connect(self.load_record_data)
        dialog.exec()
    
    def closeEvent(self, event):
        """关闭事件"""
        reply = QMessageBox.question(
            self,
            "确认退出",
            "确定要退出程序吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            event.accept()
        else:
            event.ignore()

def main():
    """主函数"""
    app = QApplication(sys.argv)
    app.setApplicationName("RISC-V Ctrl Generator")
    app.setOrganizationName("RISCV")
    
    # 设置应用程序样式
    app.setStyle("Fusion")
    
    # 加载设置
    settings = QSettings("rvctrl-gender", "settings")
    current_theme = settings.value("current_theme", "light", type=str)
    
    # 设置应用程序调色板
    palette = QPalette()
    if current_theme == "dark":
        # 暗色主题调色板
        palette.setColor(QPalette.ColorRole.Window, QColor(45, 45, 45))  # 深灰色背景
        palette.setColor(QPalette.ColorRole.WindowText, QColor(224, 224, 224))  # 浅灰色文本
        palette.setColor(QPalette.ColorRole.Base, QColor(60, 60, 60))  # 深灰色输入框背景
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(51, 51, 51))  # 更深的灰色交替背景
        palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(60, 60, 60))  # 深灰色工具提示背景
        palette.setColor(QPalette.ColorRole.ToolTipText, QColor(224, 224, 224))  # 浅灰色工具提示文本
        palette.setColor(QPalette.ColorRole.Text, QColor(224, 224, 224))  # 浅灰色文本颜色
        palette.setColor(QPalette.ColorRole.Button, QColor(60, 60, 60))  # 深灰色按钮背景
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(224, 224, 224))  # 浅灰色按钮文本
        palette.setColor(QPalette.ColorRole.BrightText, QColor(74, 158, 255))  # 亮蓝色文本
        palette.setColor(QPalette.ColorRole.Highlight, QColor(74, 158, 255))  # 蓝色高亮色
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))  # 白色高亮文本
        palette.setColor(QPalette.ColorRole.Link, QColor(74, 158, 255))  # 蓝色链接颜色
        palette.setColor(QPalette.ColorRole.LinkVisited, QColor(58, 126, 255))  # 深蓝色访问过的链接
    else:
        # 亮色主题调色板
        palette.setColor(QPalette.ColorRole.Window, QColor(255, 255, 255))  # 白色背景
        palette.setColor(QPalette.ColorRole.WindowText, QColor(44, 62, 80))  # 深蓝色文本
        palette.setColor(QPalette.ColorRole.Base, QColor(255, 255, 255))  # 白色输入框背景
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(248, 249, 250))  # 浅灰色交替背景
        palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(255, 255, 255))  # 白色工具提示背景
        palette.setColor(QPalette.ColorRole.ToolTipText, QColor(44, 62, 80))  # 深蓝色工具提示文本
        palette.setColor(QPalette.ColorRole.Text, QColor(44, 62, 80))  # 深蓝色文本颜色
        palette.setColor(QPalette.ColorRole.Button, QColor(248, 249, 250))  # 浅灰色按钮背景
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(44, 62, 80))  # 深蓝色按钮文本
        palette.setColor(QPalette.ColorRole.BrightText, QColor(52, 152, 219))  # 亮蓝色文本
        palette.setColor(QPalette.ColorRole.Highlight, QColor(52, 152, 219))  # 蓝色高亮色
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))  # 白色高亮文本
        palette.setColor(QPalette.ColorRole.Link, QColor(52, 152, 219))  # 蓝色链接颜色
        palette.setColor(QPalette.ColorRole.LinkVisited, QColor(41, 128, 185))  # 深蓝色访问过的链接
    
    app.setPalette(palette)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
