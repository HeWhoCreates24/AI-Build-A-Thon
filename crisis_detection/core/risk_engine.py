"""
Risk Engine Module
==================
Aggregates distress scores over time and triggers alerts.

Architecture:
- Maintains sliding time window of scores
- Weighted aggregation (recent scores weighted higher)
- Threshold-based alerting
- Prevents false positives from single spikes

Key Principle:
  DO NOT alert on a single sentence.
  Require sustained, consistent distress signals.

Data Flow:
  NLP Scores → Time Window Buffer → Risk Aggregation → Alert Trigger Decision
"""

import time
from datetime import datetime, timedelta
from collections import deque
import logging

logger = logging.getLogger(__name__)


class RiskEngine:
    """
    Aggregate risk scores and determine when to trigger alerts.
    
    Responsibilities:
    - Maintain rolling window of distress scores
    - Compute weighted aggregate score
    - Apply threshold logic
    - Prevent alert fatigue (cooldown periods)
    
    Alert Criteria:
    - Sustained high scores over time window
    - Multiple signals align
    - Not just a single spike
    """
    
    def __init__(self, config):
        """
        Args:
            config: Configuration with:
                - time_window_minutes: Size of rolling window
                - alert_threshold: Score threshold (0-1)
                - min_samples: Minimum samples before alerting
                - alert_cooldown_minutes: Time between alerts
        """
        self.time_window = timedelta(minutes=config.get('time_window_minutes', 15))
        self.alert_threshold = config.get('alert_threshold', 0.65)
        self.min_samples = config.get('min_samples', 5)
        self.alert_cooldown = timedelta(minutes=config.get('alert_cooldown_minutes', 30))
        
        # Rolling buffer: (timestamp, score)
        self.score_buffer = deque(maxlen=1000)
        
        # Alert tracking
        self.last_alert_time = None
        self.alert_count = 0
    
    def add_score(self, score, timestamp=None):
        """
        Add a new distress score to the rolling buffer.
        
        Args:
            score: Distress score (0-1)
            timestamp: When the score was generated (default: now)
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        self.score_buffer.append((timestamp, score))
        logger.debug(f"Added score: {score:.3f} at {timestamp}")
    
    def compute_risk(self):
        """
        Compute aggregated risk score from rolling window.
        
        Algorithm:
        1. Filter to time window
        2. Apply temporal weighting (recent = higher weight)
        3. Compute weighted average
        4. Apply frequency multiplier
        
        Returns:
            float: Aggregated risk score (0-1)
        """
        now = datetime.now()
        window_start = now - self.time_window
        
        # Filter to time window
        window_scores = [
            (ts, score) for ts, score in self.score_buffer
            if ts >= window_start
        ]
        
        if len(window_scores) < self.min_samples:
            logger.debug(f"Insufficient samples: {len(window_scores)}/{self.min_samples}")
            return 0.0
        
        # Compute weighted average
        total_weight = 0.0
        weighted_sum = 0.0
        
        for ts, score in window_scores:
            # Temporal weight: more recent = higher weight
            age_seconds = (now - ts).total_seconds()
            window_seconds = self.time_window.total_seconds()
            recency = 1.0 - (age_seconds / window_seconds)  # 1.0 = now, 0.0 = window start
            
            # Weight function: exponential decay favoring recent
            weight = recency ** 0.5  # Square root for moderate decay
            
            weighted_sum += score * weight
            total_weight += weight
        
        base_risk = weighted_sum / total_weight if total_weight > 0 else 0.0
        
        # Frequency multiplier: consistent high scores increase risk
        high_score_count = sum(1 for _, score in window_scores if score > 0.5)
        frequency_ratio = high_score_count / len(window_scores)
        
        # Boost risk if many high scores (indicates sustained distress)
        frequency_multiplier = 1.0 + (frequency_ratio * 0.3)  # Up to 30% boost
        
        final_risk = min(base_risk * frequency_multiplier, 1.0)
        
        logger.debug(f"Risk: {final_risk:.3f} (base: {base_risk:.3f}, freq: {frequency_ratio:.2f})")
        return final_risk
    
    def should_alert(self):
        """
        Determine if an alert should be triggered.
        
        Criteria:
        1. Risk score exceeds threshold
        2. Cooldown period has elapsed
        3. Sufficient data in window
        
        Returns:
            bool: True if alert should trigger
        """
        # Check cooldown
        if self.last_alert_time:
            time_since_alert = datetime.now() - self.last_alert_time
            if time_since_alert < self.alert_cooldown:
                logger.debug(f"Alert cooldown: {time_since_alert} < {self.alert_cooldown}")
                return False
        
        # Compute current risk
        risk_score = self.compute_risk()
        
        # Check threshold
        if risk_score >= self.alert_threshold:
            logger.warning(f"ALERT THRESHOLD EXCEEDED: {risk_score:.3f} >= {self.alert_threshold}")
            self.last_alert_time = datetime.now()
            self.alert_count += 1
            return True
        
        return False
    
    def get_window_stats(self):
        """
        Get statistics about the current time window.
        
        Returns:
            dict: Window statistics for reporting
        """
        now = datetime.now()
        window_start = now - self.time_window
        
        window_scores = [
            score for ts, score in self.score_buffer
            if ts >= window_start
        ]
        
        if not window_scores:
            return {
                'sample_count': 0,
                'avg_score': 0.0,
                'max_score': 0.0,
                'risk_score': 0.0
            }
        
        return {
            'sample_count': len(window_scores),
            'avg_score': sum(window_scores) / len(window_scores),
            'max_score': max(window_scores),
            'min_score': min(window_scores),
            'risk_score': self.compute_risk(),
            'window_minutes': self.time_window.total_seconds() / 60
        }


# Example usage:
"""
if __name__ == "__main__":
    config = {
        'time_window_minutes': 15,
        'alert_threshold': 0.65,
        'min_samples': 5,
        'alert_cooldown_minutes': 30
    }
    
    engine = RiskEngine(config)
    
    # Simulate incoming scores
    import random
    for i in range(20):
        score = random.uniform(0.3, 0.9)
        engine.add_score(score)
        
        if engine.should_alert():
            print(f"🚨 ALERT TRIGGERED at sample {i}")
            print(engine.get_window_stats())
        
        time.sleep(1)
"""
