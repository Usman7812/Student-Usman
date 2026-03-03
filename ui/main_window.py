import sys
import cv2
import time
import winsound
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar, QTextEdit, QTabWidget, QPushButton, QFrame
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
from ui.ar_overlay import ARRenderer

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("StudySense — AI Smart Study Companion")
        self.resize(1100, 750)
        
        # Internal State
        self.distraction_active = False
        self.last_alert_time = {} # To prevent duplicate rapid logs
        self.last_alarm_time = 0
        self.has_phone = False
        self.focus_data = {}
        self.face_present = False
        self.debug_mode = False
        self.latest_results = {}
        
        # Initialize Core Components
        self.db = DatabaseManager()
        self.db.start_session()
        
        self.decision_engine = DecisionEngine()
        self.burnout_anal = BurnoutAnalyzer(self.db)
        self.gamify_manager = GamificationManager(self.db)
        
        self.setup_ui()
        
        # 1. Start Analysis Thread (Heavy Lifting)
        self.analysis_thread = AnalysisThread(self.db)
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
        
        # Science Status Panel
        science_frame = QFrame()
        science_frame.setStyleSheet("background-color: #1A1A2E; border: 1px solid #2E86AB; border-radius: 10px; padding: 10px; margin-bottom: 5px;")
        science_layout = QVBoxLayout(science_frame)
        
        science_title = QLabel("🔬 SCIENTIFIC PROTOCOLS")
        science_title.setStyleSheet("font-weight: bold; color: #4ECDC4; font-size: 13px; border: none;")
        science_layout.addWidget(science_title)
        
        self.pomodoro_label = QLabel("Pomodoro: --:--")
        self.pomodoro_label.setStyleSheet("color: #E0E0E0; font-family: 'Segoe UI'; border: none;")
        science_layout.addWidget(self.pomodoro_label)
        
        self.eye_break_label = QLabel("Eye Break: --:--")
        self.eye_break_label.setStyleSheet("color: #E0E0E0; font-family: 'Segoe UI'; border: none;")
        science_layout.addWidget(self.eye_break_label)
        
        self.posture_status = QLabel("Posture: ✅ Good")
        self.posture_status.setStyleSheet("color: #2ECC71; font-weight: bold; border: none;")
        science_layout.addWidget(self.posture_status)
        
        right_panel.addWidget(science_frame)

        self.coaching_label = QLabel("💡 AI Coach: Initialize a 50min block for peak cognitive focus.")
        self.coaching_label.setWordWrap(True)
        self.coaching_label.setStyleSheet("font-style: italic; color: #A8D8EA; padding: 10px; border: 1px solid #7FB3D3; background-color: #16213E; border-radius: 5px;")
        right_panel.addWidget(self.coaching_label)

        # Learning & Feedback Panel
        feedback_group = QVBoxLayout()
        feedback_group.addWidget(QLabel("AI Calibration (Learning Mode)"))
        
        self.dismiss_btn = QPushButton("Dismiss False Alarm")
        self.dismiss_btn.setStyleSheet("background-color: #F39C12; color: white; font-weight: bold; padding: 5px;")
        self.dismiss_btn.clicked.connect(self.handle_dismiss_alert)
        self.dismiss_btn.hide() # Only show when distracted
        feedback_group.addWidget(self.dismiss_btn)
        
        self.correct_emo_btn = QPushButton("Correct Emotion")
        self.correct_emo_btn.setStyleSheet("background-color: #3498DB; color: white; font-weight: bold; padding: 5px;")
        self.correct_emo_btn.clicked.connect(self.handle_correct_emotion)
        feedback_group.addWidget(self.correct_emo_btn)
        
        self.debug_btn = QPushButton("Show Debug Vectors")
        self.debug_btn.setCheckable(True)
        self.debug_btn.setStyleSheet("background-color: #444; color: #EEE; padding: 5px;")
        self.debug_btn.toggled.connect(self.toggle_debug)
        feedback_group.addWidget(self.debug_btn)
        
        right_panel.addLayout(feedback_group)
        
        session_layout.addLayout(left_panel, 2)
        session_layout.addLayout(right_panel, 1)

        # Internal State for Learning
        self.last_raw_data = {'pitch': 0, 'emotions': {}}
        
        # Add Dashboard Tab
        self.analytics_tab = AnalyticsDashboard(self.db)
        self.tabs.addTab(self.session_tab, "Live Monitoring")
        self.tabs.addTab(self.analytics_tab, "Insights & Wellbeing")

    def update_frame(self, frame):
        self.analysis_thread.update_frame(frame)
        
        # 1. AR Overlay (if enabled)
        if self.debug_mode:
            frame = ARRenderer.draw_debug(frame, self.latest_results)
            
        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        q_img = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
        self.video_label.setPixmap(QPixmap.fromImage(q_img.scaled(640, 480, Qt.AspectRatioMode.KeepAspectRatio)))

    def toggle_debug(self, state):
        self.debug_mode = state
        self.debug_btn.setText("Hide Debug Vectors" if state else "Show Debug Vectors")

    def process_results(self, results):
        self.latest_results.update(results)
        # 1. Update Internal States from Results
        if 'phone_detections' in results:
            self.has_phone = any(d['conf'] > 0.45 for d in results['phone_detections'])
        
        if 'focus' in results:
            self.focus_data = results['focus']
            self.face_present = results.get('face_present', True)
        elif 'face_present' in results:
            self.face_present = results['face_present']
            if not self.face_present:
                self.focus_data = {} # Clear focus data if face is gone
        
        # 2. Determine Current Status (Priority-Based)
        status_text = f"Status: {self.focus_data.get('status', 'Initializing...')}"
        status_color = "#D6EAF8" # Default
        
        status_map = {
            "Active Study": ("Status: ACTIVE STUDY", "#2ECC71"),
            "Analog Study": ("Status: ANALOG STUDY (Deep Work)", "#2ECC71"),
            "Cognitive Pause": ("Status: COGNITIVE PAUSE", "#3498DB"),
            "Passive Drift": ("Status: PASSIVE DRIFT", "#F39C12"),
            "Daydreaming": ("Status: DAYDREAMING", "#F39C12"),
            "Mobile Usage": ("Status: MOBILE DISTRACTION!", "#E74C3C"),
            "Session Paused": ("Status: SESSION PAUSED", "#95A5A6")
        }
        
        if self.focus_data.get('status') in status_map:
            status_text, status_color = status_map[self.focus_data['status']]
            
        # Alarm Logic for high priority
        if self.focus_data.get('status') == "Mobile Usage":
            self.add_alert("Mobile Distraction Detected!", debounce=5)
            self.play_alarm(frequency=1200, duration=600)
            self.distraction_active = True
        elif self.focus_data.get('alert_level', 0) >= 1:
            self.distraction_active = True
            if self.focus_data.get('status') == "Passive Drift":
                self.add_alert("Passive Drift detected. Focus back on task?", debounce=30)
        else:
            self.distraction_active = False

        # Apply UI Changes
        self.status_label.setText(status_text)
        self.status_label.setStyleSheet(f"font-size: 18px; color: {status_color}; font-weight: bold;")
        self.dismiss_btn.setVisible(self.distraction_active)

        # 3. Update Learning State
        self.dismiss_btn.setVisible(self.distraction_active)
        if 'focus' in results and 'pitch' in results['focus']:
            self.last_raw_data['pitch'] = results['focus']['pitch']
        if 'emotion' in results and 'probs' in results['emotion']:
            self.last_raw_data['emotions'] = results['emotion']['probs']

        # 4. Secondary Metrics
        if 'fatigue' in results:
            self.fatigue_bar.setValue(int(results['fatigue']['fatigue_score']))
            if results['fatigue']['alert_needed']: 
                self.add_alert(results['fatigue']['alert_msg'], debounce=10)
            
        if 'emotion' in results and results['emotion'] and 'current_emotion' in results['emotion']:
            # Vector matching returns 'current_emotion'
            emo = results['emotion']['current_emotion'].capitalize()
            self.emotion_label.setText(f"Emotion: {emo}")

        # 5. Scientific Coaching Suggestions
        if 'coach' in results:
            coach_data = results['coach']
            
            # Update Timers
            timers = coach_data['timers']
            p_min, p_sec = divmod(timers['pomodoro_remaining_s'], 60)
            e_min, e_sec = divmod(timers['eye_break_remaining_s'], 60)
            
            self.pomodoro_label.setText(f"Pomodoro: {p_min:02d}:{p_sec:02d}")
            self.eye_break_label.setText(f"Eye Break: {e_min:02d}:{e_sec:02d}")
            
            # Update Posture
            if coach_data.get('is_slumped', False):
                self.posture_status.setText("Posture: ⚠️ Slumped")
                self.posture_status.setStyleSheet("color: #E74C3C; font-weight: bold; border: none;")
            else:
                self.posture_status.setText("Posture: ✅ Good")
                self.posture_status.setStyleSheet("color: #2ECC71; font-weight: bold; border: none;")

            if coach_data['suggestions']:
                # Update with the first (most relevant) suggestion
                self.coaching_label.setText(f"💡 AI Coach: {coach_data['suggestions'][0]}")
            
            if coach_data['alerts']:
                for alert in coach_data['alerts']:
                    self.add_alert(f"📋 {alert}", debounce=60)
                # Play a softer, instructional chime for coach alerts
                self.play_alarm(frequency=600, duration=300)

    def play_alarm(self, frequency=None, duration=None):
        if SOUND_ALERTS_ENABLED:
            current_time = time.time()
            if current_time - self.last_alarm_time > 2.5: # 2.5s cooldown for non-intrusive feel
                f = frequency if frequency else ALARM_FREQUENCY
                d = duration if duration else ALARM_DURATION
                winsound.Beep(int(f), int(d))
                self.last_alarm_time = current_time

    def handle_dismiss_alert(self):
        # AI was wrong about distraction
        self.db.log_feedback(
            event_type='distraction',
            is_false_positive=True,
            pitch=self.last_raw_data.get('pitch')
        )
        self.add_alert("Learning: Distraction dismissed. Optimizing thresholds...", debounce=0)
        self.dismiss_btn.hide()

    def handle_correct_emotion(self):
        from PyQt6.QtWidgets import QInputDialog
        emotions = ['Angry', 'Happy', 'Sad', 'Neutral', 'Surprise']
        item, ok = QInputDialog.getItem(self, "Correct Emotion", "What are you actually feeling?", emotions, 0, False)
        if ok and item:
            import json
            # Ensure all values in emotions dict are standard Python floats for JSON serialization
            emotions_data = {k: float(v) for k, v in self.last_raw_data.get('emotions', {}).items()}
            
            self.db.log_feedback(
                event_type='emotion',
                is_false_positive=True,
                correction_detail=item,
                emotions_json=json.dumps(emotions_data)
            )
            self.add_alert(f"Learning: Emotion corrected to {item}. Optimizing model...", debounce=0)

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
