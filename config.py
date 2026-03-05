import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- Vision Settings ---
CAMERA_INDEX = 0
TARGET_FPS = 24  # Increased for smooth visual experience
FRAME_WIDTH = 640
FRAME_HEIGHT = 480

# --- Analysis Intervals (seconds) ---
FACE_POSE_INTERVAL = 0.05   # 20 Hz for rapid response
PHONE_DETECTION_INTERVAL = 0.35 # 2.8 Hz for quick distraction detection
EMOTION_SAMPLE_INTERVAL = 2.0  # 0.5 Hz
COACHING_INTERVAL = 300    # 5 minutes

# --- Fatigue Detection ---
EAR_THRESHOLD = 0.22 # Slightly more sensitive (lower means more closed)
EAR_CONSEC_FRAMES = 15 # frames at 24fps ~ 0.6s
MAR_THRESHOLD = 0.5
YAWN_CONSEC_FRAMES = 20

# --- Focus & Distraction Logic (Research-Backed) ---
YAW_THRESHOLD = 30    # degrees
PITCH_THRESHOLD = 20  # degrees
LOOKING_DOWN_THRESHOLD = 40 # degrees (pitch down)
LOOK_UP_RESET_THRESHOLD = 3.0 # seconds

# Sample Windows (Seconds)
WINDOW_DIGITAL_FOCUS = 1.0
WINDOW_ANALOG_STUDY = 8.0
WINDOW_COGNITIVE_PAUSE = 15.0
WINDOW_PASSIVE_DRIFT = 30.0
WINDOW_MOBILE_USAGE = 2.0
WINDOW_DAYDREAMING = 30.0
WINDOW_FATIGUE_AVG = 60.0

# Behavioral Signatures
SACCADE_RATIO_THRESHOLD = 0.7  # Ratio of horizontal vs vertical eye movement
EXPRESSION_SPIKE_WINDOW = 5.0   # Window to detect rapid micro-expressions
MOBILE_ALARM_DELAY = 1.0        # Persistence before alarm
FATIGUE_BREAK_THRESHOLD = 75.0  # Fatigue score to suggest break

# Distraction Thresholds
GAZE_THRESHOLD = 0.35  # Relative eye movement
EYE_GRACE_PERIOD = 2.0 # Seconds before alert
MORNING_BOOST = 1.1    # Focus threshold multiplier for morning
FOCUS_ALERT_THRESHOLD = 60 # focus % below which alert is triggered

# --- Feedback Settings ---
SOUND_ALERTS_ENABLED = True
VOICE_COACHING_ENABLED = True
ALARM_FREQUENCY = 1000 # Hz for beep
ALARM_DURATION = 500   # ms

# --- Distraction & Object Settings ---
PHONE_CONF_THRESHOLD = 0.40 
PHONE_CLASS_ID = 67 # YOLOv8/v11 COCO class for cell phone
YOLO_SUSPICIOUS_INTERVAL = 0.15
USE_GPU = True    # Enable CUDA if available
USE_OPENVINO = True # Fallback for fast CPU inference

# Detailed Object Categories for Analysis
STUDY_TOOLS = [73, 63, 66] # book, laptop, keyboard
DISTRACTIONS = [PHONE_CLASS_ID]
ENVIRONMENT = [0, 39, 56]   # person, bottle, chair

# --- Emotion Settings ---
EMOTION_WINDOW = 120 # seconds
EMOTION_SMOOTHING_SAMPLES = 10 
EMOTION_EMA_ALPHA = 0.3 # Smoothing factor (lower = more stable, higher = more reactive)

# --- API Settings ---
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
CLAUDE_MODEL = "claude-3-haiku-20240307"
YOLO_MODEL_PATH = "yolo11n.pt" # Upgraded to v11

# --- Database Settings ---
DB_PATH = "sqlite:///studysense.db"
