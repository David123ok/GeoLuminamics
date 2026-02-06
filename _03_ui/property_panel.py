"""
File: property_panel.py
Creation Date: 2026-01-05
Description: Sidebar panel for editing properties of the selected object.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSlider, QDoubleSpinBox, QPushButton, QColorDialog, QGroupBox, QFormLayout, QFileDialog, QCheckBox
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from _01_core_logic.creative_state import CreativeStoneData, CreativeLaserData

class PropertyPanel(QWidget):
    property_changed = Signal() # Emitted when any property is modified
    delete_requested = Signal(object) # Emitted with item to delete
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(320)
        
        # Rich dark theme with gradients
        self.setStyleSheet("""
            QWidget {
                background-color: #1a1a2e;
                color: #eaeaea;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QGroupBox {
                background-color: #16213e;
                border: 1px solid #0f3460;
                border-radius: 8px;
                margin-top: 12px;
                padding: 10px;
                font-weight: bold;
                color: #e94560;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: #e94560;
            }
            QPushButton {
                background-color: #0f3460;
                border: none;
                border-radius: 6px;
                padding: 8px 12px;
                color: #eaeaea;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e94560;
            }
            QPushButton:pressed {
                background-color: #533483;
            }
            QSlider::groove:horizontal {
                border: 1px solid #0f3460;
                height: 8px;
                background: #16213e;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #e94560;
                border: none;
                width: 16px;
                margin: -4px 0;
                border-radius: 8px;
            }
            QSlider::handle:horizontal:hover {
                background: #ff6b6b;
            }
            QDoubleSpinBox, QSpinBox {
                background-color: #16213e;
                border: 1px solid #0f3460;
                border-radius: 4px;
                padding: 4px;
                color: #eaeaea;
            }
            QCheckBox {
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 4px;
                border: 2px solid #0f3460;
                background-color: #16213e;
            }
            QCheckBox::indicator:checked {
                background-color: #e94560;
                border-color: #e94560;
            }
            QLabel {
                color: #a0a0a0;
            }
        """)
        
        self.current_item = None
        
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(12, 12, 12, 12)
        
        # Header
        self.header_label = QLabel("No Selection")
        self.header_label.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #ffffff;
            padding-bottom: 8px;
            border-bottom: 2px solid #e94560;
        """)
        layout.addWidget(self.header_label)
        
        # --- Common Properties (Pos, Color, Texture) ---
        self.common_group = QGroupBox("Properties")
        common_layout = QFormLayout(self.common_group)
        
        # Position (Hide for Board)
        self.pos_group = QWidget()
        pos_layout = QFormLayout(self.pos_group)
        pos_layout.setContentsMargins(0,0,0,0)
        self.x_spin = QDoubleSpinBox()
        self.y_spin = QDoubleSpinBox()
        self.x_spin.valueChanged.connect(self._on_change)
        self.y_spin.valueChanged.connect(self._on_change)
        pos_layout.addRow("X:", self.x_spin)
        pos_layout.addRow("Y:", self.y_spin)
        common_layout.addRow(self.pos_group)
        
        # Color
        self.color_btn = QPushButton("Choose Color")
        self.color_btn.clicked.connect(self._pick_color)
        self.color_preview = QLabel()
        self.color_preview.setFixedSize(30,30)
        self.color_preview.setStyleSheet("background-color: #FFFFFF; border: 1px solid #555;")
        
        color_row = QWidget()
        h = QVBoxLayout(color_row) 
        h.addWidget(self.color_preview)
        h.addWidget(self.color_btn)
        common_layout.addRow("Color:", color_row)
        
        # Texture
        self.texture_btn = QPushButton("Load Texture...")
        self.texture_btn.clicked.connect(self._load_texture)
        self.clear_texture_btn = QPushButton("Clear Texture")
        self.clear_texture_btn.clicked.connect(self._clear_texture)
        self.texture_label = QLabel("None")
        common_layout.addRow("Texture:", self.texture_btn)
        common_layout.addRow("", self.clear_texture_btn)
        common_layout.addRow("Current:", self.texture_label)
        
        layout.addWidget(self.common_group)
        
        # --- Type Specific Properties ---
        
        # Stone Props
        self.stone_group = QGroupBox("Stone Effects")
        stone_layout = QFormLayout(self.stone_group)
        
        # Animation
        self.anim_check = QCheckBox("Animate Rotation")
        self.anim_check.clicked.connect(self._on_change)
        stone_layout.addRow(self.anim_check)
        
        self.anim_speed_spin = QDoubleSpinBox()
        self.anim_speed_spin.setRange(-20, 20)
        self.anim_speed_spin.setSingleStep(0.1)
        self.anim_speed_spin.valueChanged.connect(self._on_change)
        stone_layout.addRow("Speed:", self.anim_speed_spin)

        self.stone_bloom_slider = QSlider(Qt.Horizontal)
        self.stone_bloom_slider.setRange(0, 200) # 0.0 to 2.0
        self.stone_bloom_slider.valueChanged.connect(self._on_change)
        stone_layout.addRow("Bloom:", self.stone_bloom_slider)

        self.stone_glow_slider = QSlider(Qt.Horizontal)
        self.stone_glow_slider.setRange(0, 200)
        self.stone_glow_slider.valueChanged.connect(self._on_change)
        stone_layout.addRow("Glow:", self.stone_glow_slider)
        
        self.rotation_spin = QDoubleSpinBox()
        self.rotation_spin.setRange(0, 360)
        self.rotation_spin.valueChanged.connect(self._on_change)
        stone_layout.addRow("Rotation:", self.rotation_spin)
        
        layout.addWidget(self.stone_group)

        # Environment (Board) Props - Dynamically shown when Board selected
        self.env_group = QGroupBox("Environment")
        env_layout = QFormLayout(self.env_group)
        
        self.sky_top_btn = QPushButton("Sky Top")
        self.sky_top_btn.clicked.connect(lambda: self._pick_env_color("top"))
        self.sky_bot_btn = QPushButton("Sky Bottom")
        self.sky_bot_btn.clicked.connect(lambda: self._pick_env_color("bot"))
        env_layout.addRow(self.sky_top_btn, self.sky_bot_btn)
        
        self.atm_slider = QSlider(Qt.Horizontal)
        self.atm_slider.setRange(0, 100) # 0.0 to 1.0
        self.atm_slider.valueChanged.connect(self._on_change)
        env_layout.addRow("Atmosphere:", self.atm_slider)
        
        self.atm_color_btn = QPushButton("Atm Color")
        self.atm_color_btn.clicked.connect(lambda: self._pick_env_color("atm"))
        env_layout.addRow(self.atm_color_btn)
        
        # Gradient Type Toggle
        self.grad_toggle_btn = QPushButton("Toggle: Radial")
        self.grad_toggle_btn.clicked.connect(self._toggle_gradient_type)
        env_layout.addRow("Sky Gradient:", self.grad_toggle_btn)
        
        layout.addWidget(self.env_group)
        
        # Laser Props
        self.laser_group = QGroupBox("Laser Settings")
        laser_layout = QFormLayout(self.laser_group)
        
        # Animation
        self.laser_anim_check = QCheckBox("Animate Direction")
        self.laser_anim_check.clicked.connect(self._on_change)
        laser_layout.addRow(self.laser_anim_check)
        
        self.laser_anim_speed = QDoubleSpinBox()
        self.laser_anim_speed.setRange(-20, 20)
        self.laser_anim_speed.setSingleStep(0.5)
        self.laser_anim_speed.valueChanged.connect(self._on_change)
        laser_layout.addRow("Rotation Speed:", self.laser_anim_speed)
        
        self.intensity_slider = QSlider(Qt.Horizontal)
        self.intensity_slider.setRange(0, 200)
        self.intensity_slider.valueChanged.connect(self._on_change)
        laser_layout.addRow("Intensity:", self.intensity_slider)

        self.laser_bloom_slider = QSlider(Qt.Horizontal)
        self.laser_bloom_slider.setRange(0, 200)
        self.laser_bloom_slider.valueChanged.connect(self._on_change)
        laser_layout.addRow("Bloom:", self.laser_bloom_slider)

        self.laser_glow_slider = QSlider(Qt.Horizontal)
        self.laser_glow_slider.setRange(0, 200)
        self.laser_glow_slider.valueChanged.connect(self._on_change)
        laser_layout.addRow("Glow:", self.laser_glow_slider)
        
        self.direction_x = QDoubleSpinBox()
        self.direction_y = QDoubleSpinBox()
        self.direction_x.setRange(-1, 1)
        self.direction_y.setRange(-1, 1)
        self.direction_x.setSingleStep(0.1)
        self.direction_y.setSingleStep(0.1)
        self.direction_x.valueChanged.connect(self._on_change)
        self.direction_y.valueChanged.connect(self._on_change)
        
        laser_layout.addRow("Dir X:", self.direction_x)
        laser_layout.addRow("Dir Y:", self.direction_y)
        layout.addWidget(self.laser_group)
        
        # Delete Button
        self.delete_btn = QPushButton("🗑️ Delete Selected")
        self.delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #8B0000;
                color: white;
                font-weight: bold;
                padding: 10px;
                margin-top: 10px;
            }
            QPushButton:hover {
                background-color: #FF4444;
            }
        """)
        self.delete_btn.clicked.connect(self._delete_item)
        self.delete_btn.hide()
        layout.addWidget(self.delete_btn)
        
        layout.addStretch()
        
        # Hide groups initially
        self.stone_group.hide()
        self.laser_group.hide()
        
        self._is_updating_ui = False

    def load_item(self, item):
        """Load data into panel. item can be single object or list for multi-select."""
        self._is_updating_ui = True
        
        # Handle multi-selection
        if isinstance(item, list):
            self.current_item = item  # Store list
            count = len(item)
            self.header_label.setText(f"{count} Items Selected")
            self.common_group.hide()
            self.stone_group.hide()
            self.laser_group.hide()
            self.env_group.hide()
            self.delete_btn.show()  # Allow batch delete
            self._is_updating_ui = False
            return
        
        self.current_item = item
        
        if item is None:
             self.header_label.setText("No Selection")
             self.common_group.hide()
             self.stone_group.hide()
             self.laser_group.hide()
             self.env_group.hide()
             self.delete_btn.hide()
             self._is_updating_ui = False
             return
        
        # Determine Type
        self.common_group.show()
        
        # Helper to set text with limit
        def set_tex_label(path):
            if path:
                txt = path if len(path) < 20 else "..." + path[-20:]
                self.texture_label.setText(txt)
            else:
                self.texture_label.setText("None")

        from _01_core_logic.creative_state import CreativeState
        
        if isinstance(item, CreativeState):
            self.header_label.setText("Board Settings")
            self.pos_group.hide()
            self.stone_group.hide()
            self.laser_group.hide()
            self.env_group.show()
            self.delete_btn.hide()  # Can't delete board
            
            # Update gradient toggle text
            self.grad_toggle_btn.setText(f"Toggle: {item.sky_gradient_type.capitalize()}")
            
            # Use color picker for simple BG or gradient top? 
            # common_group color button will map to sky_top or background_color based on logic?
            # Let's map "Color" in common to BACKGROUND_COLOR (legacy) but allow Env panel for full sky.
            self.color_preview.setStyleSheet(f"background-color: {item.background_color}; border: 1px solid #555;")
            set_tex_label(item.background_texture_path)
            
            self.atm_slider.setValue(int(item.atmosphere_density * 100))
            
        elif isinstance(item, CreativeStoneData):
            self.header_label.setText(f"Stone: {item.stone_type.name}")
            self.pos_group.show()
            self.stone_group.show()
            self.laser_group.hide()
            self.env_group.hide()
            self.delete_btn.show()  # Allow delete
            
            self.x_spin.setValue(item.x)
            self.y_spin.setValue(item.y)
            self.color_preview.setStyleSheet(f"background-color: {item.color}; border: 1px solid #555;")
            set_tex_label(item.texture_path)
            
            self.anim_check.setChecked(item.is_animating)
            self.anim_speed_spin.setValue(item.rotation_speed)
            self.stone_bloom_slider.setValue(int(item.bloom_intensity * 100))
            self.stone_glow_slider.setValue(int(item.glow_intensity * 100))
            self.rotation_spin.setValue(item.rotation)
            
        elif isinstance(item, CreativeLaserData):
            self.header_label.setText("Laser Source")
            self.pos_group.show()
            self.stone_group.hide()
            self.laser_group.show()
            self.env_group.hide()
            self.delete_btn.show()  # Allow delete
            
            self.x_spin.setValue(item.x)
            self.y_spin.setValue(item.y)
            self.color_preview.setStyleSheet(f"background-color: {item.color}; border: 1px solid #555;")
            set_tex_label("N/A")
            
            self.laser_anim_check.setChecked(item.is_animating)
            self.laser_anim_speed.setValue(item.rotation_speed)
            self.intensity_slider.setValue(int(item.intensity * 100))
            self.laser_bloom_slider.setValue(int(item.bloom_intensity * 100))
            self.laser_glow_slider.setValue(int(item.glow_intensity * 100))
            self.direction_x.setValue(item.direction[0])
            self.direction_y.setValue(item.direction[1])
            
        self._is_updating_ui = False

    def _on_change(self):
        """Apply changes from UI to data."""
        if self._is_updating_ui or not self.current_item:
            return
            
        item = self.current_item
        from _01_core_logic.creative_state import CreativeState

        if isinstance(item, CreativeState):
            item.atmosphere_density = self.atm_slider.value() / 100.0
        else:
            item.x = self.x_spin.value()
            item.y = self.y_spin.value()
        
        if isinstance(item, CreativeStoneData):
            item.is_animating = self.anim_check.isChecked()
            item.rotation_speed = self.anim_speed_spin.value()
            item.bloom_intensity = self.stone_bloom_slider.value() / 100.0
            item.glow_intensity = self.stone_glow_slider.value() / 100.0
            item.rotation = self.rotation_spin.value()
            
        elif isinstance(item, CreativeLaserData):
            item.is_animating = self.laser_anim_check.isChecked()
            item.rotation_speed = self.laser_anim_speed.value()
            item.intensity = self.intensity_slider.value() / 100.0
            item.bloom_intensity = self.laser_bloom_slider.value() / 100.0
            item.glow_intensity = self.laser_glow_slider.value() / 100.0
            item.direction = (self.direction_x.value(), self.direction_y.value())
            
        self.property_changed.emit()

    def _pick_color(self):
        if not self.current_item: return
        
        # Get start color
        from _01_core_logic.creative_state import CreativeState
        if isinstance(self.current_item, CreativeState):
            start = self.current_item.background_color
        else:
            start = self.current_item.color
            
        color = QColorDialog.getColor(QColor(start), self, "Select Color")
        if color.isValid():
            c_str = color.name()
            if isinstance(self.current_item, CreativeState):
                self.current_item.background_color = c_str
                # By default also set sky top/bot to this if we consider "Color" as simple BG
                # self.current_item.sky_color_top = c_str
                # self.current_item.sky_color_bottom = c_str
            else:
                self.current_item.color = c_str
                
            self.color_preview.setStyleSheet(f"background-color: {c_str}; border: 1px solid #555;")
            self.property_changed.emit()

    def _pick_env_color(self, target):
        if not self.current_item: return
        from _01_core_logic.creative_state import CreativeState
        if not isinstance(self.current_item, CreativeState): return
        
        start = "#FFFFFF"
        if target == "top": start = self.current_item.sky_color_top
        elif target == "bot": start = self.current_item.sky_color_bottom
        elif target == "atm": start = self.current_item.atmosphere_color
        
        color = QColorDialog.getColor(QColor(start), self, "Select Environment Color")
        if color.isValid():
            c_str = color.name()
            if target == "top": self.current_item.sky_color_top = c_str
            elif target == "bot": self.current_item.sky_color_bottom = c_str
            elif target == "atm": self.current_item.atmosphere_color = c_str
            self.property_changed.emit()

    def _toggle_gradient_type(self):
        if not self.current_item: return
        from _01_core_logic.creative_state import CreativeState
        if not isinstance(self.current_item, CreativeState): return
        
        # Toggle between radial and linear
        if self.current_item.sky_gradient_type == "radial":
            self.current_item.sky_gradient_type = "linear"
            self.grad_toggle_btn.setText("Toggle: Linear")
        else:
            self.current_item.sky_gradient_type = "radial"
            self.grad_toggle_btn.setText("Toggle: Radial")
        
        self.property_changed.emit()
    def _load_texture(self):
        if not self.current_item: return
        
        from _01_core_logic.creative_state import CreativeState
        # Allow texture for Board (CreativeState) and Stone
        if isinstance(self.current_item, CreativeLaserData): return

        file_name, _ = QFileDialog.getOpenFileName(self, "Load Texture", "", "Images (*.png *.jpg *.jpeg)")
        if file_name:
            if isinstance(self.current_item, CreativeState):
                 self.current_item.background_texture_path = file_name
            else:
                 self.current_item.texture_path = file_name
            
            txt = file_name if len(file_name) < 20 else "..." + file_name[-20:]
            self.texture_label.setText(txt)
            self.property_changed.emit()

    def _clear_texture(self):
        if not self.current_item: return
        from _01_core_logic.creative_state import CreativeState
        
        if isinstance(self.current_item, CreativeState):
            self.current_item.background_texture_path = None
        elif isinstance(self.current_item, CreativeStoneData):
            self.current_item.texture_path = None
            
        self.texture_label.setText("None")
        self.property_changed.emit()

    def _delete_item(self):
        """Request deletion of current item(s)."""
        if self.current_item:
            if isinstance(self.current_item, list):
                # Batch delete - emit each item
                for item in self.current_item:
                    self.delete_requested.emit(item)
            else:
                self.delete_requested.emit(self.current_item)
            self.load_item(None)  # Clear panel
