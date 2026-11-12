# ============================================
#  userapi/_log.py - module-load logging (silent by default)
#  Set VIBE_VERBOSE=1 (or VIBE_DEBUG=1) to see method-attachment logs.
#  All code and comments are English. No emojis.
# ============================================
import os

_VERBOSE = (os.getenv("VIBE_VERBOSE") == "1"
            or os.getenv("VIBE_DEBUG") == "1")


def info(msg):
    if _VERBOSE:
        print(msg)
