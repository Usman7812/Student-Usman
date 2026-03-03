import os
import cv2
from config import PHONE_CLASS_ID

# --- FIX: OpenMP/DLL Initialization for PyTorch ---
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
# -------------------------------------------------

try:
    from ultralytics import YOLO
    HAS_YOLO = True
except (ImportError, OSError) as e:
    HAS_YOLO = False
    # Only print if we are sure it's a DLL issue
    print(f"[SYSTEM] YOLO Distraction Detection disabled (Reason: {e})")

class YOLODetector:
    def __init__(self, model_name='yolov8n.pt'):
        # Nano model for speed as requested
        self.model = None
        if HAS_YOLO:
            try:
                self.model = YOLO(model_name)
                # Class IDs: 67: phone, 73: book, 63: laptop
                self.classes = [PHONE_CLASS_ID, 73, 63]
            except (Exception, OSError):
                print("[SYSTEM] YOLO initialization failed due to environment issues.")
                self.model = None

    def detect(self, frame, conf=0.25):
        if self.model is None:
            return []
        # Run inference with confidence threshold
        try:
            results = self.model(frame, classes=self.classes, conf=conf, verbose=False)
        except Exception:
            return []
        
        detections = []
        for r in results:
            for box in r.boxes:
                detections.append({
                    'class': int(box.cls[0]),
                    'conf': float(box.conf[0]),
                    'bbox': box.xyxy[0].tolist() # [x1, y1, x2, y2]
                })
        
        return detections
