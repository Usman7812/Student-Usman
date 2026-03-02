import time
from config import EAR_THRESHOLD, EAR_CONSEC_FRAMES, MAR_THRESHOLD, YAWN_CONSEC_FRAMES

class FatigueAnalyzer:
    def __init__(self):
        self.ear_consec_frames = 0
        self.mar_consec_frames = 0
        self.fatigue_score = 0 # 0-100

    def analyze(self, fatigue_metrics):
        if fatigue_metrics is None:
            return None
        
        ear = fatigue_metrics['ear']
        mar = fatigue_metrics['mar']
        
        # Check for drowsiness (eyes closed)
        if ear < EAR_THRESHOLD:
            self.ear_consec_frames += 1
        else:
            self.ear_consec_frames = 0
            
        # Check for yawning
        if mar > MAR_THRESHOLD:
            self.mar_consec_frames += 1
        else:
            self.mar_consec_frames = 0
            
        # Update fatigue score
        # 0.25 is very closed, 0.35 is open. Simple mapping:
        self.fatigue_score = max(0, min(100, 100 - (ear * 200))) 
        
        alert_needed = False
        alert_msg = ""
        
        if self.ear_consec_frames >= EAR_CONSEC_FRAMES:
            alert_needed = True
            alert_msg = "Drowsiness detected! Take a break."
            self.ear_consec_frames = 0 # Reset after alert
            
        if self.mar_consec_frames >= YAWN_CONSEC_FRAMES:
            alert_needed = True
            alert_msg = "Frequent yawning detected. Are you tired?"
            self.mar_consec_frames = 0
            
        return {
            'fatigue_score': self.fatigue_score,
            'alert_needed': alert_needed,
            'alert_msg': alert_msg
        }
