import logging
import colorlog
import os
from datetime import datetime
from pathlib import Path

def setup_logger(name: str = None) -> logging.Logger:
    """
    Set up a logger with colored console output and file output.
    
    Args:
        name (str, optional): Logger name. If None, returns the root logger.
        
    Returns:
        logging.Logger: Configured logger instance
    """
    # Create logs directory if it doesn't exist
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Create a logger
    logger = logging.getLogger(name)
    if logger.handlers:  # Return logger if already configured
        return logger
        
    logger.setLevel(logging.DEBUG)
    
    # Create console handler with colored output
    console_handler = colorlog.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Create color formatter
    console_formatter = colorlog.ColoredFormatter(
        "%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        }
    )
    console_handler.setFormatter(console_formatter)
    
    # Create file handler
    current_time = datetime.now().strftime("%Y%m%d")
    file_handler = logging.FileHandler(
        filename=f"logs/app_{current_time}.log",
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    
    # Create file formatter
    file_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    file_handler.setFormatter(file_formatter)
    
    # Add handlers to logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger 