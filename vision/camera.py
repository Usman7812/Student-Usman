import cv2
import threading
import time
from PyQt6.QtCore import QThread, pyqtSignal
from config import CAMERA_INDEX, TARGET_FPS, FRAME_WIDTH, FRAME_HEIGHT

class CameraThread(QThread):
    frame_ready = pyqtSignal(object)

    def __init__(self):
        super().__init__()
        self.running = False
        self.cap = None

    def run(self):
        self.cap = cv2.VideoCapture(CAMERA_INDEX)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
        self.running = True
        
        frame_delay = 1.0 / TARGET_FPS
        
        while self.running:
            ret, frame = self.cap.read()
            if ret:
                # Flip for mirror effect
                frame = cv2.flip(frame, 1)
                self.frame_ready.emit(frame)
            
            time.sleep(frame_delay)
            
        self.cap.release()

    def stop(self):
        self.running = False
        self.wait()
