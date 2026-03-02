from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QGridLayout
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

class AnalyticsDashboard(QWidget):
    def __init__(self, db_manager):
        super().__init__()
        self.db = db_manager
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        # Title
        title = QLabel("Performance & Wellbeing Dashboard")
        title.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        title.setStyleSheet("color: #2E86AB;")
        layout.addWidget(title)
        
        # Top Grid: Stats Cards
        grid = QGridLayout()
        
        self.points_card = self.create_stat_card("Focus Points", "0", "#F4D03F")
        self.streak_card = self.create_stat_card("Day Streak", "0", "#E67E22")
        self.burnout_card = self.create_stat_card("Burnout Risk", "Low", "#E74C3C")
        
        grid.addWidget(self.points_card, 0, 0)
        grid.addWidget(self.streak_card, 0, 1)
        grid.addWidget(self.burnout_card, 0, 2)
        
        layout.addLayout(grid)
        
        # Recommendations Area
        rec_frame = QFrame()
        rec_frame.setStyleSheet("background-color: #16213E; border-radius: 10px; padding: 15px;")
        rec_layout = QVBoxLayout(rec_frame)
        rec_layout.addWidget(QLabel("AI Recommendations:"))
        self.rec_label = QLabel("Keep up the consistent work! You're performing at your peak focus.")
        self.rec_label.setWordWrap(True)
        self.rec_label.setStyleSheet("color: #A8D8EA; font-style: italic;")
        rec_layout.addWidget(self.rec_label)
        
        layout.addWidget(rec_frame)
        layout.addStretch()

    def create_stat_card(self, title, value, color):
        frame = QFrame()
        frame.setStyleSheet(f"background-color: #1A1A2E; border: 1px solid {color}; border-radius: 15px;")
        layout = QVBoxLayout(frame)
        
        t_label = QLabel(title)
        t_label.setStyleSheet("color: #888; font-size: 14px;")
        layout.addWidget(t_label)
        
        v_label = QLabel(value)
        v_label.setStyleSheet(f"color: {color}; font-size: 32px; font-weight: bold;")
        v_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(v_label)
        
        # Store label for updates
        frame.value_label = v_label
        return frame

    def update_stats(self, points, streak, risk_score):
        self.points_card.value_label.setText(str(points))
        self.streak_card.value_label.setText(str(streak))
        
        risk_text = "Low"
        if risk_score > 70: risk_text = "High"
        elif risk_score > 30: risk_text = "Moderate"
        self.burnout_card.value_label.setText(risk_text)
        
        # Update recommendation based on risk
        if risk_score > 70:
            self.rec_label.setText("Critical burnout risk detected. We strongly suggest taking the rest of the day off to recharge.")
        elif risk_score > 30:
            self.rec_label.setText("You're showing signs of cumulative fatigue. Consider shorter study blocks today.")
        else:
            self.rec_label.setText("Your patterns look healthy. Keep maintaining this balanced pace!")
