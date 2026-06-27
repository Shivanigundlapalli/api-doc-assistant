import logging

logger = logging.getLogger(__name__)

class AIServiceError(Exception):
    """Custom exception for AI service failures."""
    pass

def handle_error(error: Exception, default_message: str = "The AI service is temporarily unavailable.") -> str:
    """
    Standard error handler. Logs the error and returns a user-friendly message.
    """
    logger.error(f"Error occurred: {error}")
    return default_message
