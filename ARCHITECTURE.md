# System Architecture - Crisis Detection System V1 MVP

## Overview

The Crisis Detection System is a **local-first**, **privacy-aware** early warning system designed for university computer labs. It monitors screen content for psychological distress indicators and alerts trained counselors when sustained risk patterns emerge.

## Core Design Principles

1. **Local-Only Processing**: No cloud APIs, no external dependencies
2. **Sustained Signals Only**: Multi-sample aggregation prevents false positives
3. **Privacy by Design**: Minimal data retention, on-demand webcam only
4. **Human-in-Loop**: Assists counselors, does not replace them
5. **Hackathon-Friendly**: Modular, documented, demo-ready

---

## System Architecture

### High-Level Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                         PC STARTUP                               │
└────────────────────────┬────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│  Screenshot Service (Background Thread)                          │
│  • Captures desktop every N seconds (default: 30s)              │
│  • Saves with timestamp                                          │
│  • Rolling buffer (deletes old screenshots)                      │
└────────────────────────┬────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│  OCR Pipeline                                                     │
│  • Load screenshot                                               │
│  • Preprocess (grayscale, threshold, denoise)                   │
│  • Extract text (Tesseract)                                      │
│  • Clean text (remove artifacts)                                │
└────────────────────────┬────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│  NLP Model                                                        │
│  • Tokenize text                                                 │
│  • Run distress scoring:                                         │
│    - ML Mode: DistilBERT/MiniLM (CPU inference)                 │
│    - Rules Mode: Keyword matching (fallback)                    │
│  • Output: Distress score (0.0 - 1.0)                           │
└────────────────────────┬────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│  Risk Engine                                                      │
│  • Maintain rolling time window (default: 15 min)               │
│  • Add new score to buffer                                       │
│  • Compute weighted aggregate:                                   │
│    - Recent scores weighted higher                              │
│    - Frequency multiplier (sustained distress)                  │
│  • Compare to threshold (default: 0.65)                         │
└────────────────────────┬────────────────────────────────────────┘
                         ↓
                    Alert Trigger?
                         ↓
                    ┌────┴────┐
                    │   YES   │
                    └────┬────┘
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│  Webcam Capture (On Alert Only)                                  │
│  • Initialize camera                                             │
│  • Capture single frame                                          │
│  • Optional: Apply privacy blur                                 │
│  • Save with timestamp                                           │
└────────────────────────┬────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│  Alert Manager                                                    │
│  • Generate alert ID and payload                                │
│  • Collect evidence:                                             │
│    - Copy recent screenshots (last 5)                           │
│    - Copy webcam image                                           │
│  • Save alert JSON log                                           │
│  • Send notifications:                                           │
│    - System logger                                               │
│    - Alert summary file                                          │
│    - Email (optional)                                            │
└─────────────────────────────────────────────────────────────────┘
```

---

## Component Architecture

### 1. Screenshot Service (`screenshot_service.py`)

**Purpose**: Continuously capture desktop screenshots at regular intervals.

**Key Features**:
- Cross-platform (mss library)
- Runs in background thread (non-blocking)
- Configurable capture interval
- Rolling buffer (auto-cleanup)
- Minimal memory footprint

**Configuration**:
```yaml
screenshot:
  capture_interval_seconds: 30
  screenshot_dir: data/screenshots
  max_screenshots: 100
```

**Thread Safety**: Uses daemon thread, graceful shutdown support.

---

### 2. OCR Pipeline (`ocr_pipeline.py`)

**Purpose**: Extract text from screenshots for NLP analysis.

**Key Features**:
- Tesseract OCR (fully offline)
- Preprocessing for accuracy:
  - Grayscale conversion
  - Adaptive thresholding
  - Denoising
- Text cleaning (remove artifacts)

**Optimization**:
- Screen text typically uses clean fonts
- Preprocessing significantly improves accuracy
- Fast processing (~1-2 seconds per screenshot)

**Configuration**:
```yaml
ocr:
  preprocess: true
  tesseract_path: null  # Auto-detect (Windows may need explicit path)
