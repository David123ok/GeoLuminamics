"""
File: main_creative.py
Creation Date: 2026-01-05
Description: Entry point for the GeoLuminamics Creative Engine.
"""

import sys
import json
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QMessageBox, QFileDialog, QInputDialog
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, QTimer

from _01_core_logic.creative_state import CreativeState, CreativeStoneData, CreativeLaserData
from _01_core_logic.creative_recorder import CreativeRecorder
from _01_core_logic.creative_replayer import CreativeReplayer
from _03_ui.creative_board import CreativeBoard
from _03_ui.creative_controls import CreativeControls
from _03_ui.property_panel import PropertyPanel

class CreativeWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GeoLuminamics Creative Engine")
        self.resize(1400, 900)
        
        # Core State
        self.state = CreativeState()
        self.recorder = CreativeRecorder()
        self.replayer = CreativeReplayer(self.state)
        
        # Setup Styling
        self.setStyleSheet("""
            QMainWindow { background-color: #151515; }
            QWidget { font-family: 'Segoe UI', sans-serif; }
        """)
        
        # Layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Top Controls
        self.controls = CreativeControls()
        main_layout.addWidget(self.controls)
        
        # Middle (Board + Panel)
        content_layout = QHBoxLayout()
        self.board = CreativeBoard(self.state)
        self.prop_panel = PropertyPanel()
        
        content_layout.addWidget(self.board, stretch=1)
        content_layout.addWidget(self.prop_panel, stretch=0)
        main_layout.addLayout(content_layout)
        
        # --- Signal Connections ---
        
        # Tools
        self.controls.tool_changed.connect(self._on_tool_changed)
        self.controls.stone_type_changed.connect(self._on_stone_type_changed)
        self.controls.action_triggered.connect(self._on_action_triggered)
        
        # Selection
        self.board.item_selected.connect(self.prop_panel.load_item)
        
        # Property Updates (Two-way sync + Recording)
        self.prop_panel.property_changed.connect(self._on_property_changed)
        self.prop_panel.delete_requested.connect(self._on_delete_item)
        
        # Recording Hooks
        self.board.item_added.connect(self._on_item_added)
        self.board.item_moved.connect(self._on_item_moved)
        
        # Auto-save / Loop Timer
        self.anim_timer = QTimer(self)
        self.anim_timer.timeout.connect(self.board.animate_step)
        self.anim_timer.start(16) # ~60 FPS
        
    def _on_tool_changed(self, tool_id):
        self.board.current_tool = tool_id
        
    def _on_stone_type_changed(self, stone_type):
        self.board.selected_stone_type = stone_type
        
    def _on_item_added(self, item):
        data = item.to_dict()
        data["uid"] = item.uid # Ensure UID is captured
        self.recorder.record_action("ADD_ITEM", item_class=type(item).__name__, item_data=data)
        
    def _on_item_moved(self, item):
        self.recorder.record_action("MOVE_ITEM", uid=item.uid, x=item.x, y=item.y)
        
    def _on_property_changed(self):
        # Redraw
        self.board.redraw_everything()
        
        # Record
        item = self.prop_panel.current_item
        if item:
            self.recorder.record_action("PROP_CHANGE", uid=item.uid, full_state=item.to_dict())
    
    def _on_delete_item(self, item):
        """Handle deletion request from property panel."""
        from _01_core_logic.creative_state import CreativeStoneData, CreativeLaserData
        
        if isinstance(item, CreativeStoneData):
            self.state.remove_stone(item)
            self.recorder.record_action("DELETE_STONE", uid=item.uid)
        elif isinstance(item, CreativeLaserData):
            self.state.remove_laser(item)
            self.recorder.record_action("DELETE_LASER", uid=item.uid)
        
        self.board.redraw_everything()
            
    def _on_action_triggered(self, action):
        if action == "CLEAR":
            if QMessageBox.question(self, "Clear", "Remove all objects?") == QMessageBox.Yes:
                self.state.clear()
                self.board.redraw_everything()
                self.recorder.record_action("CLEAR")
                self.recorder.clear() # Optional: Clear history too? Or keep "Clear" as an action?
                # Keeping "Clear" as action allows full session replay.
        
        elif action == "SAVE":
            file_name, _ = QFileDialog.getSaveFileName(self, "Save Scene", "", "GeoLuminamics Scene (*.gls)")
            if file_name:
                try:
                    data = self.state.to_dict()
                    with open(file_name, 'w') as f:
                        json.dump(data, f, indent=2)
                    QMessageBox.information(self, "Success", "Scene saved successfully.")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to save scene: {e}")
                    
        elif action == "LOAD":
            file_name, _ = QFileDialog.getOpenFileName(self, "Load Scene", "", "GeoLuminamics Scene (*.gls)")
            if file_name:
                try:
                    with open(file_name, 'r') as f:
                        data = json.load(f)
                    new_state = CreativeState.from_dict(data)
                    self.state.clear()
                    # Copy contents to keep reference
                    self.state.stones = new_state.stones
                    self.state.lasers = new_state.lasers
                    self.state.grid_size = new_state.grid_size
                    self.state.background_color = new_state.background_color
                    
                    self.board.redraw_everything()
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to load scene: {e}")
                
        elif action == "SCREENSHOT":
            self._take_screenshot()
            
    def _take_screenshot(self):
        # Ask user for resolution
        resolutions = ["1x (Native)", "2x (High Quality)", "4x (Ultra HD)", "8x (Maximum)"]
        res_choice, ok = QInputDialog.getItem(self, "Select Resolution", "Export Resolution:", resolutions, 1, False)
        
        if not ok:
            return
            
        scale_map = {"1x (Native)": 1.0, "2x (High Quality)": 2.0, "4x (Ultra HD)": 4.0, "8x (Maximum)": 8.0}
        scale = scale_map.get(res_choice, 2.0)
        
        rect = self.board.scene.sceneRect()
        image = QPixmap(int(rect.width() * scale), int(rect.height() * scale))
        image.fill(Qt.transparent)
        
        from PySide6.QtGui import QPainter
        painter = QPainter(image)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        painter.scale(scale, scale)
        
        self.board.scene.render(painter)
        painter.end()
        
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Screenshot", f"screenshot_{int(scale)}x.png", "PNG Files (*.png)")
        if file_name:
            image.save(file_name)
            QMessageBox.information(self, "Success", f"Screenshot saved at {int(scale)}x resolution.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CreativeWindow()
    window.show()
    sys.exit(app.exec())
