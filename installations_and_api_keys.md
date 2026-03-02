# Installations and API Keys Guide — StudySense

Follow these steps to set up the environment and obtain the necessary credentials for the StudySense AI Smart Study Companion.

## 1. Prerequisites
- **Python 3.10+**: Ensure you have Python installed. Use `python --version` to check.
- **Hardware**: A working webcam is required for the vision pipeline.

## 2. Environment Setup
It is highly recommended to use a virtual environment to manage dependencies:

```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment (Windows)
.\venv\Scripts\activate

# Activate virtual environment (Mac/Linux)
source venv/bin/activate
```

## 3. Installation
Install the required libraries using the provided `requirements.txt`:

```powershell
pip install -r requirements.txt
```

### Key Libraries Included:
- **opencv-python**: Core webcam and image processing.
- **mediapipe**: Advanced face and pose landmark detection.
- **deepface**: Real-time emotion recognition.
- **ultralytics**: YOLOv8 for object detection (phones).
- **pyqt6**: Modern desktop UI framework.
- **anthropic**: Integration with Claude AI for coaching.
- **sqlalchemy**: SQLite database ORM.

## 4. API Keys
StudySense uses the **Anthropic Claude API** for intelligent coaching messages.

> [!NOTE]
> **Integration Status**: Your API key has been successfully integrated into a local `.env` file. You do not need to set environment variables manually.

### Security:
- Your key is stored in `d:\PROJECT\.env`.
- Never share this key or commit it to a public repository.

## 5. First Run
Once the dependencies are installed and the API key is set, run the application:

```powershell
python main.py
```

> [!IMPORTANT]
> On the first run, the application may download several AI models (YOLOv8, MediaPipe, DeepFace). This might take a few minutes depending on your internet speed.
