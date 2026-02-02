#!/usr/bin/env python3
"""
Demo Script for Screenshot Service
===================================
Tests the screenshot capture functionality.
"""

import sys
import time
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from crisis_detection.core.screenshot_service import ScreenshotService
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')


def main():
    """Demo the screenshot service."""
    print("="*60)
    print("Screenshot Service Demo")
    print("="*60)
    
    # Configuration for demo (fast captures)
    config = {
        'capture_interval_seconds': 5,  # Capture every 5 seconds
        'screenshot_dir': 'crisis_detection/data/screenshots',
        'max_screenshots': 10
    }
    
    # Create service
    service = ScreenshotService(config)
    
    print(f"\nStarting screenshot capture...")
    print(f"Interval: {config['capture_interval_seconds']} seconds")
    print(f"Directory: {config['screenshot_dir']}")
    print(f"Press Ctrl+C to stop\n")
    
    # Start service
    service.start()
    
    try:
        # Run for 30 seconds
        for i in range(6):
            time.sleep(5)
            screenshot_dir = Path(config['screenshot_dir'])
            count = len(list(screenshot_dir.glob("screenshot_*.png")))
            print(f"[{i*5}s] Screenshots captured: {count}")
    
    except KeyboardInterrupt:
        print("\n\nStopping...")
    
    finally:
        service.stop()
        print("Screenshot service stopped")
        
        # Show results
        screenshot_dir = Path(config['screenshot_dir'])
        screenshots = sorted(screenshot_dir.glob("screenshot_*.png"))
        print(f"\nTotal screenshots: {len(screenshots)}")
        if screenshots:
            print("\nRecent screenshots:")
            for ss in screenshots[-3:]:
                print(f"  - {ss.name}")


if __name__ == "__main__":
    main()
