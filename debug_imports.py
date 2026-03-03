import sys
import os
import traceback

print(f"Python version: {sys.version}")

try:
    print("Step 1: Importing Mediapipe...")
    import mediapipe as mp
    print("Successfully imported Mediapipe.")
    
    print("Step 2: Attempting to import YOLO from ultralytics...")
    from ultralytics import YOLO
    print("Successfully imported YOLO after Mediapipe.")
    
except Exception as e:
    print("\n--- Conflict Detected ---")
    traceback.print_exc()

try:
    print("\nStep 3: Attempting to initialize YOLO model...")
    from ultralytics import YOLO
    model = YOLO('yolov8n.pt')
    print("Successfully initialized YOLO model.")
except Exception as e:
    print("\n--- YOLO initialization failed ---")
    traceback.print_exc()
