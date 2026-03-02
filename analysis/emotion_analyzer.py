import time
from config import EMOTION_SAMPLE_INTERVAL, EMOTION_WINDOW, EMOTION_EMA_ALPHA
from deepface import DeepFace

class EmotionAnalyzer:
    def __init__(self):
        self.last_sample_time = 0
        self.emotion_probs = {
            'angry': 0.0, 'disgust': 0.0, 'fear': 0.0, 
            'happy': 0.0, 'sad': 0.0, 'surprise': 0.0, 'neutral': 1.0
        }
        self.last_result = 'neutral'

    def analyze(self, frame):
        current_time = time.time()
        
        # Only sample at intervals, but return the current EMA result every frame
        if current_time - self.last_sample_time < EMOTION_SAMPLE_INTERVAL:
            return self.get_current_state()

        try:
            # DeepFace analysis for emotion
            result = DeepFace.analyze(frame, actions=['emotion'], enforce_detection=False, silent=True)
            current_raw = result[0]['emotion'] # Dictionary of emotion names to scores (0-100)
            
            # 1. BIAS FIX: If happy but low confidence, suppress it
            if current_raw['happy'] < 45:
                current_raw['neutral'] += current_raw['happy']
                current_raw['happy'] = 0
            
            # 2. Apply Exponential Moving Average (EMA) to probabilities
            alpha = EMOTION_EMA_ALPHA
            for emo in self.emotion_probs:
                # Convert DeepFace 0-100 to 0.0-1.0
                current_val = current_raw.get(emo, 0) / 100.0
                self.emotion_probs[emo] = (alpha * current_val) + ((1 - alpha) * self.emotion_probs[emo])
            
            # 3. Find new dominant emotion from smoothed probabilities
            self.last_result = max(self.emotion_probs, key=self.emotion_probs.get)
            self.last_sample_time = current_time
            
            return self.get_current_state()
        except Exception:
            return self.get_current_state()

    def get_current_state(self):
        dominant = self.last_result
        prob = self.emotion_probs[dominant]
        
        return {
            'current_emotion': dominant,
            'confidence': prob * 100.0,
            'is_stable': prob > 0.6 # High confidence in the current EMA state
        }
