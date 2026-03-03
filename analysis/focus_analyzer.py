import time
import numpy as np
from config import (
    YAW_THRESHOLD, PITCH_THRESHOLD, LOOKING_DOWN_THRESHOLD,
    WINDOW_DIGITAL_FOCUS, WINDOW_ANALOG_STUDY, WINDOW_COGNITIVE_PAUSE,
    WINDOW_PASSIVE_DRIFT, WINDOW_MOBILE_USAGE, WINDOW_DAYDREAMING,
    SACCADE_RATIO_THRESHOLD, PHONE_CLASS_ID
)

class FocusAnalyzer:
    def __init__(self):
        self.state = "Active Study"
        self.state_start_time = time.time()
        self.last_known_status = "Active Study"
        
        # Persistence counters for flickering prevention
        self.phone_persistence = 0
        self.face_missing_start = None

    def reconfigure(self, thresholds):
        # This method is no longer directly used in the new logic, but kept for compatibility if needed
        pass

    def analyze(self, face_data, pose_data, detections, fatigue_score):
        """
        Research-Backed Inferential Analysis.
        Combines Pose, Behavioral Signatures, and Material Context.
        """
        now = time.time()
        
        if not face_data:
            return self._handle_face_missing(now)
            
        pose = face_data.get('head_pose', {})
        signatures = face_data.get('signatures', {})
        yaw = abs(pose.get('yaw', 0))
        pitch = pose.get('pitch', 0)
        
        saccade_ratio = signatures.get('saccade_ratio', 0)
        expression_spike = signatures.get('expression_spike', False)
        
        # Material Context
        has_phone = any(d['class'] == PHONE_CLASS_ID for d in detections)
        has_book = any(d['class'] == 73 for d in detections)
        
        # 1. IMMEDIATE ALARM: Mobile Usage (Direct or Inferred)
        if has_phone or (pitch > 30 and expression_spike):
            self.phone_persistence += 1
            if self.phone_persistence > 2: # ~0.5s at 4fps yolo
                return self._update_state("Mobile Usage", now)
        else:
            self.phone_persistence = 0

        # 2. ANALOG STUDY (Confirmed or Inferred)
        if pitch > LOOKING_DOWN_THRESHOLD:
            # If we see a book OR systematic saccades, it's study
            if has_book or saccade_ratio > SACCADE_RATIO_THRESHOLD:
                return self._update_state("Analog Study", now)
            else:
                # Looking down without book or reading pattern = Drift
                return self._update_state("Passive Drift", now)

        # 3. YAW-BASED: Cognitive Pause vs Daydreaming
        if yaw > YAW_THRESHOLD:
            elapsed = now - self.state_start_time
            if elapsed < WINDOW_COGNITIVE_PAUSE:
                return self._update_state("Cognitive Pause", now)
            else:
                return self._update_state("Daydreaming", now)

        # 4. DEFAULT: Digital Focus
        return self._update_state("Active Study", now)

    def _update_state(self, new_state, now):
        if new_state != self.state:
            # Only switch if the required window has passed or if it's high priority
            elapsed = now - self.state_start_time
            
            # High Priority overrides (Mobile)
            if new_state == "Mobile Usage":
                self.state = new_state
                self.state_start_time = now
            
            # Standard transition logic based on Sample Windows
            windows = {
                "Analog Study": WINDOW_ANALOG_STUDY,
                "Passive Drift": 5.0, # Faster transition to drift to catch it early
                "Daydreaming": WINDOW_DAYDREAMING,
                "Active Study": WINDOW_DIGITAL_FOCUS
            }
            
            required_window = windows.get(new_state, 2.0)
            if elapsed >= required_window:
                self.state = new_state
                self.state_start_time = now
                
        return {
            'status': self.state,
            'is_focused': self.state in ["Active Study", "Analog Study", "Cognitive Pause"],
            'alert_level': self._get_alert_level(),
            'focus_score': 100 if self.state in ["Active Study", "Analog Study"] else 50
        }

    def _get_alert_level(self):
        levels = {
            "Active Study": 0,
            "Analog Study": 0,
            "Cognitive Pause": 0,
            "Passive Drift": 1,
            "Daydreaming": 1,
            "Mobile Usage": 2,
            "Session Paused": 0
        }
        return levels.get(self.state, 0)

    def _handle_face_missing(self, now):
        self.state = "Session Paused"
        return {
            'status': "Session Paused",
            'is_focused': False,
            'alert_level': 0,
            'focus_score': 0
        }
