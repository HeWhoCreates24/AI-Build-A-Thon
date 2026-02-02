High-level architecture (local-first)
PC Boot
  ↓
Screenshot Service (interval-based)
  ↓
OCR (local)
  ↓
Text Preprocessing
  ↓
Local ML Inference (sentiment / distress)
  ↓
Risk Aggregator (time window + threshold)
  ↓
Alert Engine (admin + evidence)


Everything stays offline / on-device unless an alert triggers.

Recommended Tech Stack (battle-tested + hackathon-friendly)
1️⃣ OS-level Screenshot Capture

Options

Python

mss (fast, cross-platform)

pyautogui (simple, slower)

C++ (if you want speed points)

Win32 API (Windows labs)

Electron / Node

desktopCapturer (if building a UI-heavy app)

👉 Best choice for hackathon:
Python + mss

2️⃣ OCR (Offline, Local)

Top choices

Tesseract OCR

Open-source

Supports multiple languages

Works fully offline

EasyOCR

Better with messy fonts

Slightly heavier

👉 Recommended

Tesseract + pytesseract


Preprocessing helps a LOT:

Grayscale

Thresholding

Resize text-heavy regions

Libraries:

opencv-python

Pillow

3️⃣ Text Cleaning & NLP Pipeline

Python stack

spaCy (fast tokenization)

regex

langdetect (optional)

Pipeline:

OCR text
 → lowercase
 → remove noise
 → sentence chunking
 → sliding window

4️⃣ Local ML Model (Sentiment / Distress Detection)

⚠️ Important:
Generic sentiment ≠ depression detection.
You want psychological distress / crisis language detection.

Model Options (Offline)
🥇 Best Hackathon Choice

DistilBERT / MiniLM (fine-tuned)

Runs on CPU

Lightweight

Accurate

Pretrained bases:

distilbert-base-uncased

all-MiniLM-L6-v2

Fine-tune on:

Depression / mental health datasets:

CLPsych

Reddit mental health datasets

Kaggle mental health text

Libraries:

transformers
torch
onnxruntime (for speed)


👉 Convert model to ONNX for fast local inference.

5️⃣ Risk Scoring Logic (This is crucial)

Do NOT alert on a single sentence.

Use:

Sliding time window (e.g., last 15–30 min)

Weighted score

Keyword boost (self-harm phrases increase weight)

Example:

risk_score =
  (avg_model_score × 0.7)
+ (keyword_intensity × 0.2)
+ (frequency × 0.1)


Trigger only if:

Sustained risk over time

Multiple signals align

This wins you credibility with judges.

6️⃣ Webcam Capture (Only on Trigger)

opencv-python

Capture single frame, not video

Blur background (privacy win)

7️⃣ Alert System (Local Network)

Options:

Local server:

FastAPI

Flask

Notifications:

Email via SMTP

Admin dashboard (web UI)

Local system alert

Alert payload:

- Timestamp
- Risk score
- Screenshot samples
- Webcam snapshot
- Machine ID

8️⃣ Admin Dashboard (Optional but 🔥)

Frontend

React / Next.js

Or simple HTML + Tailwind

Backend

FastAPI

SQLite

Full Stack Summary (TL;DR)

Core

Python

OpenCV

Tesseract OCR

HuggingFace Transformers

PyTorch + ONNX Runtime

System

MSS (screenshots)

OpenCV (webcam)

FastAPI (alerts)

Optional UI

React + FastAPI

Ethics & Safety (Judges WILL ask)

Be ready with these bullets:

Explicit user consent

Runs entirely offline

No continuous webcam recording

Alerts only on sustained risk

Tool supports human intervention, not diagnosis

Phrase it as:

“Early warning system to assist counselors, not diagnose students.”