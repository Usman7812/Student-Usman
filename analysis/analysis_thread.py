import time
import cv2
from PyQt6.QtCore import QThread, pyqtSignal
from vision.face_processor import FaceProcessor
from vision.pose_processor import PoseProcessor
from vision.yolo_detector import YOLODetector
from analysis.fatigue_analyzer import FatigueAnalyzer
from analysis.emotion_analyzer import EmotionAnalyzer
from analysis.focus_analyzer import FocusAnalyzer
from config import (
    FACE_POSE_INTERVAL, 
    PHONE_DETECTION_INTERVAL, 
    EMOTION_SAMPLE_INTERVAL,
    PHONE_CONF_THRESHOLD,
    YOLO_SUSPICIOUS_INTERVAL
)

class AnalysisThread(QThread):
    results_ready = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.running = False
        self.current_frame = None
        
        # Processors
        self.face_proc = FaceProcessor()
        self.pose_proc = PoseProcessor()
        self.yolo_proc = YOLODetector()
        
        # Analyzers
        self.fatigue_anal = FatigueAnalyzer()
        self.emotion_anal = EmotionAnalyzer()
        self.focus_anal = FocusAnalyzer()
        
        # Timers
        self.last_face_time = 0
        self.last_phone_time = 0
        self.last_emotion_time = 0

    def update_frame(self, frame):
        self.current_frame = frame.copy()

    def run(self):
        self.running = True
        while self.running:
            if self.current_frame is None:
                time.sleep(0.01)
                continue
                
            current_time = time.time()
            results = {}
            frame_to_process = self.current_frame
            
            # 1. Face & Pose (20 Hz)
            if current_time - self.last_face_time >= FACE_POSE_INTERVAL:
                face_data = self.face_proc.process(frame_to_process)
                pose_data = self.pose_proc.process(frame_to_process)
                
                if face_data:
                    results['fatigue'] = self.fatigue_anal.analyze(face_data['fatigue_metrics'])
                    results['focus'] = self.focus_anal.analyze(face_data['head_pose'])
                    results['face_present'] = True
                else:
                    results['face_present'] = False
                    results['focus'] = {'alert_needed': True, 'alert_msg': "Face not detected!"}
                
                if pose_data:
                    results['pose_data'] = pose_data
                
                self.last_face_time = current_time

            # 2. Variable Phone Detection (YOLO)
            # Determine interval: If looking down, scan MUCH faster to confirm distraction
            is_looking_down = results.get('focus', {}).get('is_looking_down', False)
            current_phone_interval = YOLO_SUSPICIOUS_INTERVAL if is_looking_down else PHONE_DETECTION_INTERVAL
            
            if current_time - self.last_phone_time >= current_phone_interval:
                # Always send this key if the interval hits, so UI can clear state
                results['phone_detections'] = self.yolo_proc.detect(frame_to_process, conf=PHONE_CONF_THRESHOLD)
                self.last_phone_time = current_time

            # 3. Emotion Detection (DeepFace)
            if current_time - self.last_emotion_time >= EMOTION_SAMPLE_INTERVAL:
                results['emotion'] = self.emotion_anal.analyze(frame_to_process)
                self.last_emotion_time = current_time

            if results:
                self.results_ready.emit(results)
            
            # Small sleep to prevent 100% CPU usage
            time.sleep(0.01)

    def stop(self):
        self.running = False
        self.wait()
