# ============================================
#  userapi/messages.py - Vibe messages API
#  Wraps all 260 functions.messages.* TL requests plus hand-written
#  convenience methods for common tasks.
#  All code and comments are English. No emojis.
# ============================================
import inspect
import re

from telethon.tl import functions as tl_functions
from userapi._log import info as _vlog


# Names that are base classes or helpers, not real TL requests.
_SKIP = frozenset({"TLRequest", "TLObject", "List", "Optional"})


def _snake(name):
    """SearchRequest -> search; GetFullChatRequest -> get_full_chat."""
    n = name[:-7] if name.endswith("Request") else name
    return re.sub(r"(?<!^)(?=[A-Z])", "_", n).lower()


def _make_async_wrapper(tl_name, tl_cls):
    _tl_has_hash = False
    try:
        _sig = inspect.signature(tl_cls.__init__)
        if "hash" in _sig.parameters:
            _tl_has_hash = True
    except (ValueError, TypeError):
        pass
    async def wrapper(self, *args, **kwargs):
        self._require_client()
        if _tl_has_hash and not args and "hash" not in kwargs:
            kwargs["hash"] = 0
        return await self._client(tl_cls(*args, **kwargs))
    wrapper.__name__ = _snake(tl_name)
    wrapper.__qualname__ = f"Messages.{wrapper.__name__}"
    doc = f"Messages: {tl_name}. Wraps functions.messages.{tl_name}."
    try:
        sig = inspect.signature(tl_cls.__init__)
        params = [p for n, p in sig.parameters.items() if n != "self"]
        if params:
            doc += "\n\nSignature: " + str(sig).replace("(self, ", "(").replace("(self)", "()")
    except (ValueError, TypeError):
        pass
    wrapper.__doc__ = doc
    return wrapper


def _collect_messages_methods():
    methods = {}
    for name in dir(tl_functions.messages):
        if name.startswith("_") or not name.endswith("Request"):
            continue
        if name in _SKIP:
            continue
        cls = getattr(tl_functions.messages, name, None)
        if not isinstance(cls, type):
            continue
        if not hasattr(cls, "CONSTRUCTOR_ID"):
            continue
        methods[_snake(name)] = _make_async_wrapper(name, cls)
    return methods


