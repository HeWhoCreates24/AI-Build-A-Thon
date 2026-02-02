# Crisis Detection System - Quick Reference

## 📁 Project Structure

```
AI-Build-A-Thon/
├── crisis_detection/              # Main application package
│   ├── main.py                   # Entry point - orchestrates all components
│   │
│   ├── core/                     # Core processing modules
│   │   ├── screenshot_service.py # Background screenshot capture (mss)
│   │   ├── ocr_pipeline.py       # Text extraction (Tesseract + OpenCV)
│   │   ├── nlp_model.py          # Distress scoring (ML + rules fallback)
│   │   ├── risk_engine.py        # Time-windowed risk aggregation
│   │   └── webcam_capture.py     # On-demand webcam capture
│   │
│   ├── alerts/                   # Alert management
│   │   └── alert_manager.py      # Alert generation, logging, notification
│   │
│   ├── utils/                    # Utilities
│   │   ├── config_loader.py      # YAML config loading with defaults
│   │   └── logger.py             # Centralized logging setup
│   │
│   ├── config/                   # Configuration files
│   │   └── config.yaml           # Main system configuration
│   │
│   ├── models/                   # ML models
│   │   └── README.md             # Model setup instructions
│   │
│   ├── data/                     # Runtime data (gitignored)
│   │   ├── screenshots/          # Captured screenshots
│   │   ├── webcam_captures/      # Webcam images
│   │   ├── logs/                 # System logs + alert JSONs
│   │   └── evidence/             # Per-alert evidence bundles
│   │
│   └── dashboard/                # Optional admin UI (future)
│
├── tests/                        # Test suite
│
├── requirements.txt              # Python dependencies
├── setup.py                      # Quick setup script
├── .gitignore                    # Git ignore rules
│
├── PROJECT_README.md             # User-facing documentation
├── ARCHITECTURE.md               # Detailed technical architecture
└── HIGH_ARCHITECTURE.md          # Original architecture notes
```

---

## 🔄 System Flow

```
1. CAPTURE   → Screenshot Service (every 30s)
2. EXTRACT   → OCR Pipeline (Tesseract)
3. SCORE     → NLP Model (0.0 - 1.0 distress score)
4. AGGREGATE → Risk Engine (15min window, weighted)
5. DECIDE    → Threshold check (>0.65 = alert)
6. ALERT     → Webcam + Evidence + Notification
```

---

## ⚙️ Key Configuration Points

### Demo Settings (Fast)
```yaml
screenshot:
  capture_interval_seconds: 10    # Faster captures
risk:
  time_window_minutes: 5          # Shorter window
  alert_threshold: 0.60           # Lower threshold
  min_samples: 3                  # Fewer samples needed
```

### Production Settings (Conservative)
```yaml
screenshot:
  capture_interval_seconds: 60    # Slower captures
risk:
  time_window_minutes: 20         # Longer window
  alert_threshold: 0.75           # Higher threshold
  min_samples: 10                 # More samples needed
```

---

## 🚀 Quick Start

```bash
# 1. Setup
python setup.py

# 2. Activate environment
source venv/bin/activate          # Linux/Mac
# or
venv\Scripts\activate             # Windows

# 3. Run system
python crisis_detection/main.py

# 4. With custom config
python crisis_detection/main.py --config path/to/config.yaml
```

---

## 🧩 Component Responsibilities

| Component | Purpose | Key Tech |
|-----------|---------|----------|
| **Screenshot Service** | Capture desktop at intervals | mss, threading |
| **OCR Pipeline** | Extract text from images | Tesseract, OpenCV |
| **NLP Model** | Score text for distress | Transformers / Keywords |
| **Risk Engine** | Aggregate scores over time | Time-series logic |
| **Webcam Capture** | On-demand image capture | OpenCV |
| **Alert Manager** | Generate & send alerts | JSON, SMTP (optional) |

---

## 📊 Data Flow Diagram

```
┌──────────────┐
│  Screenshot  │ (Every 30s)
└──────┬───────┘
       ↓
┌──────────────┐
│     OCR      │ (1-2 seconds)
└──────┬───────┘
       ↓
┌──────────────┐
│  NLP Scorer  │ (200-500ms)
└──────┬───────┘
       ↓ score (0-1)
┌──────────────┐
│ Risk Engine  │ (15min buffer)
└──────┬───────┘
       ↓
   Threshold?
       ↓ YES
┌──────────────┐
│   Webcam +   │
│    Alert     │
└──────────────┘
```

---

