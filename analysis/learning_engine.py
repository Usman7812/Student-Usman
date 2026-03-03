import json
import os
from database.db_manager import DatabaseManager
from database.models import UserFeedback
from config import LOOKING_DOWN_THRESHOLD, EMOTION_EMA_ALPHA

LEARNING_PATH = "personal_calibration.json"

class LearningEngine:
    def __init__(self, db_manager):
        self.db = db_manager
        self.thresholds = {
            'LOOKING_DOWN_THRESHOLD': LOOKING_DOWN_THRESHOLD,
            'EMOTION_EMA_ALPHA': EMOTION_EMA_ALPHA
        }
        self.load_personal_calibration()
        self.evolve_thresholds()

    def load_personal_calibration(self):
        if os.path.exists(LEARNING_PATH):
            try:
                with open(LEARNING_PATH, 'r') as f:
                    saved = json.load(f)
                    self.thresholds.update(saved)
            except Exception:
                pass

    def evolve_thresholds(self):
        """Analyze past feedback to adjust thresholds for the current session."""
        with self.db.Session() as session:
            # 1. Learn from Distraction Feedback
            # If user dismissed 'Looking Down' alerts, their reading pitch might be steeper.
            distraction_fb = session.query(UserFeedback).filter_by(
                event_type='distraction', 
                is_false_positive=1
            ).all()
            
            if distraction_fb:
                pitches = [fb.pitch_at_event for fb in distraction_fb if fb.pitch_at_event]
                if pitches:
                    avg_false_pitch = sum(pitches) / len(pitches)
                    # Shift threshold to be slightly above the average false positive pitch
                    # Max out at 70 degrees to keep some safety
                    self.thresholds['LOOKING_DOWN_THRESHOLD'] = min(70, max(self.thresholds['LOOKING_DOWN_THRESHOLD'], avg_false_pitch + 5))

            # 2. Learn from Emotion Feedback
            # If user corrects emotions, it means the model is too jittery or biased.
            # We decrease Alpha to make it more stable (slower to react to micro-expressions).
            emotion_fb = session.query(UserFeedback).filter_by(
                event_type='emotion', 
                is_false_positive=1
            ).count()
            
            if emotion_fb > 5:
                # Reduce alpha (more stability) by 0.02 for every 5 corrections, min 0.1
                adjustment = (emotion_fb // 5) * 0.02
                self.thresholds['EMOTION_EMA_ALPHA'] = max(0.1, EMOTION_EMA_ALPHA - adjustment)

        # Save the new evolved state
        self.save_calibration()

    def save_calibration(self):
        with open(LEARNING_PATH, 'w') as f:
            json.dump(self.thresholds, f)

    def get_thresholds(self):
        return self.thresholds
