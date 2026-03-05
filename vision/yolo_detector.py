import os
import cv2
from config import PHONE_CLASS_ID, YOLO_MODEL_PATH, USE_GPU, USE_OPENVINO

# --- FIX: OpenMP/DLL Initialization for PyTorch ---
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
# -------------------------------------------------

try:
    from ultralytics import YOLO
    import torch
    HAS_YOLO = True
except (ImportError, OSError) as e:
    HAS_YOLO = False
    print(f"[SYSTEM] YOLO Detection disabled (Reason: {e})")

class YOLODetector:
    def __init__(self, model_name=YOLO_MODEL_PATH):
        self.model = None
        if not HAS_YOLO:
            return

        try:
            # 1. Determine Device
            device = 'cpu'
            if USE_GPU and torch.cuda.is_available():
                device = 0 # CUDA device 0
                print(f"[SYSTEM] YOLO using GPU: {torch.cuda.get_device_name(0)}")
            else:
                print("[SYSTEM] YOLO using CPU (CUDA not available)")

            # 2. Load/Export Model
            self.model = YOLO(model_name)
            
            # 3. OpenVINO Optimization (if on CPU)
            if device == 'cpu' and USE_OPENVINO:
                ov_path = model_name.replace('.pt', '_openvino_model')
                if not os.path.exists(ov_path):
                    print(f"[SYSTEM] Exporting {model_name} to OpenVINO for faster CPU inference...")
                    self.model.export(format='openvino')
                
                # Load the optimized model
                self.model = YOLO(ov_path, task='detect')
                print(f"[SYSTEM] YOLO using OpenVINO optimized model")
            else:
                # Move to GPU if selected
                self.model.to(device)

            # Class IDs: 67: phone, 73: book, 63: laptop, 0: person, etc.
            self.classes = [PHONE_CLASS_ID, 73, 63, 66, 0, 39, 56]
        except Exception as e:
            print(f"[SYSTEM] YOLO initialization failed: {e}")
            self.model = None

    def detect(self, frame, conf=0.25):
        if self.model is None:
            return []
        
        try:
            results = self.model(frame, classes=self.classes, conf=conf, verbose=False)
        except Exception:
            return []
        
        detections = []
        for r in results:
            for box in r.boxes:
                cls_id = int(box.cls[0])
                label = self.model.names[cls_id]
                detections.append({
                    'class': cls_id,
                    'label': label,
                    'conf': float(box.conf[0]),
                    'bbox': box.xyxy[0].tolist() # [x1, y1, x2, y2]
                })
        
        return detections
