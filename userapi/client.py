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
        # Telethon appends .session itself; store the base path only.
        base = Path(session_path) if session_path else Path.home() / ".vibe_session"
        if base.suffix in (".session", ".json"):
            base = base.with_suffix("")
        self._session_path = base
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
            str(self._session_path),
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

    # ---- extended message methods (raw TL) ----
    async def get_replies(self, peer, msg_id, limit=20):
        """Fetch replies to a message (forum topic or comment section)."""
        from telethon.tl.functions.messages import GetRepliesRequest
        self._require_client()
        peer_entity = await self._client.get_input_entity(peer)
        result = await self._client(GetRepliesRequest(
            peer=peer_entity,
            msg_id=msg_id,
            offset_id=0,
            offset_date=None,
            add_offset=0,
            limit=limit,
            max_id=0,
            min_id=0,
            hash=0,
        ))
        return result.messages

    async def send_reaction(self, peer, msg_id, emoticon=None,
                            custom_document_id=None, big=False):
        """Send or clear a reaction.

        Args:
            peer: chat / channel / user
            msg_id: target message id
            emoticon: unicode emoji, e.g. "👍". None clears all reactions.
            custom_document_id: premium custom emoji document id (overrides emoticon).
            big: render as large animation.
        """
        from telethon.tl.functions.messages import SendReactionRequest
        from telethon.tl.types import ReactionEmoji, ReactionCustomEmoji
        self._require_client()
        peer_entity = await self._client.get_input_entity(peer)
        if custom_document_id is not None:
            reaction = [ReactionCustomEmoji(document_id=custom_document_id)]
        elif emoticon is not None:
            reaction = [ReactionEmoji(emoticon=emoticon)]
        else:
            reaction = None  # clears
        return await self._client(SendReactionRequest(
            peer=peer_entity,
            msg_id=msg_id,
            big=True if big else None,
            add_to_recent=True,
            reaction=reaction,
        ))

    async def get_pinned_message(self, peer):
        """Return the pinned message in a chat, or None."""
        from telethon.tl.types import InputMessagesFilterPinned
        self._require_client()
        msgs = await self._client.get_messages(
            peer, limit=1, filter=InputMessagesFilterPinned,
        )
        return msgs[0] if msgs else None

    # ---- message management ----
    async def edit_message(self, peer, msg_id, text=None, **kwargs):
        """Edit an outgoing message. Returns the updated Message."""
        self._require_client()
        return await self._client.edit_message(peer, msg_id, text, **kwargs)

    async def delete_messages(self, peer, msg_ids, revoke=True):
        """Delete messages. `revoke=True` removes for everyone."""
        self._require_client()
        return await self._client.delete_messages(peer, msg_ids, revoke=revoke)

    async def forward_messages(self, to_peer, msg_ids, from_peer=None):
        """Forward messages to another chat. Returns list of new Messages."""
        self._require_client()
        return await self._client.forward_messages(
            to_peer, msg_ids, from_peer=from_peer,
        )

    async def pin_message(self, peer, msg_id=None, notify=False):
        """Pin a message in a chat. msg_id=None unpins the current pinned."""
        self._require_client()
        return await self._client.pin_message(peer, msg_id, notify=notify)

    async def unpin_message(self, peer, msg_id=None):
        """Unpin a message. msg_id=None removes the pinned message."""
        self._require_client()
        return await self._client.unpin_message(peer, msg_id)

    async def send_read_acknowledge(self, peer, msg_id=None):
        """Mark a chat (or a specific message) as read. Returns bool."""
        self._require_client()
        return await self._client.send_read_acknowledge(peer, msg_id)

    def action(self, peer, action="typing", **kwargs):
        """Typing/uploading indicator as async context manager.

        Usage:
            async with client.action(peer, "typing"):
                await asyncio.sleep(2)
        """
        self._require_client()
        return self._client.action(peer, action, **kwargs)

    # ---- transparent passthrough to Telethon ----
    # Any attribute not defined on VibeClient (or not a dunder / private
    # internal) is forwarded to the underlying TelegramClient. This makes
    # the entire Telethon API available directly, e.g.:
    #     await client.send_file("me", "photo.jpg")
    #     await client.get_entity("@somechannel")
    #     await client.delete_messages(peer, [msg_id])
    _INTERNAL_ATTRS = frozenset({
        "_client", "_connected", "_session_path", "_proxy",
        "_dc_host", "_dc_port", "_INTERNAL_ATTRS",
    })

    def __getattr__(self, name):
        # Only called when normal lookup fails.
        if name.startswith("__") and name.endswith("__"):
            raise AttributeError(name)
        if name in VibeClient._INTERNAL_ATTRS:
            raise AttributeError(name)

        client = self.__dict__.get("_client")

        if client is not None:
            try:
                return getattr(client, name)
            except AttributeError:
                raise AttributeError(
                    f"{type(self).__name__!r} object has no attribute {name!r}"
                ) from None

        # Not connected yet. Distinguish "exists on Telethon, needs connection"
        # from "does not exist at all" so that hasattr() works correctly.
        try:
            from telethon import TelegramClient
            getattr(TelegramClient, name)
        except AttributeError:
            raise AttributeError(
                f"{type(self).__name__!r} object has no attribute {name!r}"
            ) from None

        raise AttributeError(
            f"attribute {name!r} requires an active connection: call connect() first"
        )

    def _require_client(self):
        if self._client is None or not self._connected:
            raise RuntimeError("call connect() first")


async def _maybe_await(value):
    if asyncio.iscoroutine(value):
        return await value
    return value
