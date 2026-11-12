# ============================================
#  userapi/chatlists.py - Vibe chatlists API (chat folder contents)
#  Wraps all functions.chatlists.* TL requests.
#  All code and comments are English. No emojis.
# ============================================
from telethon.tl import functions as tl_functions
from userapi._tl_auto import bind as _bind


class ChatlistsMixin:
    """Hand-written convenience methods for chatlists."""

    async def get_chatlist_chats(self, chatlist, limit=20, **kwargs):
        """Fetch chats inside a chatlist (folder)."""
        from telethon.tl.functions.chatlists import GetChatlistChatsRequest
        self._require_client()
        return await self._client(GetChatlistChatsRequest(
            chatlist=chatlist, limit=limit, **kwargs,
        ))


def bind_to(client_cls):
    new, skipped = _bind(
        client_cls, tl_functions.chatlists, "Chatlists",
        ChatlistsMixin(),
    )
    return new, skipped


print("[chatlists] module loaded; call bind_to(VibeClient) to attach methods")
