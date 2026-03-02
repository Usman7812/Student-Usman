from datetime import datetime, timedelta
from sqlalchemy import func
from database.models import Session, Event, EmotionLog

class BurnoutAnalyzer:
    def __init__(self, db_manager):
        self.db = db_manager

    def calculate_burnout_risk(self):
        """
        Analyzes the last 7 days of data to predict burnout risk.
        Factors:
        - Decreasing total focus time.
        - Increasing frequency of fatigue alerts.
        - Negative emotion trends.
        """
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        
        with self.db.Session() as session:
            # 1. Focus Trend
            daily_focus = session.query(
                func.date(Session.start_time),
                func.sum(Session.total_focus_mins)
            ).filter(Session.start_time >= seven_days_ago)\
             .group_by(func.date(Session.start_time)).all()
            
            # 2. Fatigue Trend
            fatigue_events = session.query(Event)\
                .filter(Event.timestamp >= seven_days_ago)\
                .filter(Event.value.like('%Drowsiness%')).count()
            
            # 3. Emotion Trend (Negative vs Positive)
            emotions = session.query(EmotionLog.emotion)\
                .filter(EmotionLog.timestamp >= seven_days_ago).all()
            
            neg_count = sum(1 for e in emotions if e.emotion in ['sad', 'angry', 'fear', 'disgust'])
            total_emotions = len(emotions) if emotions else 1
            neg_ratio = neg_count / total_emotions

        # Simple heuristic risk score (0-100)
        risk_score = 0
        
        # Factor 1: Low focus or declining (Simplified)
        if len(daily_focus) > 0:
            avg_focus = sum(f[1] for f in daily_focus) / len(daily_focus)
            if avg_focus < 60: risk_score += 30 # Under 1hr/day
        
        # Factor 2: High fatigue alerts
        risk_score += min(40, fatigue_events * 5)
        
        # Factor 3: Negative emotions
        risk_score += min(30, neg_ratio * 100)
        
        return min(100, risk_score)
