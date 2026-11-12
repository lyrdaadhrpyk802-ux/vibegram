# ============================================
#  botapi/client.py - Vibe Bot Client
#  All code and comments are English. No emojis.
# ============================================
import asyncio
import re
from pathlib import Path
from userapi.client import VibeClient
from botapi.methods import BotMethodsMixin

class VibeBot(VibeClient, BotMethodsMixin):
    """A specialized client for Vibe Bots using MTProto."""
    
    def __init__(self, token, session_path=None):
        if session_path is None:
            bot_id = token.split(":")[0] if ":" in token else "bot"
            session_path = Path.home() / f".vibe_bot_{bot_id}"
            
        super().__init__(session_path=session_path)
        self._token = token
        self._user_id = None

    async def connect(self, timeout=60):
        """Connects and logs in as a bot using the token."""
        connected = await super().connect(timeout=timeout)
        if not connected:
            return False

        if not await self.is_authorized():
            try:
                await self.raw.sign_in(bot_token=self._token)
            except Exception as e:
                await self.disconnect()
                raise RuntimeError(f"Bot login failed: {e}")

        me = await self.get_me()
        self._user_id = me.id
        return True

    def command(self, name):
        """Decorator to register a handler for a specific command."""
        from telethon import events
        pattern = re.compile(rf"^/{name}(?:@\w+)?(?:\s|$)", re.IGNORECASE)
        def decorator(func):
            async def wrapper(event):
                await func(event)
            event = events.NewMessage(incoming=True, pattern=pattern)
            self.raw.add_event_handler(wrapper, event)
            return func
        return decorator
