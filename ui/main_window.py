import sys
import cv2
import time
import winsound
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar, QTextEdit, QTabWidget, QPushButton
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtCore import Qt, QTimer
from database.db_manager import DatabaseManager
from analysis.decision_engine import DecisionEngine
from analysis.burnout_analyzer import BurnoutAnalyzer
from analysis.gamification_manager import GamificationManager
from analysis.analysis_thread import AnalysisThread
from vision.camera import CameraThread
from ui.analytics_dashboard import AnalyticsDashboard
from config import SOUND_ALERTS_ENABLED, ALARM_FREQUENCY, ALARM_DURATION

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("StudySense — AI Smart Study Companion")
        self.resize(1100, 750)
        
        # Internal State
        self.distraction_active = False
        self.last_alert_time = {} # To prevent duplicate rapid logs
        self.last_alarm_time = 0
        
        # Initialize Core Components
        self.db = DatabaseManager()
        self.db.start_session()
        
        self.decision_engine = DecisionEngine()
        self.burnout_anal = BurnoutAnalyzer(self.db)
        self.gamify_manager = GamificationManager(self.db)
        
        self.setup_ui()
        
        # 1. Start Analysis Thread (Heavy Lifting)
        self.analysis_thread = AnalysisThread()
        self.analysis_thread.results_ready.connect(self.process_results)
        self.analysis_thread.start()

        # 2. Start Camera Thread (Smooth Feed)
        self.camera_thread = CameraThread()
        self.camera_thread.frame_ready.connect(self.update_frame)
        self.camera_thread.start()

        # Gamification timer (Update points every 1 min)
        self.study_timer = QTimer()
        self.study_timer.timeout.connect(self.update_study_points)
        self.study_timer.start(60000) # 1 minute
        
        # Initial Daily Stat Update
        self.refresh_stats()

    def setup_ui(self):
        # Tabs system
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        
        # Live Session Tab
        self.session_tab = QWidget()
        session_layout = QHBoxLayout(self.session_tab)
        
        # Left Panel (Webcam)
        left_panel = QVBoxLayout()
        self.video_label = QLabel("Loading Camera...")
        self.video_label.setFixedSize(640, 480)
        self.video_label.setStyleSheet("background-color: black; border: 2px solid #2E86AB; border-radius: 10px;")
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_panel.addWidget(self.video_label)
        
        # Quick Stats bar
        stats_bar = QHBoxLayout()
        self.status_label = QLabel("Status: Initializing...")
        self.status_label.setStyleSheet("font-size: 18px; color: #D6EAF8; font-weight: bold;")
        stats_bar.addWidget(self.status_label)
        
        self.emotion_label = QLabel("Emotion: Neutral")
        stats_bar.addWidget(self.emotion_label)
        left_panel.addLayout(stats_bar)
        
        self.fatigue_bar = QProgressBar()
        self.fatigue_bar.setRange(0, 100)
        self.fatigue_bar.setFormat("Fatigue: %v%")
        left_panel.addWidget(self.fatigue_bar)
        
        # Right Panel (Alerts)
        right_panel = QVBoxLayout()
        right_panel.addWidget(QLabel("Real-time Activity Log"))
        self.alert_log = QTextEdit()
        self.alert_log.setReadOnly(True)
        self.alert_log.setStyleSheet("background-color: #16213E; color: #A8D8EA; font-family: 'Consolas'; border-radius: 5px;")
        right_panel.addWidget(self.alert_log)
        
        self.coaching_label = QLabel("Welcome to StudySense! Keep focused for bonus points.")
        self.coaching_label.setWordWrap(True)
        self.coaching_label.setStyleSheet("font-style: italic; color: #A8D8EA; padding: 10px; border: 1px solid #7FB3D3; background-color: #1A1A2E; border-radius: 5px;")
        right_panel.addWidget(self.coaching_label)
        
        session_layout.addLayout(left_panel, 2)
        session_layout.addLayout(right_panel, 1)
        
        # Add Dashboard Tab
        self.analytics_tab = AnalyticsDashboard(self.db)
        self.tabs.addTab(self.session_tab, "Live Monitoring")
        self.tabs.addTab(self.analytics_tab, "Insights & Wellbeing")

    def update_frame(self, frame):
        self.analysis_thread.update_frame(frame)
        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        q_img = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
        self.video_label.setPixmap(QPixmap.fromImage(q_img.scaled(640, 480, Qt.AspectRatioMode.KeepAspectRatio)))

    def process_results(self, results):
        # 1. Distraction State Tracking
        has_phone = False
        if 'phone_detections' in results:
            has_phone = any(d['conf'] > 0.45 for d in results['phone_detections'])
        
        focus_data = results.get('focus', {})
        is_looking_down = focus_data.get('is_looking_down', False)
        alert_level = focus_data.get('alert_level', 0)
        
        self.distraction_active = has_phone or (alert_level > 0)
        
        # 2. 3-Stage UI Priority
        if has_phone:
            self.status_label.setText("Status: DISTRACTED (Phone)")
            self.status_label.setStyleSheet("font-size: 18px; color: #E74C3C; font-weight: bold;")
            self.add_alert("Distraction Confirmed: Mobile Phone detected.", debounce=5)
            self.play_alarm(frequency=1200, duration=600) # Urgent phone beep
            
        elif alert_level == 3: # Persistent Look-Down
            self.status_label.setText("Status: PERSISTENT DISTRACTION")
            self.status_label.setStyleSheet("font-size: 18px; color: #E74C3C; font-weight: bold;")
            self.add_alert(focus_data.get('alert_msg', ""), debounce=5)
            self.play_alarm(frequency=1000, duration=500) # Standard alarm
            
        elif alert_level == 2: # Nudge
            self.status_label.setText("Status: LOOKING DOWN (Nudge)")
            self.status_label.setStyleSheet("font-size: 18px; color: #F39C12; font-weight: bold;")
            self.add_alert(focus_data.get('alert_msg', ""), debounce=10)
            self.play_alarm(frequency=800, duration=200) # Subtle short nudge
            
        elif alert_level == 1: # Visual Only
            self.status_label.setText("Status: LOOKING DOWN")
            self.status_label.setStyleSheet("font-size: 18px; color: #F39C12; font-weight: bold;")
            # No sound for level 1
            
        elif 'face_present' in results and not results['face_present']:
            self.status_label.setText("Status: FACE MISSING")
            self.status_label.setStyleSheet("font-size: 18px; color: #95A5A6; font-weight: bold;")
            
        elif focus_data.get('focus_score', 100) < 60:
            self.status_label.setText("Status: LOOKING AWAY")
            self.status_label.setStyleSheet("font-size: 18px; color: #F39C12; font-weight: bold;")
            
        else:
            self.status_label.setText("Status: FOCUSED")
            self.status_label.setStyleSheet("font-size: 18px; color: #2ECC71; font-weight: bold;")

        # 3. Secondary Metrics
        if 'fatigue' in results:
            self.fatigue_bar.setValue(int(results['fatigue']['fatigue_score']))
            if results['fatigue']['alert_needed']: 
                self.add_alert(results['fatigue']['alert_msg'], debounce=10)
            
        if 'emotion' in results and results['emotion'] and results['emotion'].get('is_stable', False):
            # Average emotions to reduce jitter
            emo = results['emotion']['current_emotion'].capitalize()
            self.emotion_label.setText(f"Emotion: {emo}")

    def play_alarm(self, frequency=None, duration=None):
        if SOUND_ALERTS_ENABLED:
            current_time = time.time()
            if current_time - self.last_alarm_time > 2.5: # 2.5s cooldown for non-intrusive feel
                f = frequency if frequency else ALARM_FREQUENCY
                d = duration if duration else ALARM_DURATION
                winsound.Beep(int(f), int(d))
                self.last_alarm_time = current_time

    def add_alert(self, msg, debounce=0):
        # Check debounce timer
        current_time = time.time()
        if debounce > 0:
            if msg in self.last_alert_time and current_time - self.last_alert_time[msg] < debounce:
                return
        
        self.last_alert_time[msg] = current_time
        timestamp = time.strftime('%H:%M:%S')
        self.alert_log.append(f"<span style='color: #4ECDC4;'>[{timestamp}]</span> {msg}")
        self.db.log_event('alert', msg)

    def update_study_points(self):
        # Only add points if focused and no distractions
        if self.status_label.text() == "Status: FOCUSED":
            points = self.gamify_manager.add_points(1)
            self.gamify_manager.update_daily_progress(1) # minutes
            self.refresh_stats()

    def refresh_stats(self):
        from database.models import UserStats
        with self.db.Session() as session:
            stats = session.query(UserStats).first()
            if stats:
                risk_score = self.burnout_anal.calculate_burnout_risk()
                self.analytics_tab.update_stats(
                    stats.total_points, 
                    stats.current_streak, 
                    risk_score
                )
        self.gamify_manager.update_streak()

    def closeEvent(self, event):
        self.camera_thread.stop()
        self.analysis_thread.stop()
        self.db.end_session()
        event.accept()

if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
