import cv2
import mediapipe as mp
import numpy as np
import os
import sys
from mediapipe.tasks.python import vision

class Silencer:
    """Context manager to silence stdout/stderr at the OS level."""
    def __enter__(self):
        self.null_fds = [os.open(os.devnull, os.O_RDWR) for x in range(2)]
        self.save_fds = [os.dup(1), os.dup(2)]
        os.dup2(self.null_fds[0], 1)
        os.dup2(self.null_fds[1], 2)

    def __exit__(self, exc_type, exc_val, exc_tb):
        os.dup2(self.save_fds[0], 1)
        os.dup2(self.save_fds[1], 2)
        for fd in self.null_fds + self.save_fds:
            os.close(fd)

class PoseProcessor:
    def __init__(self):
        model_path = os.path.join('assets', 'pose_landmarker.task')
        
        with Silencer():
            base_options = mp.tasks.BaseOptions(model_asset_path=model_path)
            options = vision.PoseLandmarkerOptions(
                base_options=base_options,
                running_mode=vision.RunningMode.IMAGE
            )
            self.detector = vision.PoseLandmarker.create_from_options(options)
        
        self.LEFT_SHOULDER = 11
        self.RIGHT_SHOULDER = 12
        self.NOSE = 0

    def process(self, frame):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        
        with Silencer():
            result = self.detector.detect(mp_image)
        
        if not result.pose_landmarks:
            return None
        
        landmarks = result.pose_landmarks[0]
        h, w, _ = frame.shape
        points = np.array([[l.x * w, l.y * h] for l in landmarks])
        
        return {
            'landmarks': points,
            'metrics': self.calculate_posture(points)
        }

    def calculate_posture(self, points):
        left_shoulder = points[self.LEFT_SHOULDER]
        right_shoulder = points[self.RIGHT_SHOULDER]
        
        dy = abs(left_shoulder[1] - right_shoulder[1])
        dx = abs(left_shoulder[0] - right_shoulder[0])
        tilt_angle = np.degrees(np.arctan2(dy, dx))
        
        nose = points[self.NOSE]
        shoulder_midpoint_y = (left_shoulder[1] + right_shoulder[1]) / 2
        lean = shoulder_midpoint_y - nose[1]
        
        return {'tilt_angle': tilt_angle, 'lean': lean}
