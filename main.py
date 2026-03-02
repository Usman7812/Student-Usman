import os
import sys
import logging

# Suppress TensorFlow, Keras, and MediaPipe warnings/logs
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # 0: all, 1: no INFO, 2: no INFO/WARN, 3: no INFO/WARN/ERROR
os.environ['GLOG_minloglevel'] = '2'      # 0: INFO, 1: WARNING, 2: ERROR, 3: FATAL
os.environ['ABSL_LOGGING_LEVEL'] = 'none' # Disable Abseil logging
logging.getLogger('tensorflow').setLevel(logging.ERROR)

# Import AI libraries BEFORE PyQt6 to prevent DLL conflicts
try:
    import tensorflow as tf
    tf.get_logger().setLevel('ERROR')
    import deepface
except ImportError:
    pass

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
