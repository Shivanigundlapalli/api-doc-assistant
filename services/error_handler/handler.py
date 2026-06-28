import json
from services.logging.logger import get_logger

logger = get_logger("ErrorHandler")

class PipelineError(Exception):
    def __init__(self, stage: str, reason: str, retryable: bool = False):
        self.stage = stage
        self.reason = reason
        self.status = "failed"
        self.retryable = retryable
        super().__init__(self.to_json())
        
    def to_json(self):
        return json.dumps({
            "success": False,
            "stage": self.stage,
            "status": self.status,
            "message": self.reason,
            "retryable": self.retryable
        })

def handle_exception(stage: str, e: Exception) -> str:
    """Logs the raw exception internally and returns a clean PipelineError JSON string."""
    logger.error(f"Raw exception in [{stage}]: {e}", exc_info=True)
    
    if isinstance(e, PipelineError):
        return e.to_json()
        
    import traceback
    tb = traceback.format_exc()
    # Assume unknown exceptions might be transient/retryable depending on the stage, but default to false
    err = PipelineError(stage, f"**Internal Error ({type(e).__name__}):** `{str(e)}`\n\n```python\n{tb}\n```", retryable=False)
    return err.to_json()
