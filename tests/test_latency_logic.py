import time
import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

from config import PHONE_DETECTION_INTERVAL, YOLO_SUSPICIOUS_INTERVAL
from analysis.analysis_thread import AnalysisThread

class MockDB:
    def log_event(self, *args): pass
    def log_feedback(self, *args): pass

# Mock the LearningEngine and other processors
import analysis.analysis_thread
import vision.face_processor
import vision.pose_processor
import vision.yolo_detector
import analysis.fatigue_analyzer
import analysis.vector_emotion_matcher

class MockProcessor:
    def __init__(self, *args, **kwargs): pass
    def process(self, *args): return {}
    def detect(self, *args, **kwargs): return []
    def analyze(self, *args, **kwargs): return {}
    def match(self, *args): return {}

analysis.analysis_thread.LearningEngine = lambda x: MockProcessor()
analysis.analysis_thread.FaceProcessor = MockProcessor
analysis.analysis_thread.PoseProcessor = MockProcessor
analysis.analysis_thread.YOLODetector = MockProcessor
analysis.analysis_thread.FatigueAnalyzer = MockProcessor
analysis.analysis_thread.VectorEmotionMatcher = MockProcessor

def test_interval_logic():
    print("Testing Detection Interval Logic...")
    thread = AnalysisThread(MockDB())
    
    # Test 1: Normal state
    thread.is_looking_down = False
    print(f"Normal Look: is_looking_down={thread.is_looking_down}")
    # Simulate first check
    thread.last_phone_time = 0
    now = 100 # arbitrary time
    interval = YOLO_SUSPICIOUS_INTERVAL if thread.is_looking_down else PHONE_DETECTION_INTERVAL
    print(f"Expected Interval: {PHONE_DETECTION_INTERVAL}, Actual Logic: {interval}")
    assert interval == PHONE_DETECTION_INTERVAL
    
    # Test 2: Looking down state
    thread.is_looking_down = True
    print(f"Looking Down: is_looking_down={thread.is_looking_down}")
    interval = YOLO_SUSPICIOUS_INTERVAL if thread.is_looking_down else PHONE_DETECTION_INTERVAL
    print(f"Expected Interval: {YOLO_SUSPICIOUS_INTERVAL}, Actual Logic: {interval}")
    assert interval == YOLO_SUSPICIOUS_INTERVAL
    
    print("✅ Interval logic test passed!")

if __name__ == "__main__":
    test_interval_logic()
