# 🎵 Music-computer-vision

**Music-computer-vision** is a Python-based project that lets you control music playback using hand gestures. It uses your webcam and computer vision to detect hand movements and trigger keyboard shortcuts — enabling a **touchless** and intuitive music experience.

## ✋ What it does

This app recognizes your hand gestures and maps them to music control actions like:

- ✊ Fist → **Pause**
- ✋ Open palm → **Play**
- 👉 Pointing index → **Next track**
- ✌️ Two fingers → **Previous track**

You can control your favorite media player (e.g. Spotify, YouTube) hands-free!

## 🧠 Tech Stack

- `OpenCV` – for capturing and processing webcam video
- `MediaPipe` – for real-time hand tracking
- `pyautogui` / `keyboard` – for sending keyboard commands to the OS
- `Python` – core programming language

## 🎯 Use Cases

- Hands-free control while working out or cooking
- For people with limited mobility or motor disabilities
- Fun gesture-based interaction with music

## 🚀 How to Run

```bash
git clone https://github.com/mausor11/Music-computer-vision.git
cd Music-computer-vision
pip install -r requirements.txt
python main.py
```

Make sure your webcam is enabled and the media player is open.