```

---

### 3. NLP Model (`nlp_model.py`)

**Purpose**: Score text for psychological distress indicators.

**Modes**:

#### ML Mode (Recommended)
- **Model**: DistilBERT or MiniLM
- **Fine-tuning**: Mental health datasets (CLPsych, Reddit)
- **Inference**: CPU-optimized (PyTorch or ONNX)
- **Output**: Probability (0-1) of distress

#### Rules Mode (Fallback)
- **Approach**: Keyword matching with severity weighting
- **Categories**:
  - High severity: "kill myself", "end my life", "suicide"
  - Medium: "hopeless", "worthless", "self harm"
  - Low: "depressed", "sad", "anxious"
- **Scoring**: Weighted sum, normalized to 0-1

**Configuration**:
```yaml
nlp:
  mode: auto  # 'ml', 'rules', or 'auto'
  model_path: models/distress_model
  model_name: distilbert-base-uncased
```

**Trade-offs**:
- ML: More accurate, requires training data
- Rules: Works immediately, less nuanced

---

### 4. Risk Engine (`risk_engine.py`)

**Purpose**: Aggregate distress scores over time and determine when to alert.

**Algorithm**:

1. **Rolling Time Window**
   - Maintain buffer of (timestamp, score) pairs
   - Filter to configurable window (default: 15 min)

2. **Temporal Weighting**
   - Recent scores weighted higher
   - Formula: `weight = recency^0.5` (exponential decay)

3. **Frequency Multiplier**
   - Count high scores (>0.5) in window
   - Boost risk if many high scores (sustained distress)
   - Formula: `final_risk = base_risk × (1 + frequency_ratio × 0.3)`

4. **Threshold Check**
   - Alert if risk ≥ threshold (default: 0.65)
   - Cooldown period prevents alert fatigue (default: 30 min)

**Key Principle**: **DO NOT alert on single sentence**. Require multiple samples over time.

**Configuration**:
```yaml
risk:
  time_window_minutes: 15
  alert_threshold: 0.65
  min_samples: 5
  alert_cooldown_minutes: 30
```

**Tuning**:
- Demo: Lower threshold (0.60), shorter window (5 min)
- Production: Higher threshold (0.75), longer window (20 min)

---

### 5. Webcam Capture (`webcam_capture.py`)

**Purpose**: Capture single webcam image when alert triggers.

**CRITICAL DESIGN**:
- **NO continuous recording**
- **NO video storage**
- **Single frame on alert only**

**Key Features**:
- OpenCV camera access
- Lazy initialization (camera only opened when needed)
- Optional privacy blur (background)
- Rolling buffer (auto-cleanup)

**Privacy Considerations**:
- Explicit consent required
- Blur option for background privacy
- Immediate cleanup of old captures

**Configuration**:
```yaml
webcam:
  camera_index: 0
  save_dir: data/webcam_captures
  blur_background: false
  max_captures: 50
```

---

### 6. Alert Manager (`alert_manager.py`)

**Purpose**: Generate, log, and notify about crisis alerts.

**Alert Payload Structure**:
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
    "screenshots": ["path1.png", "path2.png"],
    "webcam": "webcam.jpg"
  },
  "machine_info": {
    "hostname": "lab-pc-042",
    "platform": "Windows"
  },
  "status": "NEW"
}
```

**Notification Methods**:
1. **Log**: System logger (critical level)
2. **File**: Consolidated alert summary
3. **Email**: SMTP notification (optional)

**Evidence Collection**:
- Copies last 5 screenshots to evidence directory
- Copies webcam image
- Creates alert-specific folder for each alert

**Configuration**:
```yaml
alerts:
  alert_log_dir: data/logs/alerts
  evidence_dir: data/evidence
  notification_methods: [log, file]
  admin_email: null
```

---

## File System Layout

