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
PHONE_DETECTION_INTERVAL = 0.5 # 2 Hz for quick distraction detection
EMOTION_SAMPLE_INTERVAL = 2.0  # 0.5 Hz
COACHING_INTERVAL = 300    # 5 minutes

# --- Fatigue Detection ---
EAR_THRESHOLD = 0.22 # Slightly more sensitive (lower means more closed)
EAR_CONSEC_FRAMES = 15 # frames at 24fps ~ 0.6s
MAR_THRESHOLD = 0.5
YAWN_CONSEC_FRAMES = 20

# --- Focus Detection ---
YAW_THRESHOLD = 30    # degrees
PITCH_THRESHOLD = 20  # degrees
LOOKING_DOWN_THRESHOLD = 40 # degrees (pitch down - more responsive default)
LOOKING_DOWN_GRACE_PERIOD = 15 # seconds (allow deep reading)
LOOK_UP_RESET_THRESHOLD = 3.0 # seconds (must look up for 3s to reset deep distraction)
FOCUS_SCORE_WINDOW = 120 # seconds (2 minutes)
FOCUS_ALERT_THRESHOLD = 60 # focus % below which alert is triggered

# --- Feedback Settings ---
SOUND_ALERTS_ENABLED = True
VOICE_COACHING_ENABLED = True
ALARM_FREQUENCY = 1000 # Hz for beep
ALARM_DURATION = 500   # ms

# --- Distraction Settings ---
PHONE_CONF_THRESHOLD = 0.45 # Higher for reduced false positives
PHONE_CLASS_ID = 67 # YOLOv8 COCO class for cell phone
YOLO_SUSPICIOUS_INTERVAL = 0.2 # Scan faster when user is looking down

# --- Emotion Settings ---
EMOTION_WINDOW = 120 # seconds
EMOTION_SMOOTHING_SAMPLES = 10 
EMOTION_EMA_ALPHA = 0.3 # Smoothing factor (lower = more stable, higher = more reactive)

# --- API Settings ---
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
CLAUDE_MODEL = "claude-3-haiku-20240307" # Haiku for speed and cost, as specified in prompt

# --- Database Settings ---
DB_PATH = "sqlite:///studysense.db"
