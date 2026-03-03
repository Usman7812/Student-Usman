import time
from config import EAR_THRESHOLD, EAR_CONSEC_FRAMES, MAR_THRESHOLD, YAWN_CONSEC_FRAMES

class FatigueAnalyzer:
    def __init__(self):
        self.ear_consec_frames = 0
        self.mar_consec_frames = 0
        self.fatigue_score = 0 # 0-100
        self.baseline_shoulder_height = None
        self.slump_frames = 0

    def analyze(self, fatigue_metrics, pose_metrics=None):
        if fatigue_metrics is None:
            return None
        
        ear = fatigue_metrics['ear']
        mar = fatigue_metrics['mar']
        
        is_slumped = False
        if pose_metrics and 'shoulder_height' in pose_metrics:
            curr_h = pose_metrics['shoulder_height']
            if self.baseline_shoulder_height is None:
                self.baseline_shoulder_height = curr_h
            
            # If shoulders drop (Y increases in CV2) by 15% from baseline
            if curr_h > self.baseline_shoulder_height * 1.15:
                self.slump_frames += 1
            else:
                self.slump_frames = 0
                # Slowly adapt baseline to account for natural movement
                self.baseline_shoulder_height = self.baseline_shoulder_height * 0.99 + curr_h * 0.01

            if self.slump_frames > 30: # ~2 seconds of slumping
                is_slumped = True

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
            'alert_msg': alert_msg,
            'is_slumped': is_slumped
        }
