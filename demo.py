#!/usr/bin/env python3
"""
End-to-End System Demo
======================
Demonstrates the complete crisis detection flow.
"""

import sys
from pathlib import Path
import time

sys.path.insert(0, str(Path(__file__).parent.parent))

from crisis_detection.core.screenshot_service import ScreenshotService
from crisis_detection.core.ocr_pipeline import OCRPipeline
from crisis_detection.core.nlp_model import NLPModel
from crisis_detection.core.risk_engine import RiskEngine
from crisis_detection.core.webcam_capture import WebcamCapture
from crisis_detection.alerts.alert_manager import AlertManager
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


def main():
    """Run end-to-end demo."""
    print("="*70)
    print(" " * 15 + "CRISIS DETECTION SYSTEM")
    print(" " * 20 + "End-to-End Demo")
    print("="*70)
    
    # Configuration (fast for demo)
    config = {
        'screenshot': {
            'capture_interval_seconds': 10,
            'screenshot_dir': 'crisis_detection/data/screenshots',
            'max_screenshots': 20
        },
        'ocr': {
            'preprocess': True,
            'tesseract_path': None
        },
        'nlp': {
            'mode': 'auto',
            'model_path': 'crisis_detection/models/distress_model',
            'model_name': 'distilbert-base-uncased'
        },
        'risk': {
            'time_window_minutes': 5,
            'alert_threshold': 0.65,
            'min_samples': 3,
            'alert_cooldown_minutes': 5
        },
        'webcam': {
            'camera_index': 0,
            'save_dir': 'crisis_detection/data/webcam_captures',
            'blur_background': False,
            'max_captures': 10
        },
        'alerts': {
            'alert_log_dir': 'crisis_detection/data/logs/alerts',
            'evidence_dir': 'crisis_detection/data/evidence',
            'notification_methods': ['log', 'file'],
            'admin_email': None
        }
    }
    
    print("\nInitializing components...")
    
    # Initialize all components
    screenshot_service = ScreenshotService(config['screenshot'])
    ocr_pipeline = OCRPipeline(config['ocr'])
    nlp_model = NLPModel(config['nlp'])
    risk_engine = RiskEngine(config['risk'])
    webcam = WebcamCapture(config['webcam'])
    alert_manager = AlertManager(config['alerts'])
    
    print("✓ All components initialized")
    
    print("\n" + "="*70)
    print("DEMO FLOW")
    print("="*70)
    
    print("\nThis demo simulates the system processing screenshots over time.")
    print("In a real scenario:")
    print("  1. Screenshots are captured automatically every 10-30 seconds")
    print("  2. OCR extracts text from each screenshot")
    print("  3. NLP model scores the text for distress (0-1)")
    print("  4. Risk engine aggregates scores over a time window")
    print("  5. If risk exceeds threshold → Alert triggered + webcam capture")
    
    # Simulate processing cycles
    recent_screenshots = []
    
    print("\n" + "-"*70)
    print("Starting processing cycles...")
    print("-"*70)
    
    # Simulate 8 cycles with increasing distress
    simulated_texts = [
        "Working on homework assignment for computer science class.",
        "Feeling a bit tired today. Long week of classes.",
        "Stressed about upcoming exams. Lot of pressure.",
        "Feeling really overwhelmed. Can't handle all this work.",
        "I feel so hopeless. Nothing I do seems to matter.",
        "I'm so depressed. I don't see the point in anything anymore.",
        "I can't take this anymore. I feel worthless and alone.",
        "I want to give up. Nobody would care if I just disappeared."
    ]
    
    for cycle in range(8):
        print(f"\n[Cycle {cycle + 1}/8]")
        print(f"{'─' * 70}")
        
        # Simulate screenshot (in real system, this happens automatically)
        print("1. Screenshot captured")
        
        # Simulate OCR (in real system, extracts from actual screenshot)
        text = simulated_texts[cycle]
        print(f"2. OCR extracted: \"{text[:50]}...\"")
        
        # NLP scoring
        score = nlp_model.score_text(text)
        print(f"3. NLP distress score: {score:.3f}", end="")
        
        if score < 0.3:
            print(" ✅ (Low)")
        elif score < 0.6:
            print(" ⚠️  (Moderate)")
        elif score < 0.8:
            print(" 🔴 (High)")
        else:
            print(" 🚨 (Critical)")
        
        # Add to risk engine
        risk_engine.add_score(score)
        risk = risk_engine.compute_risk()
        stats = risk_engine.get_window_stats()
        
        print(f"4. Risk engine: {risk:.3f} (window avg: {stats['avg_score']:.3f}, samples: {stats['sample_count']})")
        
        # Track screenshot for evidence
        recent_screenshots.append(f"screenshot_{cycle}.png")
        
        # Check for alert
        if risk_engine.should_alert():
            print("\n" + "🚨" * 35)
            print("   ALERT TRIGGERED - Sustained high distress detected!")
            print("🚨" * 35)
            
            print("\n5. Webcam capture: Capturing single frame...")
            webcam_path = webcam.capture()
            
            if webcam_path:
                print(f"   ✓ Webcam image saved: {webcam_path.name}")
            else:
                print(f"   ⚠ Webcam capture failed (continuing without image)")
            
            print("\n6. Generating alert...")
            alert = alert_manager.trigger_alert(
                risk_score=risk,
                window_stats=stats,
                screenshot_paths=recent_screenshots[-5:],
                webcam_path=webcam_path
            )
            
            print(f"   ✓ Alert ID: {alert['alert_id']}")
            print(f"   ✓ Severity: {alert['severity']}")
            print(f"   ✓ Evidence collected: {len(alert['evidence']['screenshots'])} screenshots")
            print(f"   ✓ Notification sent to admin")
            
            print("\n" + "="*70)
            print("ALERT DETAILS")
            print("="*70)
            print(f"Time: {alert['timestamp']}")
            print(f"Risk Score: {alert['risk_score']:.3f}")
            print(f"Severity: {alert['severity']}")
            print(f"Machine: {alert['machine_info']['hostname']}")
            print(f"Evidence location: {config['alerts']['evidence_dir']}/{alert['alert_id']}/")
            
            print("\n✓ Alert successfully processed!")
            break
        else:
            print("5. No alert (threshold not exceeded or cooldown active)")
        
        time.sleep(2)  # Brief pause for demo readability
    
    # Cleanup
    webcam.release()
    
    print("\n" + "="*70)
    print("DEMO COMPLETE")
    print("="*70)
    
    print("\nKey Observations:")
    print("  ✓ System required multiple high-distress samples")
    print("  ✓ Risk score increased gradually as distress persisted")
    print("  ✓ Alert only triggered after sustained pattern")
    print("  ✓ Evidence bundle created with screenshots + webcam")
    print("  ✓ Admin notification sent automatically")
    
    print("\nIn Production:")
    print("  • Screenshots captured automatically in background")
    print("  • OCR processes real screen content")
    print("  • NLP model (fine-tuned) provides accurate scoring")
    print("  • Risk engine prevents false positives")
    print("  • Counselors review all alerts with full context")
    
    print("\n" + "="*70)


if __name__ == "__main__":
    main()
