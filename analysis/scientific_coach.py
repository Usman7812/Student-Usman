import time
from typing import Dict, Optional

class ScientificCoach:
    def __init__(self):
        # Pomodoro 50/10 Settings
        self.focus_session_start = time.time()
        self.last_pomodoro_alert = 0
        self.POMODORO_WORK_LIMIT = 50 * 60 # 50 minutes
        
        # 20-20-20 Rule Settings
        self.last_eye_break = time.time()
        self.EYE_BREAK_INTERVAL = 20 * 60 # 20 minutes
        self.EYE_BREAK_DURATION = 20 # 20 seconds
        
        self.last_suggestion = ""
        self.suggestion_cooldown = 0

    def analyze(self, session_data: Dict) -> Dict:
        current_time = time.time()
        suggestions = []
        alerts = []
        
        # 1. Check Pomodoro 50/10
        elapsed_focus = current_time - self.focus_session_start
        pomodoro_remaining = max(0, self.POMODORO_WORK_LIMIT - elapsed_focus)
        
        if elapsed_focus > self.POMODORO_WORK_LIMIT:
            alerts.append("Research suggests a 10-minute break after 50m for optimal retention.")
            suggestions.append("Time for a Pomodoro break! Stretching or walking is proven to boost next-session focus.")
        elif elapsed_focus < 30: # Start of session tip
            suggestions.append("Starting a 50min Deep Work block. Minimize tab switching for better cognitive flow.")
        
        # 2. Check 20-20-20 Rule
        elapsed_eye = current_time - self.last_eye_break
        eye_remaining = max(0, self.EYE_BREAK_INTERVAL - elapsed_eye)
        if elapsed_eye > self.EYE_BREAK_INTERVAL:
            alerts.append("20-20-20 Rule: Your eyes need a break.")
            suggestions.append("Look at an object 20 feet away for 20 seconds to reduce digital eye strain.")
            
        # 3. Check for Fatigue/Posture Slump from data
        is_slumped = False
        if session_data.get('fatigue', {}).get('is_slumped', False):
            is_slumped = True
            suggestions.append("Slumped posture detected. Adjusting your back can prevent 'Zoom fatigue'.")

        return {
            'suggestions': suggestions,
            'alerts': alerts,
            'is_slumped': is_slumped,
            'timers': {
                'pomodoro_remaining_s': int(pomodoro_remaining),
                'eye_break_remaining_s': int(eye_remaining),
                'focus_elapsed_m': int(elapsed_focus / 60)
            }
        }

    def reset_eye_break(self):
        self.last_eye_break = time.time()

    def reset_focus_session(self):
        self.focus_session_start = time.time()
