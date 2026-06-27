import logging
import json
import os

# Create logs dir
os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler("logs/app.log"),
        logging.StreamHandler()
    ]
)

def get_logger(name: str):
    return logging.getLogger(name)

def log_stage(stage: str, status: str, details: dict = None):
    logger = get_logger("Pipeline")
    msg = f"[{stage}] Status: {status}"
    if details:
        msg += f" | {json.dumps(details)}"
    logger.info(msg)
