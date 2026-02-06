"""
File: creative_controls.py
Creation Date: 2026-01-05
Description: Top toolbar for creative tools.
"""

from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QButtonGroup, QLabel, QComboBox
from PySide6.QtCore import Signal
from _01_core_logic.creative_state import CreativeStoneType

class CreativeControls(QWidget):
    tool_changed = Signal(str) # Tool Name
    stone_type_changed = Signal(object) # Stone Type Enum
    action_triggered = Signal(str) # Action Name (Reset, Screenshot, etc)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(70)
        
        # Modern Dark Toolbar Styling
        self.setStyleSheet("""
            QWidget {
                background-color: #1e1e24;
                border-bottom: 2px solid #2b2b35;
                font-family: 'Segoe UI', sans-serif;
            }
            QLabel {
                color: #e94560;
                font-size: 18px;
                font-weight: 800;
                padding-left: 15px;
            }
            QPushButton {
                background-color: #2b2b35;
                border: 1px solid #3a3a45;
                border-radius: 6px;
                color: #e0e0e0;
                font-weight: 600;
                padding: 8px 16px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #3a3a45;
                border-color: #e94560;
                color: #ffffff;
            }
            QPushButton:pressed {
                background-color: #16213e;
            }
            QPushButton:checked {
                background-color: #e94560;
                border-color: #e94560;
                color: #ffffff;
            }
            QComboBox {
                background-color: #2b2b35;
                border: 1px solid #3a3a45;
                border-radius: 6px;
                color: #e0e0e0;
                padding: 5px 10px;
                min-width: 120px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: #2b2b35;
                color: #e0e0e0;
                selection-background-color: #e94560;
            }
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 10, 20, 10)
        layout.setSpacing(12)
        
        # Title
        title = QLabel("GEO LUMINAMICS")
        layout.addWidget(title)
        
        # Tool Group
        self.tool_group = QButtonGroup(self)
        self.tool_group.setExclusive(True)
        
        # Tools with Icons
        self.btn_select = self._add_tool_btn("👆 Select", "SELECT", True)
        self.btn_laser = self._add_tool_btn("🔫 Laser", "PLACE_LASER")
        self.btn_stone = self._add_tool_btn("💎 Stone", "PLACE_STONE")
        
        layout.addWidget(self.btn_select)
        layout.addWidget(self.btn_laser)
        layout.addWidget(self.btn_stone)
        
        # Stone Type Selector
        self.stone_combo = QComboBox()
        self.stone_combo.addItems(["PRISM", "MIRROR", "SPLITTER", "STOP"])
        self.stone_combo.currentTextChanged.connect(self._on_stone_type_changed)
        layout.addWidget(self.stone_combo)
        
        layout.addStretch()
        
        # Actions
        btn_clear = QPushButton("🗑️ Clear")
        btn_clear.clicked.connect(lambda: self.action_triggered.emit("CLEAR"))
        layout.addWidget(btn_clear)
        
        btn_save = QPushButton("💾 Save")
        btn_save.clicked.connect(lambda: self.action_triggered.emit("SAVE"))
        layout.addWidget(btn_save)
        
        btn_load = QPushButton("📂 Load")
        btn_load.clicked.connect(lambda: self.action_triggered.emit("LOAD"))
        layout.addWidget(btn_load)

        
        btn_shot = QPushButton("📷 Shot")
        btn_shot.clicked.connect(lambda: self.action_triggered.emit("SCREENSHOT"))
        layout.addWidget(btn_shot)

    def _add_tool_btn(self, text, tool_id, checked=False):
        btn = QPushButton(text)
        btn.setCheckable(True)
        btn.setChecked(checked)
        btn.clicked.connect(lambda: self.tool_changed.emit(tool_id))
        self.tool_group.addButton(btn)
        return btn

    def _on_stone_type_changed(self, text):
        try:
            val = CreativeStoneType[text]
            self.stone_type_changed.emit(val)
        except:
            pass
