# ============================================
#  userapi/exceptions.py - Custom Exceptions
#  All code and comments are English. No emojis.
# ============================================

class VibeError(Exception):
    """Base exception for all Vibe-related errors."""
    pass

class VibePremiumRequired(VibeError):
    """Raised when a feature requires a Premium account."""
    pass

class VibeRateLimit(VibeError):
    """Raised when the user is being rate-limited."""
    pass

class VibeButtonInvalid(VibeError):
    """Raised when the server rejects inline buttons."""
    pass

class VibeMediaForbidden(VibeError):
    """Raised when sending media is forbidden."""
    pass
