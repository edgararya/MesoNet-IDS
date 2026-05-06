# MesoNet IDS: Deepfake Intrusion Detection System 🛡️

A real-time Deepfake Intrusion Detection System (IDS) designed for Blue Team operations. This project extends the original MesoNet architecture with a live scanning dashboard, target tracking, and real-time AI analysis of video feeds or screen regions.

## 🚀 Key Features

- **Live Screen Scanner**: Select any region on your screen to monitor for deepfake content in real-time.
- **IDS Dashboard**: A professional monitoring interface built with Tkinter, featuring status indicators and system logs.
- **Target Lock System**: Integrated snipping tool to "lock" onto specific video windows or web streams.
- **MesoNet AI Engine**: Powered by Meso4 and MesoInception-4 architectures for mesoscopic image analysis.
- **Hybrid Analysis**: Combines deep learning with **ELA (Error Level Analysis)** to detect compression inconsistencies.
- **Automated Face Tracking**: Real-time face detection using Haar Cascades and MediaPipe (available in variations).

## 🛠️ Requirements

- **Python**: 3.7+
- **Core Libraries**:
  - `tensorflow` or `keras` (for MesoNet models)
  - `opencv-python` (cv2)
  - `numpy`
  - `mss` (for high-performance screen capture)
  - `Pillow` (PIL)
- **Optional (for pipeline/live scanner)**:
  - `imageio`
  - `face_recognition`

## 📦 Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/YOUR_USERNAME/MesoNet-IDS.git
   cd MesoNet-IDS
   ```
2. Install dependencies:
   ```bash
   pip install tensorflow opencv-python numpy mss pillow
   ```

## 🖥️ Usage

### Live Scanner Dashboard
To start the real-time detection dashboard, run:
```bash
python live_scanner.py
```
1. Click **"🎯 LOCK TARGET REGION"**.
2. Select the area on your screen containing the face/video.
3. The AI will start analyzing the feed and display the **Confidence Score** and **Status (REAL/FAKE)**.

### Traditional Pipeline
To run detection on a video file:
```bash
python pipeline.py --video path/to/video.mp4
```

## 🧠 Pretrained Models
The project includes pretrained weights in the `weights` folder:
- `Meso4_DF.h5`: Optimized for Deepfake detection.
- `Meso4_F2F.h5`: Optimized for Face2Face detection.

## 📜 References & Acknowledgments
This project is an extension of the original MesoNet research:
- **Darius Afchar, Vincent Nozick, Junichi Yamagishi, Isao Echizen.** "MesoNet: a Compact Facial Video Forgery Detection Network". WIFS 2018.

---
*Developed for academic research and Blue Team cybersecurity simulations.*
