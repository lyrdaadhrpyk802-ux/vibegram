# ============================================
#  userapi/_config.py - environment-based configuration
#  Reads API credentials and DC settings from env with safe defaults.
#  All code and comments are English. No emojis.
# ============================================
import os
from typing import Tuple


# Vibe's official public app credentials (shipped with the client).
# Users can override via env without touching source.
DEFAULT_API_ID = 4
DEFAULT_API_HASH = "014b35b6184100b085b0d0572f9b5103"
DEFAULT_DC_HOST = "web.vibegram.chat"
DEFAULT_DC_PORT = 443
DEFAULT_DC_ID = 2


def _get_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None or raw.strip() == "":
        return default
    try:
        return int(raw)
    except ValueError:
        print(f"[_config] error: invalid int for {name}={raw!r}, using default {default}")
        return default


def get_api_credentials() -> Tuple[int, str]:
    """Return (api_id, api_hash) from env or defaults."""
    api_id = _get_int("VIBE_API_ID", DEFAULT_API_ID)
    api_hash = os.getenv("VIBE_API_HASH", DEFAULT_API_HASH)
    return api_id, api_hash


def get_dc_settings() -> Tuple[str, int, int]:
    """Return (dc_host, dc_port, dc_id) from env or defaults."""
    host = os.getenv("VIBE_DC_HOST", DEFAULT_DC_HOST)
    port = _get_int("VIBE_DC_PORT", DEFAULT_DC_PORT)
    dc_id = _get_int("VIBE_DC_ID", DEFAULT_DC_ID)
    return host, port, dc_id


# Backward-compatible module-level constants (used by older imports).
API_ID, API_HASH = get_api_credentials()
DEFAULT_DC_HOST = os.getenv("VIBE_DC_HOST", DEFAULT_DC_HOST)
DEFAULT_DC_PORT = _get_int("VIBE_DC_PORT", DEFAULT_DC_PORT)
DEFAULT_DC_ID = _get_int("VIBE_DC_ID", DEFAULT_DC_ID)
