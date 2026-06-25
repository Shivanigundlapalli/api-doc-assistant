import logging
import os
from logging.handlers import RotatingFileHandler
from config import is_logging_enabled, is_debug_mode

def get_logger(name: str) -> logging.Logger:
    """
    Returns a configured logger instance.
    Logs to 'logs/app.log' if ENABLE_LOGGING is True.
    """
    logger = logging.getLogger(name)
    
    # Prevent duplicate handlers
    if logger.hasHandlers():
        return logger

    # Set log level based on DEBUG flag
    level = logging.DEBUG if is_debug_mode() else logging.INFO
    logger.setLevel(level)

    # Standard formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File Handler
    if is_logging_enabled():
        log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
        if not os.path.exists(log_dir):
            try:
                os.makedirs(log_dir)
            except Exception:
                pass # Fail silently if we can't create the directory (e.g., read-only filesystem)
        
        try:
            log_file = os.path.join(log_dir, "app.log")
            # 5 MB max per file, keep 3 backups
            file_handler = RotatingFileHandler(log_file, maxBytes=5*1024*1024, backupCount=3)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except Exception as e:
            # If we don't have write permissions, just skip file logging
            console_handler.setLevel(logging.WARNING)
            logger.warning(f"Could not initialize file logger: {e}")

    return logger
