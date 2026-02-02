#!/usr/bin/env python3
"""
Demo Script for NLP Model
=========================
Tests distress scoring on sample texts.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from crisis_detection.core.nlp_model import NLPModel
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')


def main():
    """Demo NLP distress scoring."""
    print("="*60)
    print("NLP Model Demo - Distress Detection")
    print("="*60)
    
    # Initialize model (will use rules-based if ML not available)
    config = {
        'mode': 'auto',
        'model_path': 'crisis_detection/models/distress_model',
        'model_name': 'distilbert-base-uncased'
    }
    
    print("\nInitializing NLP model...")
    nlp = NLPModel(config)
    print(f"Mode: {nlp.mode}")
    
    # Test samples with varying distress levels
    test_samples = [
        {
            'text': "I'm working on my Python assignment for CS 101. It's challenging but interesting.",
            'expected': 'low'
        },
        {
            'text': "I feel a bit sad today. The weather is gloomy and I'm tired.",
            'expected': 'low-medium'
        },
        {
            'text': "I'm feeling really depressed. Everything seems hopeless and I don't know what to do.",
            'expected': 'medium-high'
        },
        {
            'text': "I can't take this anymore. I feel worthless and like nobody cares. I just want it all to end.",
            'expected': 'high'
        },
        {
            'text': "I'm thinking about suicide. I have a plan and I don't see any reason to keep going.",
            'expected': 'critical'
        },
        {
            'text': "Just finished a great workout! Feeling energized and ready for the day.",
            'expected': 'none'
        }
    ]
    
    print("\n" + "="*60)
    print("TESTING DISTRESS DETECTION")
    print("="*60)
    
    for i, sample in enumerate(test_samples, 1):
        text = sample['text']
        expected = sample['expected']
        
        print(f"\n[Test {i}]")
        print(f"Text: {text[:70]}..." if len(text) > 70 else f"Text: {text}")
        
        score = nlp.score_text(text)
        
        # Interpret score
        if score < 0.3:
            level = "Low/None"
            icon = "✅"
        elif score < 0.6:
            level = "Moderate"
            icon = "⚠️"
        elif score < 0.8:
            level = "High"
            icon = "🔴"
        else:
            level = "CRITICAL"
            icon = "🚨"
        
        print(f"Score: {score:.3f} | Level: {level} {icon}")
        print(f"Expected: {expected}")
    
    print("\n" + "="*60)
    print("\nScore Interpretation:")
    print("  0.0 - 0.3: Low/no distress ✅")
    print("  0.3 - 0.6: Moderate concern ⚠️")
    print("  0.6 - 0.8: High distress 🔴")
    print("  0.8 - 1.0: Critical risk 🚨")
    print("="*60)


if __name__ == "__main__":
    main()
