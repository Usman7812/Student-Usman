import sys
import os
import traceback

print(f"Python version: {sys.version}")
print(f"Current working directory: {os.getcwd()}")

try:
    import torch
    print(f"Successfully imported torch. Version: {torch.__version__}")
except Exception as e:
    print("\n--- torch import failed ---")
    traceback.print_exc()

try:
    import torchvision
    print(f"Successfully imported torchvision. Version: {torchvision.__version__}")
except Exception as e:
    print("\n--- torchvision import failed ---")
    traceback.print_exc()

try:
    print("Attempting to import YOLO from ultralytics...")
    from ultralytics import YOLO
    print("Successfully imported YOLO.")
    
    # Try to initialize a model
    print("Attempting to initialize YOLOv8n model...")
    model = YOLO('yolov8n.pt')
    print("Successfully initialized YOLO model.")
    
except ImportError as e:
    print("\n--- YOLO import failed (ImportError) ---")
    traceback.print_exc()
except OSError as e:
    print("\n--- YOLO import failed (OSError/DLL failure) ---")
    traceback.print_exc()
except Exception as e:
    print("\n--- YOLO initialization failed (Unexpected Error) ---")
    traceback.print_exc()
