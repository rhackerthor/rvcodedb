NIGHT_QSS = """
QMainWindow { background-color: #242530; }
QWidget { color: #9b9eb0; }

QLabel { color: #9b9eb0; }

QGroupBox {
    color: #9b9eb0;
    border: 1px solid #1c1c22;
    border-radius: 4px;
    margin-top: 1em;
    padding-top: 8px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 4px;
    color: #7d8ab5;
}

QComboBox {
    background-color: #1c1c24;
    color: #9b9eb0;
    border: 1px solid #1a1a20;
    padding: 2px 6px;
    border-radius: 3px;
}
QComboBox:editable { background-color: #1c1c24; }
QComboBox QAbstractItemView {
    background-color: #1f202a;
    color: #9b9eb0;
    selection-background-color: #4a5a8a;
    border: 1px solid #1c1c22;
}

QPushButton {
    background-color: #4a5a8a;
    color: #c8ccd4;
    border: none;
    padding: 4px 12px;
    border-radius: 3px;
}
QPushButton:hover { background-color: #5a6a9a; }
QPushButton:pressed { background-color: #3a4a7a; }
QPushButton:disabled { background-color: #2e2e3c; color: #56576a; }

QLineEdit {
    background-color: #1c1c24;
    color: #9b9eb0;
    border: 1px solid #1a1a20;
    padding: 3px 6px;
    border-radius: 3px;
}
QLineEdit:focus { border-color: #4a5a8a; }

QTreeWidget, QListWidget {
    background-color: #1f202a;
    color: #9b9eb0;
    border: 1px solid #1c1c22;
    outline: none;
}
QTreeWidget::item:selected, QListWidget::item:selected {
    background-color: #4a5a8a;
}
QTreeWidget::item:hover, QListWidget::item:hover {
    background-color: #2a2c38;
}
QHeaderView::section {
    background-color: #1f202a;
    color: #6e7080;
    border: none;
    border-bottom: 1px solid #1c1c22;
    padding: 4px 8px;
}

QPlainTextEdit, QTextEdit {
    background-color: #242530;
    color: #9b9eb0;
    border: 1px solid #1c1c22;
    font-family: "JetBrains Mono", "Fira Code", "Cascadia Code", monospace;
    font-size: 12px;
}

QScrollBar:vertical {
    background-color: #1f202a;
    width: 10px;
    border: none;
}
QScrollBar::handle:vertical {
    background-color: #44475a;
    min-height: 20px;
    border-radius: 5px;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }

QScrollBar:horizontal {
    background-color: #1f202a;
    height: 10px;
    border: none;
}
QScrollBar::handle:horizontal {
    background-color: #44475a;
    min-width: 20px;
    border-radius: 5px;
}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }

QScrollArea { background-color: #1f202a; border: none; }

QStatusBar {
    background-color: #1f202a;
    color: #6e7080;
    border-top: 1px solid #1c1c22;
}

QMenuBar {
    background-color: #1f202a;
    color: #9b9eb0;
    border-bottom: 1px solid #1c1c22;
}
QMenuBar::item:selected {
    background-color: #4a5a8a;
}
QMenu {
    background-color: #1f202a;
    color: #9b9eb0;
    border: 1px solid #1c1c22;
}
QMenu::item:selected {
    background-color: #4a5a8a;
}

QCheckBox {
    color: #9b9eb0;
    spacing: 6px;
}
QCheckBox::indicator {
    width: 14px;
    height: 14px;
    border: 1px solid #44475a;
    border-radius: 2px;
    background-color: #1c1c24;
}
QCheckBox::indicator:checked {
    background-color: #4a5a8a;
    border-color: #4a5a8a;
}

QToolButton {
    background-color: #4a5a8a;
    color: #c8ccd4;
    border: none;
    padding: 3px 8px;
    border-radius: 3px;
}
QToolButton:hover { background-color: #5a6a9a; }

QTabWidget::pane {
    border: 1px solid #1c1c22;
    background-color: #242530;
}
QTabBar::tab {
    background-color: #1f202a;
    color: #6e7080;
    padding: 6px 14px;
    border: 1px solid #1c1c22;
    border-bottom: none;
}
QTabBar::tab:selected {
    background-color: #242530;
    color: #9b9eb0;
    border-bottom: 2px solid #4a5a8a;
}
"""

