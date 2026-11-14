# ============================================
#  botapi/__init__.py - Bot API package exports
# ============================================
from botapi.client import VibeBot
from botapi.http_client import VibeBotHTTP, VibeBotAPIError
from botapi import http_methods  # noqa: F401  (attaches methods to VibeBotHTTP)
from botapi.keyboards import InlineKeyboard, ReplyKeyboard

__all__ = [
    "VibeBot",
    "VibeBotHTTP",
    "VibeBotAPIError",
    "InlineKeyboard",
    "ReplyKeyboard",
]
