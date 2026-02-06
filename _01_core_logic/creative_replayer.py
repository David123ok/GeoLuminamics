"""
File: creative_replayer.py
Creation Date: 2026-01-05
Description: Replays creative actions on a state.
"""

import time
from PySide6.QtCore import QObject, Signal, QTimer
from _01_core_logic.creative_state import CreativeState, CreativeStoneType, CreativeStoneData, CreativeLaserData

class CreativeReplayer(QObject):
    step_executed = Signal(int, int) # current_step, total_steps
    playback_finished = Signal()
    
    def __init__(self, state: CreativeState):
        super().__init__()
        self.state = state
        self.history = []
        self.current_index = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self._tick)
        self.speed = 1.0
        
    def load_history(self, history):
        self.history = history
        self.current_index = 0
        
    def play(self, speed=1.0):
        self.speed = speed
        self.state.clear() # Start fresh
        self.current_index = 0
        self.timer.start(50) # 20fps check
        
    def stop(self):
        self.timer.stop()
        
    def _tick(self):
        # Determine how many steps to execute based on time?
        # Simpler: Just execute one step per tick for now, or match timestamps?
        # Let's match timestamps for "Creation Process" feel.
        
        # NOTE: For simplicity in this iteration, we just iterate index
        if self.current_index >= len(self.history):
            self.stop()
            self.playback_finished.emit()
            return
            
        action = self.history[self.current_index]
        self._execute_action(action)
        self.current_index += 1
        self.step_executed.emit(self.current_index, len(self.history))
        
    def _execute_action(self, action):
        t = action["type"]
        d = action["data"]
        
        if t == "ADD_STONE":
             color = d.get("color", "#FFFFFF")
             stone = self.state.add_stone(CreativeStoneType[d["stone_type"]], d["x"], d["y"])
             stone.color = color 
             # Apply other props if saved
             
        elif t == "MOVE_STONE":
             # Find stone (we need ID tracking for robust replay, but for now assuming order or generic lookup?)
             # Without IDs, "MOVE" is hard if we have multiple identical stones.
             # We should probably modify CreativeState to have UUIDs for stones.
             # For MVP, let's assume index-based or just skip complex moves if tracking fails.
             # Let's try to find stone at 'prev_x'/'prev_y' if captured, 
             # OR we add IDs to CreativeStoneData.
             pass 
             
        elif t == "PROP_CHANGE":
             pass
             
        elif t == "CLEAR":
             self.state.clear()
             
        # TODO: Full implementation requires ID system in CreativeStoneData