DAY_QSS = """
QMainWindow { background-color: #e1e2e7; }
QWidget { color: #3760bf; }

QLabel { color: #3760bf; }

QGroupBox {
    color: #3760bf;
    border: 1px solid #b4b5b9;
    border-radius: 4px;
    margin-top: 1em;
    padding-top: 8px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 4px;
    color: #2e7de9;
}

QComboBox {
    background-color: #f0f1f5;
    color: #3760bf;
    border: 1px solid #b4b5b9;
    padding: 2px 6px;
    border-radius: 3px;
}
QComboBox:editable { background-color: #f0f1f5; }
QComboBox QAbstractItemView {
    background-color: #d0d5e3;
    color: #3760bf;
    selection-background-color: #4094a3;
    border: 1px solid #b4b5b9;
}

QPushButton {
    background-color: #4094a3;
    color: #ffffff;
    border: none;
    padding: 4px 12px;
    border-radius: 3px;
}
QPushButton:hover { background-color: #50a4b3; }
QPushButton:pressed { background-color: #308493; }
QPushButton:disabled { background-color: #c0c5d0; color: #848cb5; }

QLineEdit {
    background-color: #f0f1f5;
    color: #3760bf;
    border: 1px solid #b4b5b9;
    padding: 3px 6px;
    border-radius: 3px;
}
QLineEdit:focus { border-color: #4094a3; }

QTreeWidget, QListWidget {
    background-color: #d0d5e3;
    color: #3760bf;
    border: 1px solid #b4b5b9;
    outline: none;
}
QTreeWidget::item:selected, QListWidget::item:selected {
    background-color: #4094a3;
    color: #ffffff;
}
QTreeWidget::item:hover, QListWidget::item:hover {
    background-color: #c4c8da;
}
QHeaderView::section {
    background-color: #d0d5e3;
    color: #6172b0;
    border: none;
    border-bottom: 1px solid #b4b5b9;
    padding: 4px 8px;
}

QPlainTextEdit, QTextEdit {
    background-color: #e1e2e7;
    color: #3760bf;
    border: 1px solid #b4b5b9;
    font-family: "JetBrains Mono", "Fira Code", "Cascadia Code", monospace;
    font-size: 12px;
}

QScrollBar:vertical {
    background-color: #d0d5e3;
    width: 10px;
    border: none;
}
QScrollBar::handle:vertical {
    background-color: #a8aecb;
    min-height: 20px;
    border-radius: 5px;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }

QScrollBar:horizontal {
    background-color: #d0d5e3;
    height: 10px;
    border: none;
}
QScrollBar::handle:horizontal {
    background-color: #a8aecb;
    min-width: 20px;
    border-radius: 5px;
}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }

QScrollArea { background-color: #d0d5e3; border: none; }

QStatusBar {
    background-color: #d0d5e3;
    color: #6172b0;
    border-top: 1px solid #b4b5b9;
}

QMenuBar {
    background-color: #d0d5e3;
    color: #3760bf;
    border-bottom: 1px solid #b4b5b9;
}
QMenuBar::item:selected {
    background-color: #4094a3;
    color: #ffffff;
}
QMenu {
    background-color: #d0d5e3;
    color: #3760bf;
    border: 1px solid #b4b5b9;
}
QMenu::item:selected {
    background-color: #4094a3;
    color: #ffffff;
}

QCheckBox {
    color: #3760bf;
    spacing: 6px;
}
QCheckBox::indicator {
    width: 14px;
    height: 14px;
    border: 1px solid #a8aecb;
    border-radius: 2px;
    background-color: #f0f1f5;
}
QCheckBox::indicator:checked {
    background-color: #4094a3;
    border-color: #4094a3;
}

QToolButton {
    background-color: #4094a3;
    color: #ffffff;
    border: none;
    padding: 3px 8px;
    border-radius: 3px;
}
QToolButton:hover { background-color: #50a4b3; }

QTabWidget::pane {
    border: 1px solid #b4b5b9;
    background-color: #e1e2e7;
}
QTabBar::tab {
    background-color: #d0d5e3;
    color: #6172b0;
    padding: 6px 14px;
    border: 1px solid #b4b5b9;
    border-bottom: none;
}
QTabBar::tab:selected {
    background-color: #e1e2e7;
    color: #3760bf;
    border-bottom: 2px solid #4094a3;
}
"""

THEMES = {"night": NIGHT_QSS, "day": DAY_QSS}
