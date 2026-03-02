from datetime import datetime, timedelta
from database.models import UserStats, DailyTarget

class GamificationManager:
    def __init__(self, db_manager):
        self.db = db_manager

    def add_points(self, points):
        with self.db.Session() as session:
            stats = session.query(UserStats).first()
            if not stats:
                stats = UserStats(total_points=0, current_streak=0)
                session.add(stats)
            
            stats.total_points += points
            session.commit()
            return stats.total_points

    def update_streak(self):
        today = datetime.utcnow().date()
        with self.db.Session() as session:
            stats = session.query(UserStats).first()
            if not stats:
                stats = UserStats(total_points=0, current_streak=1, last_study_date=datetime.utcnow())
                session.add(stats)
            else:
                if stats.last_study_date:
                    last_date = stats.last_study_date.date()
                    if last_date == today - timedelta(days=1):
                        stats.current_streak += 1
                    elif last_date < today - timedelta(days=1):
                        stats.current_streak = 1
                else:
                    stats.current_streak = 1
                
                stats.last_study_date = datetime.utcnow()
            
            session.commit()
            return stats.current_streak

    def update_daily_progress(self, minutes):
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        with self.db.Session() as session:
            target = session.query(DailyTarget).filter(DailyTarget.date == today).first()
            if not target:
                target = DailyTarget(date=today, actual_focus_minutes=minutes)
                session.add(target)
            else:
                target.actual_focus_minutes += minutes
            
            session.commit()
            return target.actual_focus_minutes