```
crisis_detection/
├── main.py                 # Orchestrator - coordinates all components
├── core/
│   ├── screenshot_service.py   # Background screenshot capture
│   ├── ocr_pipeline.py         # Text extraction
│   ├── nlp_model.py            # Distress scoring
│   ├── risk_engine.py          # Time-windowed aggregation
│   └── webcam_capture.py       # On-demand webcam
├── alerts/
│   └── alert_manager.py        # Alert generation & notification
├── utils/
│   ├── config_loader.py        # YAML config loading
│   └── logger.py               # Logging setup
├── config/
│   └── config.yaml             # Main configuration
├── models/
│   └── distress_model/         # Fine-tuned ML model (optional)
├── data/                       # Runtime data (gitignored)
│   ├── screenshots/            # Captured screenshots
│   ├── webcam_captures/        # Webcam images
│   ├── logs/                   # System logs
│   │   ├── system.log
│   │   ├── alerts/             # Alert JSON files
│   │   └── alert_summary.txt   # Consolidated alerts
│   └── evidence/               # Alert evidence bundles
│       └── ALERT_20260202_*/   # Per-alert folders
└── dashboard/                  # Optional admin UI (future)
```

---

## Configuration System

**Hierarchical Configuration**:
1. Default config (hardcoded)
2. YAML file (overrides defaults)
3. Command-line args (overrides YAML)

**Config Loading**:
```python
# Load with defaults
config = load_config('config/config.yaml')

# Merge: custom values override defaults
# Missing keys use defaults
```

**Environment-Specific Configs**:
- `config.demo.yaml`: Fast intervals, low thresholds
- `config.prod.yaml`: Conservative thresholds, longer windows

---

## Execution Flow

### Startup Sequence

1. **Load Configuration**
   - Read YAML file
   - Merge with defaults
   - Validate settings

2. **Initialize Components**
   - Screenshot service
   - OCR pipeline
   - NLP model (load weights)
   - Risk engine (empty buffer)
   - Webcam (lazy init)
   - Alert manager

3. **Start Services**
   - Screenshot service starts background thread
   - Main loop begins

### Main Processing Loop

```python
while running:
    1. Check for new screenshots
    2. If new:
        a. OCR: Extract text
        b. NLP: Score distress (0-1)
        c. Risk Engine: Add score to buffer
        d. Track screenshot for evidence
    3. Check if alert should trigger
    4. If alert:
        a. Webcam: Capture image
        b. Alert Manager: Generate alert + collect evidence
        c. Send notifications
    5. Sleep briefly (2-5 seconds)
```

### Shutdown Sequence

1. Stop screenshot service (join thread)
2. Release webcam
3. Flush logs
4. Exit gracefully

---

## Performance Characteristics

### Resource Usage (Estimated)

- **CPU**: ~5-10% (idle), ~30-40% (during processing)
- **RAM**: ~200-500 MB (ML model loaded)
- **Disk**: ~50-100 MB/hour (screenshots)
- **Network**: 0 (fully local)

### Timing (Typical)

- Screenshot capture: ~100-200ms
- OCR processing: ~1-2 seconds
- NLP inference:
  - ML mode: ~200-500ms (CPU)
  - Rules mode: ~10-50ms
- Risk aggregation: ~10-20ms
- Alert generation: ~500ms (includes webcam)

**Total latency**: ~2-4 seconds per screenshot (acceptable for 30s intervals)

---

## Scalability Considerations

### Single Machine

- Handles 1 user comfortably
- 30-second intervals sustainable 24/7
- Rolling buffers prevent disk overflow

### Lab Environment (Multiple PCs)

**Option 1: Standalone**
- Each PC runs independent instance
- Admin checks local logs/alerts

**Option 2: Centralized (Future)**
- Local agents send alerts to central server
- Central dashboard aggregates alerts
- Requires network architecture changes

---

## Security & Privacy

### Data Flow Security

1. **Capture**: Local disk only
2. **Processing**: In-memory, local CPU
3. **Storage**: Local filesystem (configurable retention)
4. **Alerts**: Local log files (no transmission unless configured)

### Privacy Features

- **Minimal Retention**: Rolling buffers, automatic cleanup
- **On-Demand Webcam**: No continuous recording
- **Background Blur**: Optional privacy filter
- **No Cloud**: Zero external API calls

### Access Control

- File permissions: Restrict access to data directories
- Log encryption: Optional (future enhancement)
- Admin authentication: Required for dashboard (if implemented)

---

## Error Handling & Resilience

### Failure Modes

1. **OCR Failure**: Skip screenshot, log error, continue
2. **NLP Model Error**: Fallback to rules mode
3. **Webcam Failure**: Log error, alert without webcam image
4. **Disk Full**: Aggressive cleanup, stop capture if critical

