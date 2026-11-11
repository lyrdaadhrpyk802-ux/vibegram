# ============================================
#  userapi/client.py - Vibe Messenger client
#  High-level wrapper over Telethon with Vibe custom auth.
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

    Usage:
        client = VibeClient()
        await client.connect()
        if not await client.is_authorized():
            await client.request_code(phone)
            await client.sign_in(phone, code)
        me = await client.get_me()
        await client.send_message("me", "hello")
        await client.disconnect()
    """

    def __init__(self, session_path=None, dc_host=DEFAULT_DC_HOST,
                 dc_port=DEFAULT_DC_PORT, proxy=None):
        self._session = Session(session_path or Path.home() / ".vibe_session.json")
        self._dc_host = dc_host
        self._dc_port = dc_port
        self._proxy = _coerce_proxy(proxy)
        self._client = None
        self._connected = False

    # ---- lifecycle ----
    async def connect(self, timeout=20):
        load_all_keys()
        if self._proxy:
            _set_ws_proxy(self._proxy)
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

    async def disconnect(self):
        self._connected = False
        if self._client is not None:
            try:
                await self._client.disconnect()
            except Exception:
                pass
            self._client = None

    # ---- auth ----
    async def is_authorized(self):
        self._require_client()
        return await self._client.is_user_authorized()

    async def request_code(self, phone):
        self._require_client()
        return await self._client.send_code_request(phone)

    async def sign_in(self, phone, code, password=None):
        self._require_client()
        try:
            return await self._client.sign_in(phone=phone, code=code)
        except Exception as e:
            if password is not None and "password" in str(e).lower():
                return await self._client.sign_in(password=password)
            raise

    async def log_out(self):
        self._require_client()
        return await self._client.log_out()

    # ---- account ----
    async def get_me(self):
        self._require_client()
        return await self._client.get_me()

    # ---- messaging ----
    async def send_message(self, peer, text, **kwargs):
        self._require_client()
        return await self._client.send_message(peer, text, **kwargs)

    async def get_messages(self, peer, limit=20):
        self._require_client()
        return await self._client.get_messages(peer, limit=limit)

    async def get_dialogs(self, limit=20):
        self._require_client()
        return await self._client.get_dialogs(limit=limit)

    async def iter_messages(self, peer, limit=None):
        self._require_client()
        async for msg in self._client.iter_messages(peer, limit=limit):
            yield msg

    # ---- escape hatch ----
    @property
    def raw(self):
        """Underlying Telethon TelegramClient for advanced usage."""
        self._require_client()
        return self._client

    # ---- transparent passthrough to Telethon ----
    # Any attribute not defined on VibeClient (or not a dunder / private
    # internal) is forwarded to the underlying TelegramClient. This makes
    # the entire Telethon API available directly, e.g.:
    #     await client.send_file("me", "photo.jpg")
    #     await client.get_entity("@somechannel")
    #     await client.delete_messages(peer, [msg_id])
    _INTERNAL_ATTRS = frozenset({
        "_client", "_connected", "_session", "_proxy",
        "_dc_host", "_dc_port", "_INTERNAL_ATTRS",
    })

    def __getattr__(self, name):
        # Only called when normal lookup fails.
        if name.startswith("__") and name.endswith("__"):
            raise AttributeError(name)
        if name in VibeClient._INTERNAL_ATTRS:
            raise AttributeError(name)

        client = self.__dict__.get("_client")
        if client is None:
            raise RuntimeError(
                f"attribute {name!r} unavailable: call connect() first"
            )

        try:
            return getattr(client, name)
        except AttributeError:
            raise AttributeError(
                f"{type(self).__name__!r} object has no attribute {name!r}"
            ) from None

    def _require_client(self):
        if self._client is None or not self._connected:
            raise RuntimeError("call connect() first")


async def _maybe_await(value):
    if asyncio.iscoroutine(value):
        return await value
    return value
