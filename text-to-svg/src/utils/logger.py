"""Custom logger configuration for the application."""
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.logging import RichHandler
from rich.traceback import install as install_rich_traceback

# Install rich traceback handling
install_rich_traceback()

# Create logs directory if it doesn't exist
LOGS_DIR = Path("logs")
LOGS_DIR.mkdir(exist_ok=True)

class CustomLogger:
    """Custom logger with rich formatting and file output."""

    def __init__(
        self,
        name: str,
        log_file: Optional[str] = None,
        level: int = logging.INFO
    ):
        """Initialize the custom logger.
        
        Args:
            name: Logger name
            log_file: Optional log file path
            level: Logging level
        """
        self.console = Console()
        
        # Create logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        # Remove existing handlers
        self.logger.handlers = []

        # Create formatters
        console_format = "%(message)s"
        file_format = (
            "[%(asctime)s] %(levelname)-8s %(name)s: "
            "%(message)s (%(filename)s:%(lineno)d)"
        )

        # Console handler with rich formatting
        console_handler = RichHandler(
            console=self.console,
            show_path=False,
            enable_link_path=True,
            markup=True,
            rich_tracebacks=True,
            tracebacks_show_locals=True,
        )
        console_handler.setFormatter(logging.Formatter(console_format))
        self.logger.addHandler(console_handler)

        # File handler if log_file is specified
        if log_file:
            log_path = LOGS_DIR / log_file
            file_handler = logging.FileHandler(log_path)
            file_handler.setFormatter(logging.Formatter(file_format))
            self.logger.addHandler(file_handler)

    @property
    def log(self) -> logging.Logger:
        """Get the configured logger instance."""
        return self.logger

def get_logger(
    name: str,
    log_file: Optional[str] = None,
    level: int = logging.INFO
) -> logging.Logger:
    """Get a configured logger instance.
    
    Args:
        name: Logger name
        log_file: Optional log file path
        level: Logging level
        
    Returns:
        logging.Logger: Configured logger instance
    """
    if not log_file:
        # Generate default log file name based on date
        date_str = datetime.now().strftime("%Y%m%d")
        log_file = f"{date_str}_{name}.log"

    return CustomLogger(name, log_file, level).log 