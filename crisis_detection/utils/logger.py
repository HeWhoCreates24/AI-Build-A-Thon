"""
Logger Setup Utility
====================
Configures system-wide logging.
"""

import logging
import sys
from pathlib import Path
from datetime import datetime


def setup_logging(config):
    """
    Setup system logging configuration.
    
    Args:
        config: Logging configuration dict
    """
    log_level = config.get('level', 'INFO')
    log_file = config.get('log_file', 'crisis_detection/data/logs/system.log')
    console_output = config.get('console_output', True)
    
    # Create log directory
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    simple_formatter = logging.Formatter(
        '%(levelname)s: %(message)s'
    )
    
    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level))
    
    # Remove existing handlers
    root_logger.handlers = []
    
    # File handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(detailed_formatter)
    root_logger.addHandler(file_handler)
    
    # Console handler
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, log_level))
        console_handler.setFormatter(detailed_formatter)
        root_logger.addHandler(console_handler)
    
    # Log startup
    logging.info("="*60)
    logging.info(f"Logging initialized - Level: {log_level}")
    logging.info(f"Log file: {log_file}")
    logging.info("="*60)
