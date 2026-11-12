# ============================================
#  userapi/channels.py - Vibe channels API
#  Wraps all functions.channels.* TL requests + convenience methods.
#  Uses channel_fix: `channel=` / `peer=` are auto-converted to InputChannel.
#  All code and comments are English. No emojis.
# ============================================
from telethon.tl import functions as tl_functions
from userapi._tl_auto import bind as _bind


class ChannelsMixin:
    """Hand-written convenience methods for channels/supergroups."""

    async def create_channel(self, title, about="", megagroup=False,
                             broadcast=False, ttl_period=None):
        """Create a new channel or supergroup."""
        from telethon.tl.functions.channels import CreateChannelRequest
        self._require_client()
        return await self._client(CreateChannelRequest(
            title=title, about=about,
            megagroup=megagroup, broadcast=broadcast,
            ttl_period=ttl_period,
        ))

    async def get_full_channel(self, channel):
        """Fetch full channel info (members count, about, etc.)."""
        from telethon.tl.functions.channels import GetFullChannelRequest
        from userapi._tl_auto import _ensure_input_channel
        self._require_client()
        ch = await _ensure_input_channel(self._client, channel)
        return await self._client(GetFullChannelRequest(channel=ch))

    async def get_channel_participants(self, channel, limit=20, **kwargs):
        """List channel/supergroup participants (list, not iterator)."""
        self._require_client()
        return await self.get_participants(channel, limit=limit, **kwargs)

    async def edit_channel_title(self, channel, title):
        """Rename a channel/supergroup."""
        from telethon.tl.functions.channels import EditTitleRequest
        from userapi._tl_auto import _ensure_input_channel
        self._require_client()
        ch = await _ensure_input_channel(self._client, channel)
        return await self._client(EditTitleRequest(channel=ch, title=title))

    async def edit_channel_about(self, channel, about):
        """Change channel description."""
        from telethon.tl.functions.messages import EditChatAboutRequest
        from telethon.tl.types import InputPeerChannel
        from userapi._tl_auto import _ensure_input_channel
        self._require_client()
        ch = await _ensure_input_channel(self._client, channel)
        peer = InputPeerChannel(channel_id=ch.channel_id, access_hash=ch.access_hash)
        return await self._client(EditChatAboutRequest(peer=peer, about=about))

    async def delete_channel(self, channel):
        """Delete a channel/supergroup (must be creator)."""
        from telethon.tl.functions.channels import DeleteChannelRequest
        from userapi._tl_auto import _ensure_input_channel
        self._require_client()
        ch = await _ensure_input_channel(self._client, channel)
        return await self._client(DeleteChannelRequest(channel=ch))

    async def toggle_signatures(self, channel, enabled):
        """Enable/disable signatures on channel posts."""
        from telethon.tl.functions.channels import ToggleSignaturesRequest
        from userapi._tl_auto import _ensure_input_channel
        self._require_client()
        ch = await _ensure_input_channel(self._client, channel)
        return await self._client(ToggleSignaturesRequest(channel=ch, enabled=enabled))


def bind_to(client_cls):
    new, skipped = _bind(
        client_cls, tl_functions.channels, "Channels",
        ChannelsMixin(), channel_fix=True,
    )
    return new, skipped


print("[channels] module loaded; call bind_to(VibeClient) to attach methods")
