# ============================================
#  userapi/client.py - Vibe Messenger client
#  Supports SOCKS5/HTTP proxy for IP bypass.
#  All code and comments are English. No emojis.
# ============================================
import asyncio
from pathlib import Path

from telethon import TelegramClient

from userapi.connection.telethon_ws import (
    ConnectionWebSocketAbridgedObfuscated,
    set_proxy as _set_ws_proxy,
    _coerce_proxy,
)
from userapi.connection.vibe_keys import load_all_keys
from userapi.session import Session


API_ID = 4
API_HASH = "014b35b6184100b085b0d0572f9b5103"
DEFAULT_DC_HOST = "web.vibegram.chat"
DEFAULT_DC_PORT = 443


class VibeClient:
    """High-level client for Vibe Messenger.

    Args:
        proxy: optional, URL string ('socks5://127.0.0.1:9050')
               or Telethon tuple/dict. Routed through the WebSocket.
    """

    def __init__(self, session_path=None, dc_host=DEFAULT_DC_HOST,
                 dc_port=DEFAULT_DC_PORT, proxy=None):
        self._session = Session(session_path or Path.home() / ".vibe_session.json")
        self._dc_host = dc_host
        self._dc_port = dc_port
        self._proxy = _coerce_proxy(proxy)
        self._client = None
        self._connected = False

    async def connect(self, timeout=20):
        """Open connection to Vibe DC. Loads RSA keys first."""
        load_all_keys()
        if self._proxy:
            _set_ws_proxy(self._proxy)
            print(f"[client] proxy set: {self._proxy}")
        else:
            _set_ws_proxy(None)
        self._client = TelegramClient(
            self._session.path.with_suffix(""),
            API_ID,
            API_HASH,
            connection=ConnectionWebSocketAbridgedObfuscated,
        )
        self._client.session.set_dc(2, self._dc_host, self._dc_port)
        await asyncio.wait_for(self._client.connect(), timeout=timeout)
        self._connected = self._client.is_connected()
        return self._connected

    async def login(self, phone, code_callback=None, password_callback=None):
        if not self._connected:
            raise RuntimeError("call connect() first")
        await self._client.send_code_request(phone)
        if code_callback is None:
            code = input("Enter the code you received: ").strip()
        else:
            code = await _maybe_await(code_callback())
        try:
            await self._client.sign_in(phone=phone, code=code)
        except Exception as e:
            if "password" in str(e).lower() and password_callback is not None:
                pw = await _maybe_await(password_callback())
                await self._client.sign_in(password=pw)
            else:
                raise
        return await self.get_me()

    async def get_me(self):
        return await self._client.get_me()

    async def send_message(self, peer, text):
        return await self._client.send_message(peer, text)

    async def get_dialogs(self, limit=20):
        return await self._client.get_dialogs(limit=limit)

    async def disconnect(self):
        self._connected = False
        if self._client is not None:
            try:
                await self._client.disconnect()
            except Exception as e:
                print(f"[client] error: {e}")
            self._client = None


async def _maybe_await(value):
    if asyncio.iscoroutine(value):
        return await value
    return value
