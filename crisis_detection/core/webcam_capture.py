"""
Webcam Capture Module
=====================
Captures single webcam image when alert is triggered.

Architecture:
- Uses OpenCV for camera access
- Captures ONLY on alert (not continuous)
- Privacy-aware: can blur background
- Saves with timestamp for evidence

CRITICAL:
  No continuous recording.
  No video storage.
  Single frame only on alert.

Data Flow:
  Alert Triggered → Capture Frame → Optional Privacy Filter → Save Image
"""

import cv2
from datetime import datetime
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class WebcamCapture:
    """
    Capture single webcam images on demand.
    
    Responsibilities:
    - Initialize camera connection
    - Capture single frame on request
    - Apply privacy filters (optional)
    - Save with timestamp
    
    Privacy Features:
    - Background blur
    - Face detection only (optional)
    - Immediate cleanup
    """
    
    def __init__(self, config):
        """
        Args:
            config: Configuration with:
                - camera_index: Camera device index (0 = default)
                - save_dir: Directory for webcam captures
                - blur_background: Enable privacy blur
                - max_captures: Maximum captures to keep
        """
        self.camera_index = config.get('camera_index', 0)
        self.save_dir = Path(config.get('save_dir', 'data/webcam_captures'))
        self.blur_background = config.get('blur_background', False)
        self.max_captures = config.get('max_captures', 50)
        
        # Ensure directory exists
        self.save_dir.mkdir(parents=True, exist_ok=True)
        
        # Camera object (lazy initialization)
        self.camera = None
    
    def _init_camera(self):
        """Initialize camera if not already done."""
        if self.camera is None or not self.camera.isOpened():
            self.camera = cv2.VideoCapture(self.camera_index)
            
            if not self.camera.isOpened():
                logger.error(f"Failed to open camera {self.camera_index}")
                return False
            
            # Set camera properties for faster capture
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            
            logger.info(f"Camera {self.camera_index} initialized")
        
        return True
    
    def capture(self):
        """
        Capture a single webcam frame.
        
        Returns:
            Path: Path to saved image, or None if failed
        """
        try:
            # Initialize camera
            if not self._init_camera():
                logger.error("Camera initialization failed")
                return None
            
            # Capture frame
            ret, frame = self.camera.read()
            
            if not ret or frame is None:
                logger.error("Failed to capture frame")
                return None
            
            # Apply privacy filter if enabled
            if self.blur_background:
                frame = self._blur_background(frame)
            
            # Save with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"webcam_{timestamp}.jpg"
            filepath = self.save_dir / filename
            
            cv2.imwrite(str(filepath), frame)
            logger.info(f"Captured webcam image: {filename}")
            
            # Cleanup old captures
            self._cleanup_old_captures()
            
            return filepath
            
        except Exception as e:
            logger.error(f"Webcam capture error: {e}")
            return None
    
    def _blur_background(self, frame):
        """
        Apply background blur for privacy.
        
        Simple implementation: general blur
        Advanced: face detection + selective blur
        
        Args:
            frame: OpenCV image
            
        Returns:
            Blurred frame
        """
        # Simple approach: blur entire image
        # For hackathon demo, this is sufficient
        blurred = cv2.GaussianBlur(frame, (51, 51), 0)
        
        # TODO: Advanced version would use face detection
        # to blur only background, keeping face in focus
        
        return blurred
    
    def _cleanup_old_captures(self):
        """Remove oldest captures to maintain buffer size."""
        captures = sorted(self.save_dir.glob("webcam_*.jpg"))
        
        if len(captures) > self.max_captures:
            to_delete = len(captures) - self.max_captures
            for capture in captures[:to_delete]:
                capture.unlink()
                logger.debug(f"Deleted old capture: {capture.name}")
    
    def release(self):
        """Release camera resources."""
        if self.camera:
            self.camera.release()
            self.camera = None
            logger.info("Camera released")


# Example usage:
"""
if __name__ == "__main__":
    config = {
        'camera_index': 0,
        'save_dir': 'data/webcam_captures',
        'blur_background': False,
        'max_captures': 50
    }
    
    webcam = WebcamCapture(config)
    
    # Simulate alert trigger
    print("Alert triggered! Capturing webcam...")
    image_path = webcam.capture()
    
    if image_path:
        print(f"Saved to: {image_path}")
    
    webcam.release()
"""
