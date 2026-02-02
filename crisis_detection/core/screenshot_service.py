"""
Screenshot Service Module
==========================
Captures desktop screenshots at configurable intervals.
Runs as a background service/thread.

Architecture:
- Uses mss (fast, cross-platform screenshot library)
- Configurable capture interval (default: 30 seconds)
- Saves screenshots with timestamp for evidence trail
- Minimal memory footprint (cleans old screenshots)

Data Flow:
  System Start → Screenshot Service → OCR Pipeline
"""

import mss
import time
from datetime import datetime
from pathlib import Path
import threading
import logging
import os
import sys

logger = logging.getLogger(__name__)


class ScreenshotService:
    """
    Continuously captures desktop screenshots at regular intervals.
    
    Responsibilities:
    - Capture full desktop screen
    - Save with timestamp
    - Maintain rolling buffer (delete old screenshots)
    - Thread-safe operation
    """
    
    def __init__(self, config):
        """
        Args:
            config: Configuration object with:
                - capture_interval_seconds: Time between captures
                - screenshot_dir: Directory to save screenshots
                - max_screenshots: Maximum screenshots to keep
        """
        self.interval = config.get('capture_interval_seconds', 30)
        self.screenshot_dir = Path(config.get('screenshot_dir', 'data/screenshots'))
        self.max_screenshots = config.get('max_screenshots', 100)
        self.running = False
        self._thread = None
        
        # Ensure directory exists
        self.screenshot_dir.mkdir(parents=True, exist_ok=True)
    
    def start(self):
        """Start the screenshot capture service in a background thread.

        Returns:
            bool: True if started successfully, False otherwise.
        """
        if self.running:
            logger.warning("Screenshot service already running")
            return True

        if sys.platform.startswith("linux") and not os.environ.get("DISPLAY"):
            logger.error("Cannot start screenshot service: $DISPLAY not set (headless environment)")
            return False
        
        self.running = True
        self._thread = threading.Thread(target=self._capture_loop, daemon=True)
        self._thread.start()
        logger.info(f"Screenshot service started (interval: {self.interval}s)")
        return True
    
    def stop(self):
        """Stop the screenshot capture service."""
        self.running = False
        if self._thread:
            self._thread.join(timeout=5)
        logger.info("Screenshot service stopped")
    
    def _capture_loop(self):
        """Main capture loop (runs in background thread)."""
        with mss.mss() as sct:
            while self.running:
                try:
                    self._capture_screenshot(sct)
                    self._cleanup_old_screenshots()
                    time.sleep(self.interval)
                except mss.exception.ScreenShotError as e:
                    logger.error(f"Screenshot capture error: {e}")
                    self.running = False
                except Exception as e:
                    logger.error(f"Screenshot capture error: {e}")
    
    def _capture_screenshot(self, sct):
        """
        Capture a single screenshot.
        
        Args:
            sct: mss screenshot object
            
        Returns:
            Path to saved screenshot
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{timestamp}.png"
        filepath = self.screenshot_dir / filename
        
        # Capture monitor 1 (primary display)
        monitor = sct.monitors[1]
        screenshot = sct.grab(monitor)
        
        # Save to disk
        mss.tools.to_png(screenshot.rgb, screenshot.size, output=str(filepath))
        
        logger.debug(f"Captured screenshot: {filename}")
        return filepath
    
    def _cleanup_old_screenshots(self):
        """Remove oldest screenshots to maintain buffer size."""
        screenshots = sorted(self.screenshot_dir.glob("screenshot_*.png"))
        
        if len(screenshots) > self.max_screenshots:
            to_delete = len(screenshots) - self.max_screenshots
            for screenshot in screenshots[:to_delete]:
                screenshot.unlink()
                logger.debug(f"Deleted old screenshot: {screenshot.name}")


# Example usage structure:
"""
if __name__ == "__main__":
    config = {
        'capture_interval_seconds': 30,
        'screenshot_dir': 'data/screenshots',
        'max_screenshots': 100
    }
    
    service = ScreenshotService(config)
    service.start()
    
    # Keep running...
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        service.stop()
"""
