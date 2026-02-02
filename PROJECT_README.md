# Crisis Detection System - V1 MVP

A local-first crisis risk detection system for university computer labs. Runs entirely offline with no cloud dependencies.

## 🎯 Purpose

Early warning system to assist counselors in identifying students who may be experiencing psychological distress. **This is NOT a diagnostic tool** but a support mechanism for human intervention.

## ⚙️ How It Works

```
PC Boot → Screenshot Capture (30s intervals) → OCR Text Extraction 
→ NLP Distress Scoring → Risk Aggregation (15min window) 
→ Threshold Check → [Alert + Webcam Capture] → Admin Notification
```

### Key Principles

- **Local-first**: Everything runs offline on the lab PC
- **Privacy-aware**: No continuous recording, minimal data retention
- **Sustained signals**: Alerts only on consistent distress patterns, not single sentences
- **Human-in-loop**: Tool assists counselors, does not replace them
- **Explicit consent**: Designed for environments with clear user agreement

## 📁 Project Structure

```
AI-Build-A-Thon/
├── crisis_detection/
│   ├── main.py                      # Main entry point
│   ├── core/                        # Core system modules
│   │   ├── screenshot_service.py    # Desktop screenshot capture
│   │   ├── ocr_pipeline.py          # Text extraction (Tesseract)
│   │   ├── nlp_model.py             # Distress scoring (ML/rules)
│   │   ├── risk_engine.py           # Time-windowed risk aggregation
│   │   └── webcam_capture.py        # On-demand webcam capture
│   ├── alerts/                      # Alert management
│   │   └── alert_manager.py         # Alert generation & notification
│   ├── utils/                       # Utilities
│   │   ├── config_loader.py         # Configuration management
│   │   └── logger.py                # Logging setup
│   ├── config/                      # Configuration files
│   │   └── config.yaml              # System configuration
│   ├── models/                      # ML models (fine-tuned)
│   │   └── distress_model/          # Trained model files
│   ├── data/                        # Runtime data
│   │   ├── screenshots/             # Captured screenshots
│   │   ├── webcam_captures/         # Webcam images
│   │   ├── logs/                    # System logs
│   │   └── evidence/                # Alert evidence bundles
│   └── dashboard/                   # Optional admin UI
├── tests/                           # Test files
├── requirements.txt                 # Python dependencies
├── README.md                        # This file
└── HIGH_ARCHITECTURE.md             # Architecture documentation
```

## 🚀 Quick Start

### 1. Prerequisites

- **Python 3.8+**
- **Tesseract OCR** installed on system
  - Linux: `sudo apt install tesseract-ocr`
  - Windows: Download from [GitHub](https://github.com/UB-Mannheim/tesseract/wiki)
- **Webcam** (optional for demo)

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure System

Edit `crisis_detection/config/config.yaml`:

```yaml
screenshot:
  capture_interval_seconds: 30    # Adjust capture frequency
  
risk:
  alert_threshold: 0.65            # Risk threshold (0-1)
  time_window_minutes: 15          # Time window for aggregation
  
alerts:
  notification_methods:
    - log
    - file
  admin_email: admin@university.edu  # Optional
```

### 4. Run System

```bash
python crisis_detection/main.py
```

Or with custom config:

```bash
python crisis_detection/main.py --config path/to/config.yaml
```

## 🧠 ML Model

### Option 1: Rule-Based (Default Fallback)

Uses keyword matching with severity weighting. Works out-of-the-box.

### Option 2: ML-Based (Recommended)

Fine-tune a lightweight transformer on mental health datasets:

**Datasets**:
- CLPsych (Reddit mental health)
- Kaggle depression detection
- Crisis text line data

**Model**:
- Base: `distilbert-base-uncased` or `all-MiniLM-L6-v2`
- Fine-tune on binary classification: distress / no-distress
- Export to ONNX for fast CPU inference

Place model in `crisis_detection/models/distress_model/`

## 🎓 Hackathon Tips

### Demo Workflow

1. **Start system** → Shows initialization
2. **Open browser** with test text (mental health forums)
3. **Wait 30-60 seconds** → System captures and processes
4. **Show risk dashboard** → Rising scores in time window
5. **Trigger alert** → Webcam capture + evidence bundle
6. **Show admin notification** → Log/email output

### Judging Points

✅ **Technical**: Modular architecture, clean code, local ML inference  
✅ **Impact**: Clear use case, solves real problem  
✅ **Ethics**: Privacy-aware, consent-based, human-in-loop  
✅ **Demo**: Working end-to-end, shows sustained risk logic

### If ML Model Fails

Rule-based fallback is built-in. Still demonstrates:
- Full system integration
- Risk aggregation logic
- Alert pipeline

## 🔒 Ethics & Safety

### What This System IS

- ✅ Early warning tool for trained counselors
- ✅ Supplementary data for human decision-making
- ✅ Privacy-respecting (local-only, minimal retention)

### What This System IS NOT

- ❌ Medical diagnosis device
- ❌ Autonomous decision-maker
- ❌ Surveillance system
- ❌ Replacement for mental health professionals

### Key Safeguards

1. **Explicit consent**: Users must agree to monitoring
2. **Offline-first**: No data leaves the device without alert
3. **Sustained signals**: Multiple data points required for alert
4. **Human review**: All alerts reviewed by trained staff
5. **Data minimization**: Rolling buffers, automatic cleanup

## 📊 Configuration Tuning

### For Demonstrations

```yaml
screenshot:
  capture_interval_seconds: 10    # Faster for demo
risk:
  time_window_minutes: 5          # Shorter window
  min_samples: 3                  # Fewer samples
  alert_threshold: 0.60           # Lower threshold
```

### For Production

```yaml
screenshot:
  capture_interval_seconds: 30-60
risk:
  time_window_minutes: 15-30
  min_samples: 8-10
  alert_threshold: 0.70-0.80
  alert_cooldown_minutes: 60-120
```

## 🧪 Testing

Run tests:

```bash
pytest tests/
```

Test individual components:

```bash
# Test screenshot
python crisis_detection/core/screenshot_service.py

# Test OCR
python crisis_detection/core/ocr_pipeline.py

# Test NLP
python crisis_detection/core/nlp_model.py
```

## 📝 License

For hackathon/educational use. Consult legal counsel before production deployment.

## 🤝 Contributing

This is a hackathon MVP. For production use:
- Conduct thorough security audit
- Obtain institutional ethics approval
- Implement comprehensive logging
- Add encryption for stored data
- Engage mental health professionals in design

---

**Remember**: This tool **assists** trained professionals. It does not diagnose or treat mental health conditions.
