"""
File: creative_board.py
Creation Date: 2026-01-05
Description: Board widget for the Creative Engine. Handles rendering and interaction.
"""

from PySide6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsEllipseItem, QGraphicsLineItem
from PySide6.QtGui import QBrush, QColor, QPen, QRadialGradient, QPixmap, QPainter, QTransform
from PySide6.QtCore import Qt, Signal, QPointF
from _01_core_logic.creative_state import CreativeState, CreativeStoneType
from _02_engines.laser import LaserCalculator2D
import math
import os

class CreativeBoard(QGraphicsView):
    item_selected = Signal(object) # Emits the selected data object (Stone or Laser)
    item_added = Signal(object) # Emitted when new item placed
    item_moved = Signal(object) # Emitted when item finished dragging
    
    def __init__(self, state: CreativeState, parent=None):
        super().__init__(parent)
        self.state = state
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        
        # Configuration
        self.cell_size = 35
        self.margin = 50
        
        # Interaction State
        self.current_tool = "SELECT" # SELECT, PLACE_STONE, PLACE_LASER
        self.selected_stone_type = CreativeStoneType.PRISM
        self.is_dragging = False
        self.drag_start_pos = None
        self.dragged_item = None # The visual item being dragged (if any)
        self.dragged_data = None # The data object being dragged
        
        # Laser Creation State
        self.creating_laser = False
        self.laser_start_point = None
        self.temp_laser_arrow = None
        
        # Visual Items Map
        self.stone_items = {} # Maps CreativeStoneData -> QGraphicsItem
        self.laser_source_items = {} # Maps CreativeLaserData -> QGraphicsItem (the source indicator)
        self.laser_beam_items = [] # List of beam lines
        
        # Selection State
        self.selection_set = set()  # Set of selected data objects
        self.selection_highlights = []  # List of highlight QGraphicsItems
        
        self._init_board_visuals()
        self._setup_view()
        
    def _setup_view(self):
        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.SmoothPixmapTransform)
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self._update_scene_rect()

    def _update_scene_rect(self):
        size = (self.state.grid_size - 1) * self.cell_size + (self.margin * 2)
        # Check for background image and adjust scene size if needed? 
        # Usually grid defines size. Let's stick to grid.
        self.setSceneRect(0, 0, size, size)
        
    def animate_step(self):
        """Update animation state and visuals."""
        import math
        changed = False
        
        # Stones
        for stone, item in self.stone_items.items():
            if stone.is_animating and stone.rotation_speed != 0:
                stone.rotation += stone.rotation_speed
                stone.rotation %= 360
                item.setRotation(stone.rotation)
                changed = True
        
        # Lasers - rotate direction vector
        for laser in self.state.lasers:
            if laser.is_animating and laser.rotation_speed != 0:
                angle_rad = math.radians(laser.rotation_speed)
                dx, dy = laser.direction
                new_dx = dx * math.cos(angle_rad) - dy * math.sin(angle_rad)
                new_dy = dx * math.sin(angle_rad) + dy * math.cos(angle_rad)
                laser.direction = (new_dx, new_dy)
                
                # Update arrow rotation
                if laser in self.laser_source_items:
                    arrow = self.laser_source_items[laser]
                    angle = math.degrees(math.atan2(new_dy, new_dx))
                    arrow.setRotation(angle)
                changed = True
                
        if changed:
            self._update_beams()

    def _init_board_visuals(self):
        # We redraw background in separate method to handle updates easily
        self._draw_background()

        # Grid
        grid_pen = QPen(QColor(60, 60, 60), 1)
        size_px = (self.state.grid_size - 1) * self.cell_size
        
        for i in range(self.state.grid_size):
            pos = self.margin + i * self.cell_size
            # Vertical
            self.scene.addLine(pos, self.margin, pos, self.margin + size_px, grid_pen).setZValue(-5)
            # Horizontal
            self.scene.addLine(self.margin, pos, self.margin + size_px, pos, grid_pen).setZValue(-5)

        # Atmosphere Overlay (initialized, updated layout in redraw)
        self.atm_rect = self.scene.addRect(self.sceneRect(), Qt.NoPen, Qt.NoBrush)
        self.atm_rect.setZValue(100) # Top
        self.atm_rect.setOpacity(0)

    def _draw_background(self):
        # Clear existing background items defined in this method?
        # Simpler: Clear ALL items in redraw_everything.
        # But grid should persist.
        # Let's handle background dynamic update in redraw_everything
        pass

    def redraw_everything(self):
        """Full redraw of dynamic elements."""
        self.scene.clear()
        self.selection_highlight = None
        
        # Background - Sky Gradient or Texture
        rect = self.sceneRect()
        if self.state.background_texture_path and os.path.exists(self.state.background_texture_path):
            pixmap = QPixmap(self.state.background_texture_path)
            if not pixmap.isNull():
                bg_item = self.scene.addPixmap(pixmap)
                bg_item.setZValue(-10)
                scale_x = rect.width() / pixmap.width()
                scale_y = rect.height() / pixmap.height()
                bg_item.setScale(max(scale_x, scale_y))
        else:
            # Gradient Background - Radial or Linear
            from PySide6.QtGui import QLinearGradient, QRadialGradient
            
            if self.state.sky_gradient_type == "radial":
                # Radial gradient from center
                center_x = rect.width() / 2
                center_y = rect.height() / 2
                radius = max(rect.width(), rect.height()) * 0.7
                gradient = QRadialGradient(center_x, center_y, radius)
                gradient.setColorAt(0, QColor(self.state.sky_color_top))
                gradient.setColorAt(1, QColor(self.state.sky_color_bottom))
            else:
                # Linear gradient top to bottom
                gradient = QLinearGradient(rect.topLeft(), rect.bottomLeft())
                gradient.setColorAt(0, QColor(self.state.sky_color_top))
                gradient.setColorAt(1, QColor(self.state.sky_color_bottom))
            
            bg_rect = self.scene.addRect(rect, Qt.NoPen, QBrush(gradient))
            bg_rect.setZValue(-10)
        
        # Grid - Softer lines with subtle glow effect
        size_px = (self.state.grid_size - 1) * self.cell_size
        grid_color = QColor(50, 60, 80, 100)  # Subtle blue-gray
        grid_pen = QPen(grid_color, 1)
        grid_pen.setCosmetic(True)
        
        for i in range(self.state.grid_size):
            pos = self.margin + i * self.cell_size
            self.scene.addLine(pos, self.margin, pos, self.margin + size_px, grid_pen).setZValue(-5)
            self.scene.addLine(self.margin, pos, self.margin + size_px, pos, grid_pen).setZValue(-5)
        
        # Atmosphere Overlay
        if self.state.atmosphere_density > 0:
            atm_color = QColor(self.state.atmosphere_color)
            atm_color.setAlpha(int(255 * self.state.atmosphere_density * 0.5))
            atm_rect = self.scene.addRect(rect, Qt.NoPen, QBrush(atm_color))
            atm_rect.setZValue(100)
            atm_rect.setAcceptedMouseButtons(Qt.NoButton)

        # Clear maps
        self.stone_items.clear()
        self.laser_source_items.clear()
        self.laser_beam_items.clear()
        
        # Draw Stones
        for stone in self.state.stones:
            self._draw_stone(stone)
            
        # Draw Laser Sources
        for laser in self.state.lasers:
            self._draw_laser_source(laser)
            
        # Recalculate Beams
        self._update_beams()
             
    def _draw_stone(self, stone):
        x_px = self.margin + stone.x * self.cell_size
        y_px = self.margin + stone.y * self.cell_size
        radius = self.cell_size / 2 - 2
        
        group = self.scene.createItemGroup([])
        group.setPos(x_px, y_px)
        group.setRotation(stone.rotation) # Rotation in degrees
        group.setZValue(10)
        
        # Main Body
        color = QColor(stone.color)
        
        if stone.texture_path and os.path.exists(stone.texture_path):
             # Texture
             pix = QPixmap(stone.texture_path)
             if not pix.isNull():
                 pix = pix.scaled(int(radius*2), int(radius*2), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                 p_item = self.scene.addPixmap(pix)
                 p_item.setOffset(-radius, -radius)
                 p_item.setParentItem(group)
                 brush = Qt.NoBrush
        else:
            # Gradient
            grad = QRadialGradient(-radius/3, -radius/3, radius * 1.5)
            grad.setColorAt(0, color.lighter(150))
            grad.setColorAt(1, color)
            brush = QBrush(grad)
        
        if brush != Qt.NoBrush:
            body = self.scene.addEllipse(-radius, -radius, radius*2, radius*2, QPen(Qt.black, 2), brush)
            body.setParentItem(group)

        # Bloom effect (glow behind)
        if stone.bloom_intensity > 0:
            glow_radius = radius * (1.0 + stone.bloom_intensity * 0.8)
            glow_alpha = int(100 * stone.glow_intensity)
            glow_color = QColor(color.red(), color.green(), color.blue(), glow_alpha)
            glow = self.scene.addEllipse(-glow_radius, -glow_radius, glow_radius*2, glow_radius*2, Qt.NoPen, QBrush(glow_color))
            glow.setParentItem(group)
            glow.setZValue(-1)
        
        # Shape Indicator (Stone Type)
        pen = QPen(Qt.white if color.lightness() < 128 else Qt.black, 2)
        if stone.stone_type == CreativeStoneType.MIRROR:
            line = self.scene.addLine(0, -radius+4, 0, radius-4, pen)
            line.setParentItem(group)
        elif stone.stone_type == CreativeStoneType.SPLITTER:
            line1 = self.scene.addLine(0, -radius+4, 0, radius-4, pen)
            line2 = self.scene.addLine(-radius+4, 0, radius-4, 0, pen)
            line1.setParentItem(group)
            line2.setParentItem(group)
        elif stone.stone_type == CreativeStoneType.STOP:
             rect = self.scene.addRect(-radius/2, -radius/2, radius, radius, pen, QBrush(Qt.black))
             rect.setParentItem(group)
             
        self.stone_items[stone] = group

    def _draw_laser_source(self, laser):
        x_px = self.margin + laser.x * self.cell_size
        y_px = self.margin + laser.y * self.cell_size
        
        # Source Indicator (Arrow)
        arrow = self.scene.addPolygon(
            [QPointF(-10, -5), QPointF(-10, 5), QPointF(10, 0)],
            QPen(Qt.white, 1), QBrush(QColor(laser.color))
        )
        arrow.setPos(x_px, y_px)
        
        # Rotation based on direction
        angle = math.degrees(math.atan2(laser.direction[1], laser.direction[0]))
        arrow.setRotation(angle)
        arrow.setZValue(5)
        
        self.laser_source_items[laser] = arrow

    def _update_beams(self):
        # Clear old beams
        for item in self.laser_beam_items:
            self.scene.removeItem(item)
        self.laser_beam_items.clear()
        
        # Create temp dictionary for calc
        stones_dict = {}
        for s in self.state.stones:
            # Check if this is a STOP stone
            stone_obj = type('obj', (object,), {
                'type_name': s.stone_type.name,
                'stone_type': s.stone_type,
                'player': 1, # Dummy
                'rotation_angle': s.rotation
            })
            stones_dict[(s.x, s.y)] = stone_obj
            
            # Additional logic for STOP type to handle in LaserCalculator or locally?
            # The existing LaserCalculator doesn't know about STOP stones.
            # We might need to monkey-patch or subclass LaserCalculator2D.
            # For now, let's assume it passes through or we implement STOP logic later.
        
        # Calculate
        calc = LaserCalculator2D(self.state.grid_size)
        
        for laser in self.state.lasers:
            if not laser.enabled: continue
            
            start = (laser.x, laser.y)
            # Laser calc expects integer start usually for grid binding, but float for freeform?
            # The existing calc might be grid-bound. We need to check handling.
            # If using grid-based calc, we might be limited.
            # For "Freeform", we might need a custom raycaster.
            # Let's stick to the existing calc for now and see limitations.
            
            paths = calc.calculate_path(start, laser.direction, stones_dict)
            
            # Draw
            pen = QPen(QColor(laser.color), 3 * laser.intensity)
            pen.setCapStyle(Qt.RoundCap)
            
            # Glow pen
            glow_width = 8 * laser.bloom_intensity
            if glow_width < 1: glow_width = 1
            
            glow_alpha = int(100 * laser.glow_intensity)
            glow_color = QColor(laser.color)
            glow_color.setAlpha(glow_alpha)
            
            glow_pen = QPen(glow_color, glow_width)
            
            for path in paths:
                for i in range(len(path) - 1):
                    p1 = path[i]
                    p2 = path[i+1]
                    
                    x1 = self.margin + p1[0] * self.cell_size
                    y1 = self.margin + p1[1] * self.cell_size
                    x2 = self.margin + p2[0] * self.cell_size
                    y2 = self.margin + p2[1] * self.cell_size
                    
                    # Glow
                    if laser.bloom_intensity > 0:
                        line_glow = self.scene.addLine(x1, y1, x2, y2, glow_pen)
                        line_glow.setZValue(2)
                        self.laser_beam_items.append(line_glow)
                    
                    # Core
                    line = self.scene.addLine(x1, y1, x2, y2, pen)
                    line.setZValue(3)
                    self.laser_beam_items.append(line)

    # Interaction Events
    def mousePressEvent(self, event):
        pos = self.mapToScene(event.pos())
        gx = round((pos.x() - self.margin) / self.cell_size)
        gy = round((pos.y() - self.margin) / self.cell_size)
        
        if event.button() == Qt.LeftButton:
            if self.current_tool == "PLACE_STONE":
                # Check bounding
                if 0 <= gx < self.state.grid_size and 0 <= gy < self.state.grid_size:
                    # Check overlap
                    existing = self.state.get_stone_at(gx, gy)
                    if not existing:
                        self.state.add_stone(self.selected_stone_type, gx, gy)
                        self.redraw_everything()
            
            elif self.current_tool == "PLACE_LASER":
                self.creating_laser = True
                self.laser_start_point = (pos.x() - self.margin) / self.cell_size, (pos.y() - self.margin) / self.cell_size
                self.drag_start_pos = pos
                
            elif self.current_tool == "SELECT":
                shift_held = event.modifiers() & Qt.ShiftModifier
                
                # Find item at click
                clicked_stone = self.state.get_stone_at(gx, gy)
                clicked_laser = None
                
                if not clicked_stone:
                    # Check lasers
                    for l, item in self.laser_source_items.items():
                        lx_px = self.margin + l.x * self.cell_size
                        ly_px = self.margin + l.y * self.cell_size
                        if (pos.x() - lx_px)**2 + (pos.y() - ly_px)**2 < (self.cell_size/2)**2:
                            clicked_laser = l
                            break
                
                clicked_item = clicked_stone or clicked_laser
                
                if clicked_item:
                    self._highlight_item(clicked_item, add_to_selection=shift_held)
                    
                    # Emit selection (single or list)
                    if len(self.selection_set) == 1:
                        self.item_selected.emit(clicked_item)
                    else:
                        self.item_selected.emit(list(self.selection_set))
                    
                    # Prepare drag (single item only)
                    if not shift_held:
                        self.is_dragging = True
                        self.dragged_data = clicked_item
                else:
                    # Deselect / Select Board
                    self.selection_set.clear()
                    self._clear_highlight()
                    self.item_selected.emit(self.state)
                    
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        pos = self.mapToScene(event.pos())
        
        if self.creating_laser:
            # Update laser visual arrow
            pass # TODO visual preview
            
        elif self.is_dragging and self.dragged_data:
            # Update position (snap to grid?)
            gx = round((pos.x() - self.margin) / self.cell_size)
            gy = round((pos.y() - self.margin) / self.cell_size)
            
            if 0 <= gx < self.state.grid_size and 0 <= gy < self.state.grid_size:
                # Update data
                self.dragged_data.x = gx
                self.dragged_data.y = gy
                self.redraw_everything()
                self._highlight_item(self.stone_items[self.dragged_data])
                
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        pos = self.mapToScene(event.pos())
        
        if self.creating_laser:
            # Create laser
            end_x = (pos.x() - self.margin) / self.cell_size
            end_y = (pos.y() - self.margin) / self.cell_size
            
            dx = end_x - self.laser_start_point[0]
            dy = end_y - self.laser_start_point[1]
            mag = math.sqrt(dx*dx + dy*dy)
            
            if mag > 0.1: # Threshold to create
                self.state.add_laser(self.laser_start_point[0], self.laser_start_point[1], dx/mag, dy/mag)
                self.redraw_everything()
                
            self.creating_laser = False
            
        elif self.is_dragging:
            self.is_dragging = False
            # Recalculate beams final
            self._update_beams()
            
        super().mouseReleaseEvent(event)
        
    def _highlight_item(self, data_item, add_to_selection=False):
        """Add/set highlight for item. If add_to_selection, adds to set; otherwise replaces."""
        if not add_to_selection:
            self._clear_highlight()
            self.selection_set.clear()
        
        # Add to selection set
        self.selection_set.add(data_item)
        
        # Find visual item
        item = None
        if data_item in self.stone_items:
            item = self.stone_items[data_item]
        elif data_item in self.laser_source_items:
            item = self.laser_source_items[data_item]
        
        if item:
            rect = item.boundingRect()
            highlight = self.scene.addRect(rect.translated(item.pos()), QPen(Qt.yellow, 2), Qt.NoBrush)
            highlight.setZValue(20)
            self.selection_highlights.append(highlight)
        
    def _clear_highlight(self):
        for h in self.selection_highlights:
            self.scene.removeItem(h)
        self.selection_highlights.clear()
        
    def get_selection(self):
        """Return list of selected data items."""
        return list(self.selection_set)
