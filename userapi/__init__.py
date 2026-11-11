# ============================================
#  userapi/__init__.py - package exports
#  Applies Vibe custom auth patches and silences
#  benign Telethon shutdown tracebacks (unless VIBE_DEBUG=1).
#  All code and comments are English. No emojis.
# ============================================
import logging
import os

from userapi.crypto.vibe_auth import apply_patches

apply_patches()

if os.getenv("VIBE_DEBUG") != "1":
    logging.getLogger("telethon.network.mtprotosender").setLevel(logging.CRITICAL)
    logging.getLogger("telethon.network.connection.connection").setLevel(logging.CRITICAL)

from userapi.client import VibeClient, API_ID, API_HASH

__all__ = ["VibeClient", "API_ID", "API_HASH"]
