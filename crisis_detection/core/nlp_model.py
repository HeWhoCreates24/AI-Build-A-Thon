"""
NLP Model Module
================
Scores text for psychological distress and crisis indicators.
Supports both ML-based and rule-based approaches.

Architecture:
- Primary: DistilBERT/MiniLM fine-tuned model (CPU-optimized)
- Fallback: Rule-based keyword scoring
- ONNX runtime for fast inference
- Local-only (no API calls)

Data Flow:
  Cleaned Text → Tokenization → Model Inference → Distress Score (0-1)
"""

import logging
import re
from pathlib import Path

logger = logging.getLogger(__name__)

# Optional: ML model imports (graceful fallback if not available)
try:
    from transformers import AutoTokenizer, AutoModelForSequenceClassification
    import torch
    HAS_TRANSFORMERS = True
except ImportError:
    HAS_TRANSFORMERS = False
    logger.warning("Transformers not available, using rule-based fallback")


class NLPModel:
    """
    Detect psychological distress in text.
    
    Responsibilities:
    - Load and manage ML model (or fallback)
    - Score text for crisis indicators
    - Provide confidence scores
    
    Modes:
    - 'ml': Use transformer model
    - 'rules': Use keyword-based scoring
    - 'auto': Try ML, fallback to rules
    """
    
    def __init__(self, config):
        """
        Args:
            config: Configuration with:
                - mode: 'ml', 'rules', or 'auto'
                - model_path: Path to saved model
                - model_name: HuggingFace model name
        """
        self.mode = config.get('mode', 'auto')
        self.model = None
        self.tokenizer = None
        
        # Try to load ML model
        if self.mode in ['ml', 'auto'] and HAS_TRANSFORMERS:
            self._load_ml_model(config)
        
        # Fallback to rules if ML not available
        if self.model is None:
            logger.info("Using rule-based fallback for distress detection")
            self.mode = 'rules'
        
        # Load crisis keywords
        self._load_crisis_keywords()
    
    def _load_ml_model(self, config):
        """Load transformer model for distress detection."""
        try:
            model_path = config.get('model_path')
            model_name = config.get('model_name', 'distilbert-base-uncased')
            allow_online = config.get('allow_online_model_download', False)
            
            if model_path and Path(model_path).exists():
                # Load fine-tuned local model
                self.tokenizer = AutoTokenizer.from_pretrained(model_path)
                self.model = AutoModelForSequenceClassification.from_pretrained(model_path)
                logger.info(f"Loaded fine-tuned model from {model_path}")
            else:
                if not allow_online:
                    logger.warning("No local model found and online download disabled; using rule-based fallback")
                    self.model = None
                    self.tokenizer = None
                    return
                # For hackathon demo: use base model (would normally be fine-tuned)
                # This is a placeholder - real system needs mental health fine-tuning
                logger.warning("No fine-tuned model found, using base model (DEMO ONLY)")
                self.tokenizer = AutoTokenizer.from_pretrained(model_name)
                self.model = AutoModelForSequenceClassification.from_pretrained(
                    model_name,
                    num_labels=2  # Binary: distress / no-distress
                )
            
            self.model.eval()  # Set to evaluation mode
            
        except Exception as e:
            logger.error(f"Failed to load ML model: {e}")
            self.model = None
    
    def _load_crisis_keywords(self):
        """
        Load crisis/distress keywords and phrases.
        
        Categories:
        - Suicide ideation
        - Self-harm
        - Hopelessness
        - Severe depression indicators
        """
        self.crisis_keywords = {
            'high_severity': [
                'kill myself', 'end my life', 'suicide', 'want to die',
                'better off dead', 'no reason to live', 'goodbye world'
            ],
            'medium_severity': [
                'hopeless', 'worthless', 'can\'t go on', 'give up',
                'no point', 'hate myself', 'self harm', 'cut myself',
                'nobody cares', 'disappear forever'
            ],
            'low_severity': [
                'depressed', 'sad', 'lonely', 'anxious', 'stressed',
                'overwhelmed', 'tired of everything', 'struggling'
            ]
        }
        
        # Severity weights
        self.severity_weights = {
            'high_severity': 1.0,
            'medium_severity': 0.6,
            'low_severity': 0.3
        }
    
    def score_text(self, text):
        """
        Score text for distress level.
        
        Args:
            text: String to analyze
            
        Returns:
            float: Distress score (0.0 to 1.0)
                  0.0 = No distress
                  1.0 = Critical distress
        """
        if not text or len(text.strip()) < 10:
            return 0.0
        
        if self.mode == 'ml' and self.model:
            return self._score_ml(text)
        else:
            return self._score_rules(text)
    
    def _score_ml(self, text):
        """
        Score using ML model.
        
        Args:
            text: Input text
            
        Returns:
            Distress probability (0-1)
        """
        try:
            # Tokenize
            inputs = self.tokenizer(
                text,
                padding=True,
                truncation=True,
                max_length=512,
                return_tensors='pt'
            )
            
            # Inference (no gradient computation)
            with torch.no_grad():
                outputs = self.model(**inputs)
                logits = outputs.logits
                
                # Convert to probability (softmax)
                probs = torch.nn.functional.softmax(logits, dim=-1)
                
                # Return probability of distress class (class 1)
                distress_prob = probs[0][1].item()
            
            return distress_prob
            
        except Exception as e:
            logger.error(f"ML scoring error: {e}")
            # Fallback to rules
            return self._score_rules(text)
    
    def _score_rules(self, text):
        """
        Rule-based scoring using keyword matching.
        
        Algorithm:
        - Check for crisis keywords (weighted by severity)
        - Account for frequency
        - Normalize to 0-1 scale
        
        Args:
            text: Input text
            
        Returns:
            Distress score (0-1)
        """
        text_lower = text.lower()
        score = 0.0
        
        # Check each severity category
        for severity, keywords in self.crisis_keywords.items():
            weight = self.severity_weights[severity]
            
            for keyword in keywords:
                # Count occurrences (but cap to avoid over-weighting)
                count = min(text_lower.count(keyword), 3)
                score += count * weight * 0.2  # 0.2 per occurrence
        
        # Normalize to 0-1 (cap at 1.0)
        return min(score, 1.0)


# Example usage:
"""
if __name__ == "__main__":
    config = {
        'mode': 'auto',
        'model_path': 'models/distress_model',
        'model_name': 'distilbert-base-uncased'
    }
    
    nlp = NLPModel(config)
    
    # Test texts
    test_samples = [
        "I'm feeling a bit sad today",
        "I can't take this anymore, I want to end it all",
        "Working on my Python project for class"
    ]
    
    for sample in test_samples:
        score = nlp.score_text(sample)
        print(f"Text: {sample}")
        print(f"Distress Score: {score:.3f}\n")
"""
