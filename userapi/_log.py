# ============================================
#  userapi/_log.py - Standard Logging Setup
#  All code and comments are English. No emojis.
# ============================================
import logging
import os

logger = logging.getLogger("vibegram")

def setup_logging(level=logging.INFO):
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(level)
    return logger

def info(msg):
    if os.getenv("VIBE_VERBOSE") == "1" or os.getenv("VIBE_DEBUG") == "1":
        logger.info(msg)
