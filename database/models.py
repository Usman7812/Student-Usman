from datetime import datetime
from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Session(Base):
    __tablename__ = 'sessions'
    id = Column(Integer, primary_key=True)
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    total_focus_mins = Column(Float, default=0.0)
    avg_emotion = Column(String(50), nullable=True)

    events = relationship("Event", back_populates="session")
    emotions = relationship("EmotionLog", back_populates="session")
    posture_logs = relationship("PostureLog", back_populates="session")
    distractions = relationship("DistractionLog", back_populates="session")

class Event(Base):
    __tablename__ = 'events'
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey('sessions.id'))
    timestamp = Column(DateTime, default=datetime.utcnow)
    event_type = Column(String(50)) # e.g., 'alert', 'focus_pulse'
    value = Column(String(255))

    session = relationship("Session", back_populates="events")

class EmotionLog(Base):
    __tablename__ = 'emotions'
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey('sessions.id'))
    timestamp = Column(DateTime, default=datetime.utcnow)
    emotion = Column(String(50))
    confidence = Column(Float)

    session = relationship("Session", back_populates="emotions")

class PostureLog(Base):
    __tablename__ = 'posture_logs'
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey('sessions.id'))
    timestamp = Column(DateTime, default=datetime.utcnow)
    status = Column(String(50)) # e.g., 'good', 'bad'
    angle = Column(Float)

    session = relationship("Session", back_populates="posture_logs")

class DistractionLog(Base):
    __tablename__ = 'distractions'
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey('sessions.id'))
    timestamp = Column(DateTime, default=datetime.utcnow)
    source = Column(String(100)) # e.g., 'phone', 'person'

    session = relationship("Session", back_populates="distractions")

class UserStats(Base):
    __tablename__ = 'user_stats'
    id = Column(Integer, primary_key=True)
    total_points = Column(Integer, default=0)
    current_streak = Column(Integer, default=0)
    last_study_date = Column(DateTime)
    burnout_risk_score = Column(Float, default=0.0) # 0 to 100

class DailyTarget(Base):
    __tablename__ = 'daily_targets'
    id = Column(Integer, primary_key=True)
    date = Column(DateTime, unique=True, default=datetime.utcnow)
    target_focus_minutes = Column(Integer, default=120)
    actual_focus_minutes = Column(Integer, default=0)