## 🎯 Scoring Logic

### NLP Model Output
- **0.0 - 0.3**: Low/no distress
- **0.3 - 0.6**: Moderate concern
- **0.6 - 0.8**: High distress
- **0.8 - 1.0**: Critical risk

### Risk Engine Aggregation
```python
# Weighted average (recent scores weighted higher)
base_risk = Σ(score × recency_weight) / Σ(recency_weight)

# Frequency boost (sustained high scores)
frequency_multiplier = 1 + (high_score_ratio × 0.3)

# Final risk
final_risk = base_risk × frequency_multiplier
```

### Alert Trigger
```python
if final_risk >= threshold:
    AND cooldown_elapsed:
    AND min_samples_met:
        → TRIGGER ALERT
```

---

## 🔒 Privacy & Ethics

### Design Principles
✅ Local-only processing (no cloud)  
✅ Sustained signals required (no single-sentence triggers)  
✅ On-demand webcam only (no continuous recording)  
✅ Rolling buffers (automatic cleanup)  
✅ Human-in-loop (counselor review)  

### Required for Production
- [ ] Explicit user consent
- [ ] Ethics board approval
- [ ] Data encryption
- [ ] Access controls
- [ ] Regular audits

---

## 📝 Example Alert Payload

```json
{
  "alert_id": "ALERT_20260202_143052_1",
  "timestamp": "2026-02-02T14:30:52",
  "risk_score": 0.87,
  "severity": "CRITICAL",
  "window_stats": {
    "sample_count": 12,
    "avg_score": 0.72,
    "max_score": 0.95
  },
  "evidence": {
    "screenshots": ["screenshot_1.png", ...],
    "webcam": "webcam.jpg"
  },
  "machine_info": {
    "hostname": "lab-pc-042",
    "platform": "Windows"
  }
}
```

---

## 🧪 Testing Individual Components

```bash
# Screenshot service
python crisis_detection/core/screenshot_service.py

# OCR pipeline
python crisis_detection/core/ocr_pipeline.py

# NLP model
python crisis_detection/core/nlp_model.py

# Risk engine
python crisis_detection/core/risk_engine.py

# Webcam
python crisis_detection/core/webcam_capture.py

# Alert manager
python crisis_detection/alerts/alert_manager.py
```

---

## 💡 Hackathon Demo Tips

### Setup (Before Judges Arrive)
1. Start system with demo config
2. Have browser ready with test content
3. Terminal showing live logs

### Presentation Flow (10 min)
1. **Problem** (1 min): Mental health crisis on campuses
2. **Solution** (2 min): Local-first early warning system
3. **Architecture** (2 min): Walk through components
4. **Live Demo** (4 min): Trigger alert, show evidence
5. **Ethics** (1 min): Privacy safeguards, human-in-loop

### Key Talking Points
- "Fully offline - no privacy concerns"
- "Sustained signals - no false alarms"
- "Assists counselors - doesn't replace them"
- "Production-ready architecture"

---

## 🐛 Troubleshooting

### Tesseract not found
```bash
# Linux
sudo apt install tesseract-ocr

# Mac
brew install tesseract

# Windows
# Download from: https://github.com/UB-Mannheim/tesseract/wiki
```

### ML model not loading
→ System will automatically fall back to rules-based scoring  
→ Check logs for details

### Webcam fails
→ Alert will still trigger (without webcam image)  
→ Check camera permissions

### No screenshots captured
→ Check screenshot_dir path in config  
→ Verify mss library installed

---

## 📚 Documentation Files

- **PROJECT_README.md**: User guide, quick start, demo instructions
- **ARCHITECTURE.md**: Detailed technical architecture, algorithms
- **HIGH_ARCHITECTURE.md**: Original design notes
- **QUICK_REFERENCE.md**: This file - fast lookup

---

## 🎓 For Judges

**What This System IS**:
- Early warning tool for counselors
- Privacy-first, local processing
- Sustained signal detection (not single sentences)
- Assistance for human decision-making

**What This System IS NOT**:
- Medical diagnosis device
- Autonomous decision maker
- Surveillance system
- Replacement for professionals

---

## ⏭️ Future Enhancements

- [ ] Real-time dashboard (FastAPI + React)
- [ ] ONNX model optimization
- [ ] Multi-language support
- [ ] Advanced privacy filters
- [ ] Mobile counselor app
- [ ] Integration with campus systems

---

**Version**: 1.0.0 (Hackathon MVP)  
**License**: Educational Use  
**Contact**: See PROJECT_README.md for details
