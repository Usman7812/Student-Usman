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

class FaceProcessor:
    def __init__(self):
        model_path = os.path.join('assets', 'face_landmarker.task')
        
        with Silencer():
            base_options = mp.tasks.BaseOptions(model_asset_path=model_path)
            options = vision.FaceLandmarkerOptions(
                base_options=base_options,
                running_mode=vision.RunningMode.IMAGE,
                output_face_blendshapes=True,
                num_faces=1
            )
            self.detector = vision.FaceLandmarker.create_from_options(options)
        
        # Mapping standard indices
        self.LEFT_EYE = [362, 385, 387, 263, 373, 380]
        self.RIGHT_EYE = [33, 160, 158, 133, 153, 144]
        self.MOUTH_TOP = 13
        self.MOUTH_BOTTOM = 14
        self.MOUTH_LEFT = 78
        self.MOUTH_RIGHT = 308

    def process(self, frame):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        
        with Silencer():
            result = self.detector.detect(mp_image)
        
        if not result.face_landmarks:
            return None
        
        landmarks = result.face_landmarks[0]
        blendshapes = result.face_blendshapes[0] if result.face_blendshapes else []
        
        h, w, _ = frame.shape
        points = np.array([[l.x * w, l.y * h] for l in landmarks])
        
        # Convert blendshapes to dictionary
        blendshape_dict = {b.category_name: b.score for b in blendshapes}
        
        return {
            'landmarks': points,
            'blendshapes': blendshape_dict,
            'fatigue_metrics': self.calculate_fatigue(points),
            'head_pose': self.estimate_head_pose(points, h, w)
        }

    def calculate_fatigue(self, points):
        def get_ear(eye_points):
            p1, p2, p3, p4, p5, p6 = eye_points
            dist1 = np.linalg.norm(p2 - p6)
            dist2 = np.linalg.norm(p3 - p5)
            dist3 = np.linalg.norm(p1 - p4)
            return (dist1 + dist2) / (2.0 * dist3)

        left_ear = get_ear(points[self.LEFT_EYE])
        right_ear = get_ear(points[self.RIGHT_EYE])
        avg_ear = (left_ear + right_ear) / 2.0
        
        mar = np.linalg.norm(points[self.MOUTH_TOP] - points[self.MOUTH_BOTTOM]) / \
              np.linalg.norm(points[self.MOUTH_LEFT] - points[self.MOUTH_RIGHT])
        
        return {'ear': avg_ear, 'mar': mar}

    def estimate_head_pose(self, points, h, w):
        nose = points[1]
        left_eye = points[33]
        right_eye = points[263]
        
        face_center_x = (left_eye[0] + right_eye[0]) / 2
        yaw = (nose[0] - face_center_x) / (right_eye[0] - left_eye[0]) * 90
        
        eye_center_y = (left_eye[1] + right_eye[1]) / 2
        pitch = (nose[1] - eye_center_y) / (right_eye[1] - left_eye[1]) * 90
        
        # AR Projection Points (3D Axes)
        # We project lines from the nose based on pitch/yaw
        scale = 50
        nose_p = (int(nose[0]), int(nose[1]))
        
        # Simple orthographic-like projection for visualization
        x_axis = (int(nose[0] + scale * np.cos(np.radians(yaw))), int(nose[1]))
        y_axis = (int(nose[0]), int(nose[1] + scale * np.sin(np.radians(pitch))))
        z_axis = (int(nose[0] + scale * np.sin(np.radians(yaw))), int(nose[1] - scale * np.cos(np.radians(pitch))))
        
        return {
            'yaw': yaw, 
            'pitch': pitch,
            'projection_points': {
                'nose': nose_p,
                'x': x_axis,
                'y': y_axis,
                'z': z_axis
            }
        }
