import os
import sys
import logging

# Suppress MediaPipe and general logging
os.environ['GLOG_minloglevel'] = '2'      # 0: INFO, 1: WARNING, 2: ERROR, 3: FATAL
os.environ['ABSL_LOGGING_LEVEL'] = 'none' # Disable Abseil logging

from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow

# Ensure directories exist for assets if not already there
os.makedirs("assets/icons", exist_ok=True)
os.makedirs("assets/sounds", exist_ok=True)

def main():
    """
    Main entry point for StudySense.
    """
    app = QApplication(sys.argv)
    
    # Modern Dark Theme for WOW effect
    app.setStyle("Fusion")
    
    # Set app-wide stylesheet for a premium feel
    app.setStyleSheet("""
        QMainWindow {
            background-color: #1A1A2E;
        }
        QLabel {
            color: #E0E0E0;
            font-family: 'Segoe UI', sans-serif;
            font-size: 14px;
        }
        QProgressBar {
            border: 2px solid #2E86AB;
            border-radius: 5px;
            text-align: center;
            background-color: #16213E;
            color: white;
            height: 25px;
        }
        QProgressBar::chunk {
            background-color: #2E86AB;
        }
        QTextEdit {
            background-color: #16213E;
            border: 1px solid #2E86AB;
            border-radius: 10px;
            padding: 5px;
            color: #A8D8EA;
        }
    """)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