class MessagesMixin:
    """Hand-written convenience methods for common message tasks."""

    # -- send (additional shortcuts not already on VibeClient) --
    async def send_media(self, peer, media, caption=None, **kwargs):
        """Send pre-uploaded media (InputMedia). For local files use send_file.

        Returns the created Message (extracted from the Updates response).
        """
        import os
        from telethon.tl.functions.messages import SendMediaRequest
        from telethon.tl.types import UpdateNewMessage, UpdateNewChannelMessage
        self._require_client()
        entity = await self._client.get_input_entity(peer)
        random_id = kwargs.pop("random_id", None)
        if random_id is None or random_id == 0:
            random_id = int.from_bytes(os.urandom(8), "big", signed=True)
        result = await self._client(SendMediaRequest(
            peer=entity, media=media,
            message=caption or "",
            random_id=random_id, **kwargs,
        ))
        # Normalize to Message when possible
        if hasattr(result, "updates"):
            for u in result.updates:
                if isinstance(u, (UpdateNewMessage, UpdateNewChannelMessage)):
                    return u.message
        # Scheduled / short-sent responses
        from telethon.tl.types import UpdateShortSentMessage
        if isinstance(result, UpdateShortSentMessage):
            return result
        return result

    # -- history --
    async def get_history(self, peer, limit=20, **kwargs):
        """Fetch message history with full control (offset_id, max_id, etc.)."""
        from telethon.tl.functions.messages import GetHistoryRequest
        self._require_client()
        entity = await self._client.get_input_entity(peer)
        result = await self._client(GetHistoryRequest(
            peer=entity, offset_id=kwargs.pop("offset_id", 0),
            offset_date=kwargs.pop("offset_date", None),
            add_offset=kwargs.pop("add_offset", 0),
            limit=limit, max_id=kwargs.pop("max_id", 0),
            min_id=kwargs.pop("min_id", 0), hash=0,
        ))
        return result.messages

    # -- read state --
    async def read_history(self, peer, max_id=0):
        """Mark entire chat as read up to max_id."""
        from telethon.tl.functions.messages import ReadHistoryRequest
        self._require_client()
        entity = await self._client.get_input_entity(peer)
        return await self._client(ReadHistoryRequest(peer=entity, max_id=max_id))

    async def read_mentions(self, peer, max_id=0):
        """Mark mentions in a chat as read."""
        from telethon.tl.functions.messages import ReadMentionsRequest
        self._require_client()
        entity = await self._client.get_input_entity(peer)
        return await self._client(ReadMentionsRequest(peer=entity, top_msg_id=max_id))

    # -- mute / archive --
    async def mute_chat(self, peer, mute_until=None):
        """Mute chat notifications.

        `mute_until`: datetime (until when) or None (forever).
        `mute_until=datetime.now()` (past) means unmute.
        """
        from telethon.tl.functions.account import UpdateNotifySettingsRequest
        from telethon.tl.types import InputNotifyPeer, InputPeerNotifySettings
        import datetime as _dt
        self._require_client()
        entity = await self._client.get_input_entity(peer)
        if mute_until is None:
            mute_until = _dt.datetime(2038, 1, 1, tzinfo=_dt.timezone.utc)
        settings = InputPeerNotifySettings(
            show_previews=False, silent=True, mute_until=mute_until,
        )
        return await self._client(UpdateNotifySettingsRequest(
            peer=InputNotifyPeer(peer=entity), settings=settings,
        ))

    async def unmute_chat(self, peer):
        """Unmute chat notifications."""
        from telethon.tl.functions.account import UpdateNotifySettingsRequest
        from telethon.tl.types import InputNotifyPeer, InputPeerNotifySettings
        import datetime as _dt
        self._require_client()
        entity = await self._client.get_input_entity(peer)
        settings = InputPeerNotifySettings(
            show_previews=True,
            silent=False,
            mute_until=_dt.datetime(2000, 1, 1, tzinfo=_dt.timezone.utc),
        )
        return await self._client(UpdateNotifySettingsRequest(
            peer=InputNotifyPeer(peer=entity), settings=settings,
        ))

    async def archive_chat(self, peer):
        """Archive a chat."""
        from telethon.tl.functions.folders import EditPeerFoldersRequest
        from telethon.tl.types import InputFolderPeer
        self._require_client()
        entity = await self._client.get_input_entity(peer)
        return await self._client(EditPeerFoldersRequest(
            folder_peers=[InputFolderPeer(peer=entity, folder_id=1)],
        ))

    async def unarchive_chat(self, peer):
        """Unarchive a chat."""
        from telethon.tl.functions.folders import EditPeerFoldersRequest
        from telethon.tl.types import InputFolderPeer
        self._require_client()
        entity = await self._client.get_input_entity(peer)
        return await self._client(EditPeerFoldersRequest(
            folder_peers=[InputFolderPeer(peer=entity, folder_id=0)],
        ))

    # -- search --
    async def search_peers(self, query, limit=20):
        """Search users/chats by name or username (global peer search).

        Returns a `Found` object with `results`, `my_results`, `chats`, `users`.
        """
        from telethon.tl.functions.contacts import SearchRequest
        self._require_client()
        return await self._client(SearchRequest(q=query, limit=limit))

    # Backwards-compatible alias
    async def search_global(self, query, limit=20):
        """Deprecated alias for search_peers. Returns Found, not messages."""
        return await self.search_peers(query, limit=limit)

    async def search_messages(self, peer, query, limit=20, offset_id=0,
                              message_filter=None, **kwargs):
        """Search messages inside a specific chat.

        `message_filter` may be any InputMessagesFilter* instance; when
        None, InputMessagesFilterEmpty is used (text search, no filter).
        """
        from telethon.tl.functions.messages import SearchRequest
        from telethon.tl.types import InputMessagesFilterEmpty
        self._require_client()
        entity = await self._client.get_input_entity(peer)
        if message_filter is None:
            message_filter = InputMessagesFilterEmpty()
        result = await self._client(SearchRequest(
            peer=entity,
            q=query,
            filter=message_filter,
            min_date=None,
            max_date=None,
            offset_id=offset_id,
            add_offset=0,
            limit=limit,
            max_id=0,
            min_id=0,
            hash=0,
            from_id=None,
            top_msg_id=None,
        ))
        return result.messages


# ---------- attach everything ----------
def bind_to(client_cls):
    """Attach auto-generated + hand-written messages methods to VibeClient."""
    for name, fn in MessagesMixin.__dict__.items():
        if name.startswith("__") or name.startswith("_"):
            continue
        if not callable(fn):
            continue
        setattr(client_cls, name, fn)
    generated = _collect_messages_methods()
    count_new, count_skipped = 0, 0
    for name, fn in generated.items():
        if hasattr(client_cls, name):
            count_skipped += 1
            continue
        setattr(client_cls, name, fn)
        count_new += 1
    return count_new, count_skipped


_vlog("[messages] module loaded; call bind_to(VibeClient) to attach methods")
