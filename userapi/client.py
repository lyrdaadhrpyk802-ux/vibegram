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

    def disconnect(self):
        # Telethon's disconnect() is sync but returns a coroutine that must
        # be awaited. Keep the same signature for API parity.
        async def _do():
            self._connected = False
            if self._client is not None:
                try:
                    await self._client.disconnect()
                except Exception:
                    pass
                self._client = None
        return _do()

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

        NOTE: on Vibe, reactions require a premium account; a
        PremiumAccountRequiredError is raised otherwise (Telegram does not
        require premium for reactions). Callers should catch it and inform
        the user.

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

    # ---- files and media ----
    async def send_file(self, peer, file, caption=None, **kwargs):
        """Send photo/video/document/voice.

        `file` may be a path, bytes, file-like, or URL. Any extra keyword
        args are forwarded to Telethon (force_document, voice_note,
        video_note, supports_streaming, reply_to, progress_callback, ...).
        Returns the new Message.
        """
        self._require_client()
        return await self._client.send_file(
            peer, file, caption=caption, **kwargs,
        )

    async def download_media(self, message, file=None, **kwargs):
        """Download media attached to a Message.

        `file` may be a path, file-like, or None (auto name). Returns the
        path or bytes. Extra kwargs (thumb, progress_callback) forwarded.
        """
        self._require_client()
        return await self._client.download_media(
            message, file=file, **kwargs,
        )

    async def download_file(self, input_location, file=None, **kwargs):
        """Download raw file by InputFileLocation (advanced). Returns bytes
        when `file` is None, otherwise writes to it."""
        self._require_client()
        return await self._client.download_file(
            input_location, file=file, **kwargs,
        )

    async def upload_file(self, file, **kwargs):
        """Upload a file and return its InputFile handle (for reuse in
        send_file or raw TL calls)."""
        self._require_client()
        return await self._client.upload_file(file, **kwargs)

    # ---- peer / entity ----
    async def get_entity(self, entity):
        """Resolve a peer. Accepts id, username (@name), phone, or URL.
        Returns User, Chat, or Channel (or a list if `entity` is a list)."""
        self._require_client()
        return await self._client.get_entity(entity)

    async def get_input_entity(self, peer):
        """Return the InputPeer for a peer (needed by raw TL calls)."""
        self._require_client()
        return await self._client.get_input_entity(peer)

    async def get_peer_id(self, peer, add_mark=True):
        """Return the numeric id of a peer.
        `add_mark=True` returns marked id (works with get_entity/get_messages)."""
        self._require_client()
        return await self._client.get_peer_id(peer, add_mark=add_mark)

    async def resolve_username(self, username):
        """Resolve '@name' or 'name' or a t.me URL to a full entity."""
        self._require_client()
        name = username.lstrip("@")
        if "t.me/" in name or "telegram.me/" in name:
            name = name.rsplit("/", 1)[-1]
        return await self._client.get_entity(name)

    # ---- groups and channels ----
    async def get_participants(self, entity, limit=None, **kwargs):
        """List participants of a chat/channel as a list."""
        self._require_client()
        return await self._client.get_participants(entity, limit=limit, **kwargs)

    def iter_participants(self, entity, limit=None, **kwargs):
        """Async iterator over participants (returns AsyncIterator, not a
        coroutine). Use: async for u in client.iter_participants(...): ..."""
        self._require_client()
        return self._client.iter_participants(entity, limit=limit, **kwargs)

    async def kick_participant(self, entity, user):
        """Remove a user from a group/channel."""
        self._require_client()
        return await self._client.kick_participant(entity, user)

    async def edit_admin(self, entity, user, **kwargs):
        """Grant/revoke admin rights. Keywords: is_admin=True/False, plus
        admin-specific flags (change_info, post_messages, ...)."""
        self._require_client()
        return await self._client.edit_admin(entity, user, **kwargs)

    async def edit_permissions(self, entity, user=None, until_date=None, **kwargs):
        """Edit a user's permissions (default: silent). Pass view_messages
        and related booleans to override."""
        self._require_client()
        return await self._client.edit_permissions(
            entity, user, until_date=until_date, **kwargs,
        )

    async def _to_input_channel(self, peer):
        """Convert any peer to InputChannel (required by channels.* methods)."""
        from telethon.tl.types import InputChannel, InputPeerChannel
        ent = await self._client.get_input_entity(peer)
        if isinstance(ent, InputPeerChannel):
            return InputChannel(
                channel_id=ent.channel_id,
                access_hash=ent.access_hash,
            )
        return ent

    async def join_channel(self, channel):
        """Join a channel/supergroup by id, username, or invite link."""
        from telethon.tl.functions.channels import JoinChannelRequest
        self._require_client()
        input_channel = await self._to_input_channel(channel)
        return await self._client(JoinChannelRequest(input_channel))

    async def leave_channel(self, channel):
        """Leave a channel/supergroup."""
        from telethon.tl.functions.channels import LeaveChannelRequest
        self._require_client()
        input_channel = await self._to_input_channel(channel)
        return await self._client(LeaveChannelRequest(input_channel))

    # ---- profile photos ----
    async def get_profile_photos(self, entity, limit=None, offset=0, max_id=0):
        """List a user's/channel's profile photos."""
        self._require_client()
        return await self._client.get_profile_photos(
            entity, limit=limit, offset=offset, max_id=max_id,
        )

    def iter_profile_photos(self, entity, limit=None, offset=0, max_id=0):
        """Async iterator over profile photos (use: async for ...)."""
        self._require_client()
        return self._client.iter_profile_photos(
            entity, limit=limit, offset=offset, max_id=max_id,
        )

    async def download_profile_photo(self, entity, file=None, download_big=True):
        """Download profile photo. Returns path or None if no photo."""
        self._require_client()
        return await self._client.download_profile_photo(
            entity, file=file, download_big=download_big,
        )

    # ---- dialogs (extended) ----
    def iter_dialogs(self, limit=None, **kwargs):
        """Async iterator over dialogs (use: async for d in ...)."""
        self._require_client()
        return self._client.iter_dialogs(limit=limit, **kwargs)

    async def get_drafts(self, entity=None):
        """Return drafts (all or for a specific chat)."""
        self._require_client()
        return await self._client.get_drafts(entity)

    def iter_drafts(self, entity=None):
        """Async iterator over drafts."""
        self._require_client()
        return self._client.iter_drafts(entity)

    async def delete_dialog(self, entity, revoke=False):
        """Delete a chat from the dialog list (revoke=True also leaves it)."""
        self._require_client()
        return await self._client.delete_dialog(entity, revoke=revoke)

    # ---- all remaining TelegramClient methods ----
    # Grouped wrappers over the remaining 27 public TelegramClient methods.
    # Sync vs async is matched to Telethon 1.45.0.
    # Aliases are provided for is_user_authorized / send_code_request.

    # -- aliases (existing methods with Telethon names) --
    async def is_user_authorized(self):
        return await self.is_authorized()

    async def send_code_request(self, phone, *args, **kwargs):
        return await self.request_code(phone, *args, **kwargs)

    # -- event handlers --
    def add_event_handler(self, callback, event=None):
        self._require_client()
        return self._client.add_event_handler(callback, event)

    def remove_event_handler(self, callback, event=None):
        self._require_client()
        return self._client.remove_event_handler(callback, event)

    def list_event_handlers(self):
        self._require_client()
        return self._client.list_event_handlers()

    def on(self, event):
        self._require_client()
        return self._client.on(event)

    def run_until_disconnected(self):
        self._require_client()
        return self._client.run_until_disconnected()

    def conversation(self, *args, **kwargs):
        self._require_client()
        return self._client.conversation(*args, **kwargs)

    # -- updates / sync --
    async def catch_up(self):
        self._require_client()
        return await self._client.catch_up()

    async def set_receive_updates(self, receive_updates):
        self._require_client()
        return await self._client.set_receive_updates(receive_updates)

    # -- auth extras --
    async def qr_login(self):
        self._require_client()
        return await self._client.qr_login()

    async def sign_up(self, *args, **kwargs):
        self._require_client()
        return await self._client.sign_up(*args, **kwargs)

    async def edit_2fa(self, *args, **kwargs):
        self._require_client()
        return await self._client.edit_2fa(*args, **kwargs)

    # -- status --
    def is_connected(self):
        self._require_client()
        return self._client.is_connected()

    async def is_bot(self):
        self._require_client()
        return await self._client.is_bot()

    # -- folders / takeout / stats --
    async def edit_folder(self, *args, **kwargs):
        self._require_client()
        return await self._client.edit_folder(*args, **kwargs)

    def takeout(self, *args, **kwargs):
        self._require_client()
        return self._client.takeout(*args, **kwargs)

    async def end_takeout(self, *args, **kwargs):
        self._require_client()
        return await self._client.end_takeout(*args, **kwargs)

    async def get_stats(self, *args, **kwargs):
        self._require_client()
        return await self._client.get_stats(*args, **kwargs)

    # -- admin log --
    async def get_admin_log(self, *args, **kwargs):
        self._require_client()
        return await self._client.get_admin_log(*args, **kwargs)

    def iter_admin_log(self, *args, **kwargs):
        self._require_client()
        return self._client.iter_admin_log(*args, **kwargs)

    # -- permissions --
    async def get_permissions(self, *args, **kwargs):
        self._require_client()
        return await self._client.get_permissions(*args, **kwargs)

    # -- downloads (iterator) --
    def iter_download(self, *args, **kwargs):
        self._require_client()
        return self._client.iter_download(*args, **kwargs)

    # -- inline / markup --
    async def inline_query(self, *args, **kwargs):
        self._require_client()
        return await self._client.inline_query(*args, **kwargs)

    def build_reply_markup(self, *args, **kwargs):
        self._require_client()
        return self._client.build_reply_markup(*args, **kwargs)

    # -- startup --
    def start(self, *args, **kwargs):
        self._require_client()
        return self._client.start(*args, **kwargs)

    # -- proxy (overrides module-level, affects this instance) --
    def set_proxy(self, proxy):
        self._proxy = _coerce_proxy(proxy)
        _set_ws_proxy(self._proxy)
        if self._client is not None:
            self._client.set_proxy(proxy)

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


