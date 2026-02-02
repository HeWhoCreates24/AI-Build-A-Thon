"""
Main Application Entry Point
=============================
Orchestrates all system components.

This is the main entry point for the Crisis Detection System.
Starts all services and coordinates their interactions.

Usage:
    python main.py [--config config.yaml]
"""

import logging
import sys
from pathlib import Path
import time
import signal
import argparse

# Ensure project root is on sys.path for direct execution
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Import core modules
from crisis_detection.core.screenshot_service import ScreenshotService
from crisis_detection.core.ocr_pipeline import OCRPipeline
from crisis_detection.core.nlp_model import NLPModel
from crisis_detection.core.risk_engine import RiskEngine
from crisis_detection.core.webcam_capture import WebcamCapture
from crisis_detection.alerts.alert_manager import AlertManager
from crisis_detection.utils.config_loader import load_config
from crisis_detection.utils.logger import setup_logging


class CrisisDetectionSystem:
    """
    Main system orchestrator.
    
    Coordinates:
    - Screenshot capture service
    - OCR processing
    - NLP distress scoring
    - Risk aggregation
    - Alert triggering
    """
    
    def __init__(self, config_path='crisis_detection/config/config.yaml'):
        """
        Initialize all system components.
        
        Args:
            config_path: Path to configuration file
        """
        # Load configuration
        self.config = load_config(config_path)
        
        # Setup logging
        setup_logging(self.config.get('logging', {}))
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.logger.info("Initializing Crisis Detection System...")
        
        self.screenshot_service = ScreenshotService(self.config['screenshot'])
        self.ocr_pipeline = OCRPipeline(self.config['ocr'])
        self.nlp_model = NLPModel(self.config['nlp'])
        self.risk_engine = RiskEngine(self.config['risk'])
        self.webcam = WebcamCapture(self.config['webcam'])
        self.alert_manager = AlertManager(self.config['alerts'])
        
        # Track recent screenshots for evidence
        self.recent_screenshots = []
        
        # System state
        self.running = False
        
        self.logger.info("System initialized successfully")
    
    def start(self):
        """Start the crisis detection system."""
        self.logger.info("=" * 60)
        self.logger.info("STARTING CRISIS DETECTION SYSTEM")
        self.logger.info("=" * 60)
        
        # Start screenshot service
        if not self.screenshot_service.start():
            self.logger.error("Screenshot service failed to start. Exiting main loop.")
            self.logger.error("Tip: Run demo.py for headless environments or start with a display.")
            self.stop()
            return
        
        self.running = True
        
        # Main processing loop
        self._main_loop()
    
    def _main_loop(self):
        """
        Main processing loop.
        
        Flow:
        1. Check for new screenshots
        2. Process with OCR
        3. Score with NLP
        4. Update risk engine
        5. Check for alerts
        """
        last_processed = None
        
        while self.running:
            try:
                # Get latest screenshot
                screenshot_dir = Path(self.config['screenshot']['screenshot_dir'])
                screenshots = sorted(screenshot_dir.glob("screenshot_*.png"))
                
                if not screenshots:
                    time.sleep(5)
                    continue
                
                latest_screenshot = screenshots[-1]
                
                # Skip if already processed
                if latest_screenshot == last_processed:
                    time.sleep(5)
                    continue
                
                self.logger.info(f"Processing: {latest_screenshot.name}")
                
                # OCR: Extract text
                text = self.ocr_pipeline.extract_text(latest_screenshot)
                
                if not text or len(text.strip()) < 10:
                    self.logger.debug("No significant text extracted")
                    last_processed = latest_screenshot
                    continue
                
                # NLP: Score distress
                distress_score = self.nlp_model.score_text(text)
                self.logger.info(f"Distress score: {distress_score:.3f}")
                
                # Risk Engine: Add score
                self.risk_engine.add_score(distress_score)
                
                # Track screenshot for evidence
                self.recent_screenshots.append(latest_screenshot)
                if len(self.recent_screenshots) > 10:
                    self.recent_screenshots.pop(0)
                
                # Check if alert should trigger
                if self.risk_engine.should_alert():
                    self._handle_alert()
                
                last_processed = latest_screenshot
                
                # Brief pause
                time.sleep(2)
                
            except KeyboardInterrupt:
                self.logger.info("Keyboard interrupt received")
                break
            except Exception as e:
                self.logger.error(f"Main loop error: {e}", exc_info=True)
                time.sleep(5)
    
    def _handle_alert(self):
        """Handle alert trigger."""
        self.logger.warning("🚨 ALERT TRIGGERED 🚨")
        
        # Get risk statistics
        risk_score = self.risk_engine.compute_risk()
        window_stats = self.risk_engine.get_window_stats()
        
        # Capture webcam
        self.logger.info("Capturing webcam image...")
        webcam_path = self.webcam.capture()
        
        # Trigger alert
        alert = self.alert_manager.trigger_alert(
            risk_score=risk_score,
            window_stats=window_stats,
            screenshot_paths=self.recent_screenshots,
            webcam_path=webcam_path
        )
        
        self.logger.critical(f"Alert created: {alert['alert_id']}")
    
    def stop(self):
        """Gracefully stop the system."""
        self.logger.info("Stopping Crisis Detection System...")
        
        self.running = False
        self.screenshot_service.stop()
        self.webcam.release()
        
        self.logger.info("System stopped")


def signal_handler(signum, frame):
    """Handle system signals for graceful shutdown."""
    print("\n\nShutdown signal received...")
    sys.exit(0)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Crisis Detection System')
    parser.add_argument(
        '--config',
        default='crisis_detection/config/config.yaml',
        help='Path to configuration file'
    )
    
    args = parser.parse_args()
    
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Create and start system
    system = CrisisDetectionSystem(args.config)
    
    try:
        system.start()
    except KeyboardInterrupt:
        pass
    finally:
        system.stop()


if __name__ == "__main__":
    main()
