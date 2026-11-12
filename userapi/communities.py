# ============================================
#  userapi/communities.py - Vibe communities API
#  Wraps all functions.communities.* TL requests.
#  All code and comments are English. No emojis.
# ============================================
from telethon.tl import functions as tl_functions
from userapi._tl_auto import bind as _bind


class CommunitiesMixin:
    """Hand-written convenience methods for communities."""

    async def get_communities(self, limit=20, **kwargs):
        """List joined communities."""
        from telethon.tl.functions.communities import GetJoinedCommunitiesRequest
        self._require_client()
        try:
            return await self._client(GetJoinedCommunitiesRequest(
                offset=0, limit=limit, **kwargs,
            ))
        except Exception:
            return None


def bind_to(client_cls):
    new, skipped = _bind(
        client_cls, tl_functions.communities, "Communities",
        CommunitiesMixin(),
    )
    return new, skipped


print("[communities] module loaded; call bind_to(VibeClient) to attach methods")