# ---- attach account methods ----
from userapi.account import bind_to as _bind_account
_count_new, _count_skipped = _bind_account(VibeClient)
print(f"[account] attached {_count_new} methods ({_count_skipped} already present)")


# ---- attach messages methods ----
from userapi.messages import bind_to as _bind_messages
_m_new, _m_skipped = _bind_messages(VibeClient)
print(f"[messages] attached {_m_new} methods ({_m_skipped} already present)")


# ---- attach contacts methods ----
from userapi.contacts import bind_to as _bind_contacts
_c_new, _c_skipped = _bind_contacts(VibeClient)
print(f"[contacts] attached {_c_new} methods ({_c_skipped} already present)")


# ---- attach users methods ----
from userapi.users import bind_to as _bind_users
_u_new, _u_skipped = _bind_users(VibeClient)
print(f"[users] attached {_u_new} methods ({_u_skipped} already present)")

# ---- attach photos methods ----
from userapi.photos import bind_to as _bind_photos
_p_new, _p_skipped = _bind_photos(VibeClient)
print(f"[photos] attached {_p_new} methods ({_p_skipped} already present)")


# ---- attach channels methods ----
from userapi.channels import bind_to as _bind_channels
_ch_new, _ch_skipped = _bind_channels(VibeClient)
print(f"[channels] attached {_ch_new} methods ({_ch_skipped} already present)")

# ---- attach chatlists methods ----
from userapi.chatlists import bind_to as _bind_chatlists
_cl_new, _cl_skipped = _bind_chatlists(VibeClient)
print(f"[chatlists] attached {_cl_new} methods ({_cl_skipped} already present)")

# ---- attach communities methods ----
from userapi.communities import bind_to as _bind_communities
_cm_new, _cm_skipped = _bind_communities(VibeClient)
print(f"[communities] attached {_cm_new} methods ({_cm_skipped} already present)")

# ---- attach folders methods ----
from userapi.folders import bind_to as _bind_folders
_f_new, _f_skipped = _bind_folders(VibeClient)
print(f"[folders] attached {_f_new} methods ({_f_skipped} already present)")


# ---- attach extra TL namespaces ----
from userapi.extra import bind_all as _bind_extra
_extra_summary = _bind_extra(VibeClient)
for _ns, _new, _skip, _status in _extra_summary:
    print(f"[extra] {_ns:10s} new={_new:>3d} skipped={_skip:>3d} ({_status})")


async def _maybe_await(value):
    if asyncio.iscoroutine(value):
        return await value
    return value