### Graceful Degradation

- ML model unavailable → Rules-based scoring
- Webcam unavailable → Alert without webcam
- Config file missing → Use hardcoded defaults

### Logging Strategy

- **DEBUG**: Detailed processing steps
- **INFO**: Major state changes
- **WARNING**: Recoverable errors
- **ERROR**: Component failures
- **CRITICAL**: Alert triggers

---

## Testing Strategy

### Unit Tests

- `test_screenshot_service.py`: Mock mss, test capture loop
- `test_ocr_pipeline.py`: Test with sample images
- `test_nlp_model.py`: Test both ML and rules modes
- `test_risk_engine.py`: Test windowing and aggregation
- `test_alert_manager.py`: Test alert generation

### Integration Tests

- End-to-end flow with mock components
- Test alert triggering with simulated high-risk text
- Test evidence collection

### Manual Testing

- Run with demo config (fast intervals)
- Display browser with mental health content
- Verify alert triggers correctly

---

## Demo Strategy for Hackathon

### Setup (5 minutes)

1. Install dependencies: `pip install -r requirements.txt`
2. Configure for demo: Short intervals, low threshold
3. Start system: `python crisis_detection/main.py`

### Demonstration (10 minutes)

1. **Show Architecture** (2 min)
   - Walk through components
   - Explain local-first design

2. **Live Demo** (5 min)
   - System running in background
   - Open browser with distress-related text
   - Show logs: Scores rising
   - Alert triggers
   - Show evidence bundle (screenshots + webcam)

3. **Ethics Discussion** (2 min)
   - Privacy safeguards
   - Human-in-loop design
   - Consent framework

4. **Q&A** (1 min)
   - Handle technical questions
   - Discuss production considerations

### Talking Points

✅ "Fully offline - no cloud dependencies"  
✅ "Sustained signals only - prevents false alarms"  
✅ "Privacy-first: on-demand webcam, rolling buffers"  
✅ "Assists counselors, doesn't replace them"  
✅ "Modular architecture - easy to extend"

---

## Future Enhancements (Post-Hackathon)

### Technical

- [ ] ONNX model export for faster inference
- [ ] Multi-language support (OCR + NLP)
- [ ] Advanced privacy filters (face detection + selective blur)
- [ ] Encrypted evidence storage
- [ ] Real-time dashboard (FastAPI + React)

### Features

- [ ] Sentiment trend visualization
- [ ] Alert escalation levels
- [ ] Integration with campus counseling systems
- [ ] Mobile app for counselors
- [ ] Anonymous reporting mechanism

### Research

- [ ] Fine-tune models on larger datasets
- [ ] A/B testing of threshold values
- [ ] Longitudinal studies on effectiveness
- [ ] False positive/negative analysis

---

## Ethical Guidelines for Deployment

### Prerequisites for Production Use

1. **Institutional Ethics Approval**
   - IRB review
   - Student consent process
   - Data retention policies

2. **Technical Safeguards**
   - End-to-end encryption
   - Access control lists
   - Audit logging
   - Regular security audits

3. **Human Oversight**
   - Trained counselor review of all alerts
   - Regular system calibration
   - Feedback loop for false positives

4. **Transparency**
   - Clear notification to users
   - Opt-out mechanism
   - Public documentation of algorithms

### Red Lines (DO NOT CROSS)

❌ Deploying without explicit user consent  
❌ Claiming diagnostic capability  
❌ Using for punitive actions  
❌ Sharing data with third parties  
❌ Continuous webcam recording  

---

## Conclusion

This architecture balances **technical feasibility** (hackathon-ready), **ethical responsibility** (privacy-first), and **real-world impact** (assists counselors).

The system is designed to **assist, not replace** human judgment. It provides **early warning signals** to help trained professionals identify students who may need support.

**Key Success Factors**:
1. Local-only processing (privacy)
2. Sustained signal logic (accuracy)
3. Modular design (maintainability)
4. Clear ethical boundaries (responsibility)

**For Judges**: This is a **tool for counselors**, not a surveillance system. It prioritizes privacy, requires sustained signals, and keeps humans in the decision loop.
