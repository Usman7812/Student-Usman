import time
from config import (
    YAW_THRESHOLD, 
    PITCH_THRESHOLD, 
    LOOKING_DOWN_THRESHOLD, 
    LOOKING_DOWN_GRACE_PERIOD, 
    LOOK_UP_RESET_THRESHOLD,
    FOCUS_SCORE_WINDOW, 
    FOCUS_ALERT_THRESHOLD
)

class FocusAnalyzer:
    def __init__(self):
        self.focus_history = [] # List of (timestamp, is_focused)
        self.last_alert_time = 0
        self.look_down_start_time = None
        self.last_look_up_time = None

    def analyze(self, head_pose):
        current_time = time.time()
        
        is_looking_down = False
        if head_pose is None:
            # If face is lost, we don't reset the look-down timer immediately
            # This handles cases where the head tilts so far down the camera loses it
            is_looking_down = (self.look_down_start_time is not None)
            self.focus_history.append((current_time, False))
        else:
            yaw = abs(head_pose['yaw'])
            pitch = head_pose['pitch']
            
            # Normal focus check
            is_focused = yaw < YAW_THRESHOLD and abs(pitch) < PITCH_THRESHOLD
            
            # 1. Look-Down Persistence Logic
            if pitch > LOOKING_DOWN_THRESHOLD:
                is_looking_down = True
                is_focused = False
                self.last_look_up_time = None # Reset look-up buffer
                if self.look_down_start_time is None:
                    self.look_down_start_time = current_time
            else:
                # User looked up. Check if we should reset the timer or keep buffering
                if self.look_down_start_time is not None:
                    if self.last_look_up_time is None:
                        self.last_look_up_time = current_time
                    
                    # SOFT RESET: Only clear look_down if they look up for > LOOK_UP_RESET_THRESHOLD
                    if current_time - self.last_look_up_time > LOOK_UP_RESET_THRESHOLD:
                        self.look_down_start_time = None
                        self.last_look_up_time = None
                    else:
                        is_looking_down = True # Keep the "Distracted" state active during brief glaces up
                
            self.focus_history.append((current_time, is_focused))
            
        # Clean history
        self.focus_history = [f for f in self.focus_history if current_time - f[0] < FOCUS_SCORE_WINDOW]
        
        focused_count = sum([1 for f in self.focus_history if f[1]])
        focus_score = (focused_count / len(self.focus_history)) * 100 if self.focus_history else 100
        
        alert_needed = False
        alert_level = 0 # 0: None, 1: Visual, 2: Nudge, 3: Alarm
        alert_msg = ""
        
        # 2. 3-Stage Distraction Analysis
        if is_looking_down and self.look_down_start_time:
            elapsed = current_time - self.look_down_start_time
            if elapsed > LOOKING_DOWN_GRACE_PERIOD:
                alert_needed = True
                if elapsed > 25:
                    alert_level = 3 # Alarm
                    alert_msg = f"CRITICAL: Persistent distraction ({int(elapsed)}s)!"
                elif elapsed > 20:
                    alert_level = 2 # Nudge sound
                    alert_msg = f"Nudge: You've been looking down for {int(elapsed)}s."
                else:
                    alert_level = 1 # Visual only
                    alert_msg = "Looking down? Focus back when ready."
        
        return {
            'focus_score': focus_score,
            'alert_needed': alert_needed,
            'alert_level': alert_level,
            'alert_msg': alert_msg,
            'is_looking_down': is_looking_down,
            'look_down_duration': current_time - self.look_down_start_time if self.look_down_start_time else 0
        }
