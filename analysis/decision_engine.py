import anthropic
import time
import pyttsx3
import threading
from config import ANTHROPIC_API_KEY, CLAUDE_MODEL

class DecisionEngine:
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        self.last_coaching_time = 0
        
        # Voice Engine Initialization
        self.voice_enabled = True
        self.engine = pyttsx3.init()
        self.voice_thread = None

    def speak(self, text):
        if not self.voice_enabled:
            return
            
        def _speak():
            try:
                # Need to re-init in thread for some OS/drivers
                local_engine = pyttsx3.init()
                local_engine.say(text)
                local_engine.runAndWait()
            except Exception as e:
                print(f"TTS Error: {e}")

        # Run in separate thread to avoid blocking AI/UI
        threading.Thread(target=_speak, daemon=True).start()

    def process_rules(self, data):
        """
        Rule-based decision logic.
        data: {fatigue, focus, emotion, posture, distractions}
        """
        alerts = []
        
        # Fatigue alerts
        if 'fatigue' in data and data['fatigue']['alert_needed']:
            alerts.append(data['fatigue']['alert_msg'])
            
        # Focus alerts
        if 'focus' in data and data['focus']['alert_needed']:
            alerts.append(data['focus']['alert_msg'])
            
        # Posture alerts
        if 'pose_data' in data and data['pose_data']['metrics']['tilt_angle'] > 20:
            alerts.append("Straighten your back!")
            
        # Distraction alerts
        if 'phone_detections' in data and data['phone_detections']:
            alerts.append("Distraction detected! Put your phone away.")
            
        # Trigger voice for the most important alert
        if alerts:
            self.speak(alerts[0])
            
        return alerts

    def generate_coaching_feedback(self, session_data):
        """
        Wrapper for get_claude_coaching with a more descriptive name.
        """
        return self.get_claude_coaching(session_data)

    def get_claude_coaching(self, session_data):
        """
        Calls Claude API for a personalized coaching message.
        """
        current_time = time.time()
        # Rate limit coaching messages (e.g., once every 5 mins)
        if current_time - self.last_coaching_time < 300:
            return None
            
        prompt = f"""
        You are a supportive AI study coach. Here is the student's current session data summary:
        - Study duration: {session_data.get('study_minutes', 'N/A')} minutes
        - Focus status: {session_data.get('focus_status', 'Good')}
        - Fatigue detected: {session_data.get('fatigue_count', 0)} times
        
        Generate ONE short, warm, empathetic coaching message (max 12 words).
        """
        
        try:
            message = self.client.messages.create(
                model=CLAUDE_MODEL,
                max_tokens=60,
                messages=[{'role': 'user', 'content': prompt}]
            )
            self.last_coaching_time = current_time
            text = message.content[0].text
            self.speak(text) # Also speak the coaching message
            return text
        except Exception as e:
            print(f"Claude API failed: {e}")
            return "You're making great progress. Keep it up!"
