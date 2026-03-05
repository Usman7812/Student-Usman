import time
import cv2
from PyQt6.QtCore import QThread, pyqtSignal
from vision.face_processor import FaceProcessor
from vision.pose_processor import PoseProcessor
from vision.yolo_detector import YOLODetector
from analysis.fatigue_analyzer import FatigueAnalyzer
from analysis.vector_emotion_matcher import VectorEmotionMatcher
from analysis.focus_analyzer import FocusAnalyzer
from analysis.scientific_coach import ScientificCoach
import os
from config import (
    FACE_POSE_INTERVAL, 
    PHONE_DETECTION_INTERVAL, 
    EMOTION_SAMPLE_INTERVAL,
    PHONE_CONF_THRESHOLD,
    YOLO_SUSPICIOUS_INTERVAL
)
from analysis.learning_engine import LearningEngine

class AnalysisThread(QThread):
    results_ready = pyqtSignal(dict)

    def __init__(self, db_manager):
        super().__init__()
        self.db = db_manager
        self.learning_engine = LearningEngine(self.db)
        self.running = False
        self.current_frame = None
        
        # Processors
        self.face_proc = FaceProcessor()
        self.pose_proc = PoseProcessor()
        self.yolo_proc = YOLODetector()
        
        # Analyzers
        self.fatigue_anal = FatigueAnalyzer()
        self.emotion_anal = VectorEmotionMatcher(os.path.join('assets', 'emotion_vectors.json'))
        self.focus_anal = FocusAnalyzer()
        self.coach = ScientificCoach()
        
        # Timers
        self.last_face_time = 0
        self.last_phone_time = 0
        self.last_emotion_time = 0
        self.last_coach_time = 0

    def update_frame(self, frame):
        self.current_frame = frame.copy()

    def run(self):
        self.running = True
        
        # Apply Personalized Learnings
        # thresholds = self.learning_engine.get_thresholds()
        # self.focus_anal.reconfigure(thresholds)
        
        while self.running:
            if self.current_frame is None:
                time.sleep(0.01)
                continue
                
            current_time = time.time()
            results = {}
            frame_to_process = self.current_frame
            
            # 1. Objects (YOLO) - Variable Interval Detection
            # Determine interval: If looking down, scan MUCH faster to confirm distraction
            is_looking_down = results.get('focus', {}).get('is_looking_down', False)
            current_phone_interval = YOLO_SUSPICIOUS_INTERVAL if is_looking_down else PHONE_DETECTION_INTERVAL
            
            if current_time - self.last_phone_time >= current_phone_interval:
                results['phone_detections'] = self.yolo_proc.detect(frame_to_process, conf=PHONE_CONF_THRESHOLD)
                self.last_phone_time = current_time

            # 2. Face & Pose (20 Hz)
            if current_time - self.last_face_time >= FACE_POSE_INTERVAL:
                face_data = self.face_proc.process(frame_to_process)
                pose_data = self.pose_proc.process(frame_to_process)
                
                if face_data:
                    results['face_data'] = face_data
                    pose_metrics = pose_data['metrics'] if pose_data else None
                    fatigue_results = self.fatigue_anal.analyze(face_data['fatigue_metrics'], pose_metrics)
                    results['fatigue'] = fatigue_results
                    
                    # New Inferential Focus Analysis
                    results['focus'] = self.focus_anal.analyze(
                        face_data, 
                        pose_data, 
                        results.get('phone_detections', []), 
                        fatigue_results.get('score', 0)
                    )
                    results['face_present'] = True
                else:
                    results['face_present'] = False
                    # Still run focus analysis with objects even if face is missing
                    results['focus'] = self.focus_anal.analyze(None, None, results.get('phone_detections', []), 0)
                
                # Scientific Coaching (Every 5 seconds)
                if current_time - self.last_coach_time >= 5.0:
                    results['coach'] = self.coach.analyze(results)
                    self.last_coach_time = current_time
                
                if pose_data:
                    results['pose_data'] = pose_data
                
                self.last_face_time = current_time

            # 3. Emotion Detection (Neural Vector Matching)
            if current_time - self.last_emotion_time >= EMOTION_SAMPLE_INTERVAL:
                # Use high-fidelity blendshapes from face_data if available
                if 'face_data' in results and 'blendshapes' in results['face_data']:
                    results['emotion'] = self.emotion_anal.match(results['face_data']['blendshapes'])
                self.last_emotion_time = current_time

            if results:
                self.results_ready.emit(results)
            
            # Small sleep to prevent 100% CPU usage
            time.sleep(0.01)

    def stop(self):
        self.running = False
        self.wait()
