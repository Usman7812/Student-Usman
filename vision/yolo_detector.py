import cv2
from ultralytics import YOLO
from config import PHONE_CLASS_ID

class YOLODetector:
    def __init__(self, model_name='yolov8n.pt'):
        # Nano model for speed as requested
        self.model = YOLO(model_name)
        self.classes = [PHONE_CLASS_ID]

    def detect(self, frame, conf=0.25):
        # Run inference with confidence threshold
        results = self.model(frame, classes=self.classes, conf=conf, verbose=False)
        
        detections = []
        for r in results:
            for box in r.boxes:
                detections.append({
                    'class': int(box.cls[0]),
                    'conf': float(box.conf[0]),
                    'bbox': box.xyxy[0].tolist() # [x1, y1, x2, y2]
                })
        
        return detections
