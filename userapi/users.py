# ============================================
#  userapi/users.py - Vibe users API
#  Wraps all functions.users.* TL requests plus convenience methods.
#  All code and comments are English. No emojis.
# ============================================
from telethon.tl import functions as tl_functions
from userapi._tl_auto import bind as _bind, collect as _collect


class UsersMixin:
    """Hand-written convenience methods for users."""

    async def get_full_user(self, user):
        """Fetch full user info (bio, common chats count, etc.)."""
        from telethon.tl.functions.users import GetFullUserRequest
        self._require_client()
        entity = await self._client.get_input_entity(user)
        return await self._client(GetFullUserRequest(id=entity))

    async def get_users(self, users):
        """Resolve a list of users/ids in one call."""
        from telethon.tl.functions.users import GetUsersRequest
        self._require_client()
        if not isinstance(users, (list, tuple)):
            users = [users]
        inputs = [await self._client.get_input_entity(u) for u in users]
        return await self._client(GetUsersRequest(id=inputs))


def bind_to(client_cls):
    new, skipped = _bind(
        client_cls, tl_functions.users, "Users", UsersMixin(),
    )
    return new, skipped


print("[users] module loaded; call bind_to(VibeClient) to attach methods")
