#!/usr/bin/env python3
"""
Demo Script for OCR Pipeline
============================
Tests OCR text extraction on screenshots.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from crisis_detection.core.ocr_pipeline import OCRPipeline
from crisis_detection.core.screenshot_service import ScreenshotService
import time
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')


def main():
    """Demo OCR extraction."""
    print("="*60)
    print("OCR Pipeline Demo")
    print("="*60)
    
    # First, capture a screenshot if none exists
    screenshot_dir = Path('crisis_detection/data/screenshots')
    screenshots = sorted(screenshot_dir.glob("screenshot_*.png"))
    
    if not screenshots:
        print("\nNo screenshots found. Capturing one now...")
        config = {
            'capture_interval_seconds': 1,
            'screenshot_dir': 'crisis_detection/data/screenshots',
            'max_screenshots': 1
        }
        service = ScreenshotService(config)
        service._init_camera = lambda: True  # Mock for demo
        
        # Manual capture
        import mss
        with mss.mss() as sct:
            service._capture_screenshot(sct)
        
        screenshots = sorted(screenshot_dir.glob("screenshot_*.png"))
    
    if not screenshots:
        print("ERROR: Could not capture screenshot")
        return
    
    # Use the most recent screenshot
    test_image = screenshots[-1]
    print(f"\nUsing screenshot: {test_image.name}")
    
    # Initialize OCR pipeline
    config = {
        'preprocess': True,
        'tesseract_path': None  # Auto-detect
    }
    
    ocr = OCRPipeline(config)
    
    print("\nExtracting text...")
    text = ocr.extract_text(test_image)
    
    print("\n" + "="*60)
    print("EXTRACTED TEXT")
    print("="*60)
    
    if text:
        print(f"\n{text}\n")
        print(f"Total characters: {len(text)}")
        print(f"Word count: {len(text.split())}")
    else:
        print("\nNo text extracted (empty screen or OCR failed)")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    main()
