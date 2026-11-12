# ============================================
#  userapi/folders.py - Vibe folders API (chat folders)
#  Wraps all functions.folders.* TL requests.
#  All code and comments are English. No emojis.
# ============================================
from telethon.tl import functions as tl_functions
from userapi._tl_auto import bind as _bind


class FoldersMixin:
    """Hand-written convenience methods for folders."""

    async def get_folders(self):
        """List all chat folders."""
        from telethon.tl.functions.messages import GetDialogFiltersRequest
        self._require_client()
        try:
            r = await self._client(GetDialogFiltersRequest())
            return getattr(r, "filters", [])
        except Exception:
            return []

    async def create_folder(self, title, peer_ids=None):
        """Create or update a chat folder with the given peers."""
        from telethon.tl.functions.messages import UpdateDialogFilterRequest
        from telethon.tl.types import DialogFilter
        self._require_client()
        peers = []
        if peer_ids:
            for pid in peer_ids:
                peers.append(await self._client.get_input_entity(pid))
        filt = DialogFilter(
            id=2, title=title, pinned_peers=peers, include_peers=peers,
        )
        return await self._client(UpdateDialogFilterRequest(filter_id=2, filter=filt))


def bind_to(client_cls):
    new, skipped = _bind(
        client_cls, tl_functions.folders, "Folders",
        FoldersMixin(),
    )
    return new, skipped


print("[folders] module loaded; call bind_to(VibeClient) to attach methods")
