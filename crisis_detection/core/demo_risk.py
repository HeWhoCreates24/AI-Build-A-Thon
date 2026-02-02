#!/usr/bin/env python3
"""
Demo Script for Risk Engine
===========================
Tests time-windowed risk aggregation.
"""

import sys
from pathlib import Path
import time
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from crisis_detection.core.risk_engine import RiskEngine
import random


def main():
    """Demo risk engine aggregation."""
    print("="*60)
    print("Risk Engine Demo - Time-Windowed Aggregation")
    print("="*60)
    
    # Configuration
    config = {
        'time_window_minutes': 5,   # 5-minute window for demo
        'alert_threshold': 0.65,
        'min_samples': 3,
        'alert_cooldown_minutes': 2
    }
    
    engine = RiskEngine(config)
    
    print(f"\nConfiguration:")
    print(f"  Time window: {config['time_window_minutes']} minutes")
    print(f"  Alert threshold: {config['alert_threshold']}")
    print(f"  Min samples: {config['min_samples']}")
    print(f"  Cooldown: {config['alert_cooldown_minutes']} minutes")
    
    print("\n" + "="*60)
    print("SCENARIO 1: Gradual Increase in Distress")
    print("="*60)
    
    # Simulate scores over time
    scores_scenario1 = [0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.85, 0.9]
    
    for i, score in enumerate(scores_scenario1, 1):
        engine.add_score(score)
        risk = engine.compute_risk()
        stats = engine.get_window_stats()
        
        print(f"\n[Sample {i}] Score: {score:.2f}")
        print(f"  Risk: {risk:.3f} | Samples: {stats['sample_count']} | Avg: {stats['avg_score']:.3f}")
        
        if engine.should_alert():
            print(f"  🚨 ALERT TRIGGERED! Risk exceeded threshold!")
            print(f"  Window stats: {stats}")
        
        time.sleep(0.5)  # Brief pause for readability
    
    # Reset for next scenario
    engine = RiskEngine(config)
    
    print("\n" + "="*60)
    print("SCENARIO 2: Fluctuating Scores (No Sustained Distress)")
    print("="*60)
    
    scores_scenario2 = [0.7, 0.2, 0.8, 0.3, 0.6, 0.1, 0.7, 0.2]
    
    for i, score in enumerate(scores_scenario2, 1):
        engine.add_score(score)
        risk = engine.compute_risk()
        stats = engine.get_window_stats()
        
        print(f"\n[Sample {i}] Score: {score:.2f}")
        print(f"  Risk: {risk:.3f} | Samples: {stats['sample_count']}")
        
        if engine.should_alert():
            print(f"  🚨 ALERT TRIGGERED!")
        else:
            print(f"  ✓ No alert (fluctuating scores don't trigger)")
        
        time.sleep(0.5)
    
    # Reset for next scenario
    engine = RiskEngine(config)
    
    print("\n" + "="*60)
    print("SCENARIO 3: Sustained High Distress")
    print("="*60)
    
    scores_scenario3 = [0.75, 0.80, 0.78, 0.82, 0.85, 0.83, 0.87]
    
    for i, score in enumerate(scores_scenario3, 1):
        engine.add_score(score)
        risk = engine.compute_risk()
        stats = engine.get_window_stats()
        
        print(f"\n[Sample {i}] Score: {score:.2f}")
        print(f"  Risk: {risk:.3f} | Samples: {stats['sample_count']}")
        
        if engine.should_alert():
            print(f"  🚨 ALERT TRIGGERED! Sustained high distress detected!")
            break
        
        time.sleep(0.5)
    
    print("\n" + "="*60)
    print("\nKey Takeaways:")
    print("  ✅ System requires sustained distress (not single spikes)")
    print("  ✅ Time-windowed aggregation prevents false positives")
    print("  ✅ Recent scores weighted higher than older scores")
    print("  ✅ Frequency multiplier rewards consistent high scores")
    print("="*60)


if __name__ == "__main__":
    main()
