"""
File: creative_recorder.py
Creation Date: 2026-01-05
Description: Records creative actions for replay.
"""

import json
import time

class CreativeRecorder:
    def __init__(self):
        self.history = [] # List of action dicts
        self.start_time = time.time()
        self.is_recording = True
        
    def record_action(self, action_type, **kwargs):
        """
        Record an action.
        action_type: "ADD_STONE", "MOVE_STONE", "PROP_CHANGE", "ADD_LASER", etc.
        """
        if not self.is_recording:
            return
            
        entry = {
            "time": time.time() - self.start_time,
            "type": action_type,
            "data": kwargs
        }
        self.history.append(entry)
        # print(f"Recorded: {action_type} -> {kwargs}")

    def get_history_json(self):
        return json.dumps(self.history, indent=2)

    def load_history(self, json_str):
        self.history = json.loads(json_str)
        
    def clear(self):
        self.history = []
        self.start_time = time.time()
