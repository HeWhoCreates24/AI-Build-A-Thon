"""
Configuration Loader Utility
============================
Loads and validates system configuration.
"""

import yaml
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


def load_config(config_path):
    """
    Load configuration from YAML file.
    
    Args:
        config_path: Path to config file
        
    Returns:
        dict: Configuration dictionary
    """
    config_file = Path(config_path)
    
    if not config_file.exists():
        logger.warning(f"Config file not found: {config_path}, using defaults")
        return get_default_config()
    
    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)
    
    # Merge with defaults for missing keys
    default_config = get_default_config()
    config = merge_configs(default_config, config)
    
    return config


def merge_configs(default, custom):
    """
    Recursively merge custom config into default.
    
    Args:
        default: Default configuration
        custom: Custom configuration
        
    Returns:
        Merged configuration
    """
    if isinstance(default, dict) and isinstance(custom, dict):
        merged = default.copy()
        for key, value in custom.items():
            if key in merged:
                merged[key] = merge_configs(merged[key], value)
            else:
                merged[key] = value
        return merged
    else:
        return custom


def get_default_config():
    """
    Get default system configuration.
    
    Returns:
        dict: Default config
    """
    return {
        'screenshot': {
            'capture_interval_seconds': 30,
            'screenshot_dir': 'crisis_detection/data/screenshots',
            'max_screenshots': 100
        },
        'ocr': {
            'preprocess': True,
            'tesseract_path': None  # Auto-detect
        },
        'nlp': {
            'mode': 'auto',  # 'ml', 'rules', or 'auto'
            'model_path': 'crisis_detection/models/distress_model',
            'model_name': 'distilbert-base-uncased',
            'allow_online_model_download': False
        },
        'risk': {
            'time_window_minutes': 15,
            'alert_threshold': 0.65,
            'min_samples': 5,
            'alert_cooldown_minutes': 30
        },
        'webcam': {
            'camera_index': 0,
            'save_dir': 'crisis_detection/data/webcam_captures',
            'blur_background': False,
            'max_captures': 50
        },
        'alerts': {
            'alert_log_dir': 'crisis_detection/data/logs/alerts',
            'evidence_dir': 'crisis_detection/data/evidence',
            'notification_methods': ['log', 'file'],
            'admin_email': None
        },
        'logging': {
            'level': 'INFO',
            'log_file': 'crisis_detection/data/logs/system.log',
            'console_output': True
        }
    }
