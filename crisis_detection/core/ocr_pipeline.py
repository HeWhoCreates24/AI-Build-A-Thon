"""
OCR Pipeline Module
===================
Extracts text from screenshots using Tesseract OCR.
Includes preprocessing for better accuracy.

Architecture:
- Uses Tesseract OCR (fully offline)
- Preprocessing: grayscale, thresholding, noise reduction
- Optimized for screen text (clean fonts)

Data Flow:
  Screenshot → Preprocessing → OCR → Cleaned Text → NLP Model
"""

import pytesseract
from PIL import Image
import cv2
import numpy as np
import logging
import re

logger = logging.getLogger(__name__)


class OCRPipeline:
    """
    Extract and clean text from screenshots.
    
    Responsibilities:
    - Load and preprocess images
    - Perform OCR extraction
    - Basic text cleaning
    """
    
    def __init__(self, config):
        """
        Args:
            config: Configuration object with:
                - tesseract_path: Path to tesseract executable (Windows)
                - preprocess: Whether to apply preprocessing
        """
        self.preprocess_enabled = config.get('preprocess', True)
        
        # Set Tesseract path (mainly for Windows)
        tesseract_path = config.get('tesseract_path')
        if tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
    
    def extract_text(self, image_path):
        """
        Extract text from an image file.
        
        Args:
            image_path: Path to screenshot image
            
        Returns:
            str: Extracted text (cleaned)
        """
        try:
            # Load image
            image = cv2.imread(str(image_path))
            
            if image is None:
                logger.error(f"Failed to load image: {image_path}")
                return ""
            
            # Preprocess if enabled
            if self.preprocess_enabled:
                image = self._preprocess_image(image)
            
            # Convert to PIL Image for pytesseract
            if len(image.shape) == 2:  # Grayscale
                pil_image = Image.fromarray(image)
            else:  # Color
                pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            
            # Perform OCR
            text = pytesseract.image_to_string(pil_image)
            
            # Clean text
            cleaned_text = self._clean_text(text)
            
            logger.debug(f"Extracted {len(cleaned_text)} characters from {image_path}")
            return cleaned_text
            
        except Exception as e:
            logger.error(f"OCR extraction error: {e}")
            return ""
    
    def _preprocess_image(self, image):
        """
        Preprocess image for better OCR accuracy.
        
        Techniques:
        - Convert to grayscale
        - Apply thresholding
        - Denoise
        
        Args:
            image: OpenCV image
            
        Returns:
            Preprocessed image
        """
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Denoise
        denoised = cv2.fastNlMeansDenoising(gray, h=10)
        
        # Apply adaptive thresholding
        # Good for varying lighting conditions
        threshold = cv2.adaptiveThreshold(
            denoised,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            11,
            2
        )
        
        return threshold
    
    def _clean_text(self, text):
        """
        Clean OCR output text.
        
        Operations:
        - Remove excessive whitespace
        - Remove special OCR artifacts
        - Normalize line breaks
        
        Args:
            text: Raw OCR output
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove common OCR artifacts
        text = re.sub(r'[|_]{3,}', '', text)  # Long underscores/pipes
        
        # Normalize quotes
        text = text.replace('"', '"').replace('"', '"')
        
        # Strip and return
        return text.strip()


# Example usage structure:
"""
if __name__ == "__main__":
    config = {
        'preprocess': True,
        'tesseract_path': r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Windows
    }
    
    ocr = OCRPipeline(config)
    text = ocr.extract_text('data/screenshots/screenshot_20260202_143000.png')
    print(f"Extracted: {text[:200]}...")
"""
