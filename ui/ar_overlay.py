import cv2
import numpy as np

class ARRenderer:
    @staticmethod
    def draw_debug(frame, results):
        overlay = frame.copy()
        
        # 1. Draw Face Landmarks & Head Pose
        if 'face_data' in results and results['face_data']:
            landmarks = results['face_data']['landmarks']
            # Draw landmarks as subtle dots
            for pt in landmarks:
                cv2.circle(frame, (int(pt[0]), int(pt[1])), 1, (0, 255, 255), -1)
            
            # Draw 3D Pose Axes
            pose = results['face_data']['head_pose']
            if 'projection_points' in pose:
                pts = pose['projection_points']
                cv2.line(frame, pts['nose'], pts['x'], (0, 0, 255), 2) # X - Red
                cv2.line(frame, pts['nose'], pts['y'], (0, 255, 0), 2) # Y - Green
                cv2.line(frame, pts['nose'], pts['z'], (255, 0, 0), 2) # Z - Blue
        
        # 2. Draw YOLO Detections (Bounding Boxes)
        if 'phone_detections' in results:
            for det in results['phone_detections']:
                x1, y1, x2, y2 = map(int, det['bbox'])
                cls = det['class']
                conf = det['conf']
                
                # Color based on class
                color = (0, 165, 255) # Orange for Phone
                label = f"PHONE {conf:.2f}"
                if cls == 73: # Book
                    color = (0, 255, 0) # Green for Book
                    label = "BOOK (STUDY)"
                elif cls == 63: # Laptop
                    color = (255, 255, 0) # Cyan for Laptop
                    label = "LAPTOP"
                
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                cv2.putText(frame, label, (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        return frame
