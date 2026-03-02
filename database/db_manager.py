from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.models import Base, Session, Event, EmotionLog, PostureLog, DistractionLog
from config import DB_PATH

class DatabaseManager:
    def __init__(self):
        self.engine = create_engine(DB_PATH)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.current_session_id = None

    def start_session(self):
        with self.Session() as db_session:
            new_session = Session()
            db_session.add(new_session)
            db_session.commit()
            self.current_session_id = new_session.id
            return self.current_session_id

    def end_session(self):
        if self.current_session_id is None:
            return
        with self.Session() as db_session:
            session = db_session.query(Session).get(self.current_session_id)
            if session:
                session.end_time = datetime.utcnow()
                db_session.commit()
        self.current_session_id = None

    def log_event(self, event_type, value):
        if self.current_session_id is None: return
        with self.Session() as db_session:
            event = Event(session_id=self.current_session_id, event_type=event_type, value=value)
            db_session.add(event)
            db_session.commit()

    def log_emotion(self, emotion, confidence):
        if self.current_session_id is None: return
        with self.Session() as db_session:
            log = EmotionLog(session_id=self.current_session_id, emotion=emotion, confidence=confidence)
            db_session.add(log)
            db_session.commit()

    def log_posture(self, status, angle):
        if self.current_session_id is None: return
        with self.Session() as db_session:
            log = PostureLog(session_id=self.current_session_id, status=status, angle=angle)
            db_session.add(log)
            db_session.commit()

    def log_distraction(self, source):
        if self.current_session_id is None: return
        with self.Session() as db_session:
            log = DistractionLog(session_id=self.current_session_id, source=source)
            db_session.add(log)
            db_session.commit()
