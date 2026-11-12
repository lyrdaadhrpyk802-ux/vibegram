# ============================================
#  userapi/account.py - Vibe account API
#  Wraps all 137 functions.account.* TL requests plus hand-written
#  convenience methods for common tasks.
#  All code and comments are English. No emojis.
# ============================================
import inspect
import re

from telethon.tl import functions as tl_functions
from userapi._log import info as _vlog


# ---------- auto-generated wrappers ----------
def _make_async_wrapper(tl_name, tl_cls):
    _tl_has_hash = False
    try:
        _sig = inspect.signature(tl_cls.__init__)
        if "hash" in _sig.parameters:
            _tl_has_hash = True
    except (ValueError, TypeError):
        pass
    """Create an async method that invokes `tl_cls(**kwargs)` via client.raw."""
    async def wrapper(self, *args, **kwargs):
        self._require_client()
        if _tl_has_hash and not args and "hash" not in kwargs:
            kwargs["hash"] = 0
        return await self._client(tl_cls(*args, **kwargs))
    wrapper.__name__ = _snake(tl_name)
    wrapper.__qualname__ = f"Account.{wrapper.__name__}"
    doc = f"Account: {tl_name}. Wraps functions.account.{tl_name}."
    sig = None
    try:
        sig = inspect.signature(tl_cls.__init__)
        params = [p for n, p in sig.parameters.items() if n != "self"]
        if params:
            doc += "\n\nSignature: " + str(sig).replace("(self, ", "(").replace("(self)", "()")
    except (ValueError, TypeError):
        pass
    wrapper.__doc__ = doc
    return wrapper


def _snake(name):
    """UpdateProfileRequest -> update_profile"""
    n = name[:-7] if name.endswith("Request") else name
    s = re.sub(r"(?<!^)(?=[A-Z])", "_", n).lower()
    return s


def _collect_account_methods():
    """Build a dict {method_name: wrapper} for every functions.account request."""
    methods = {}
    for name in dir(tl_functions.account):
        if name.startswith("_") or not name.endswith("Request"):
            continue
        cls = getattr(tl_functions.account, name, None)
        if not isinstance(cls, type):
            continue
        if not hasattr(cls, "CONSTRUCTOR_ID"):
            continue
        method_name = _snake(name)
        methods[method_name] = _make_async_wrapper(name, cls)
    return methods


# ---------- hand-written convenience methods ----------
class AccountMixin:
    """Account-related methods. Mixed into VibeClient."""

    # -- profile --
    async def update_profile(self, first_name=None, last_name=None, about=None):
        """Update first name / last name / bio. Pass None to leave unchanged."""
        self._require_client()
        from telethon.tl.functions.account import UpdateProfileRequest
        return await self._client(UpdateProfileRequest(
            first_name=first_name, last_name=last_name, about=about,
        ))

    async def update_username(self, username):
        """Change @username. Pass '' to remove, or a string to set."""
        self._require_client()
        from telethon.tl.functions.account import UpdateUsernameRequest
        return await self._client(UpdateUsernameRequest(username=username))

    async def check_username(self, username):
        """Check whether a username is available (True = free)."""
        self._require_client()
        from telethon.tl.functions.account import CheckUsernameRequest
        return await self._client(CheckUsernameRequest(username=username))

    async def update_status(self, offline=False):
        """Set online/offline status."""
        self._require_client()
        from telethon.tl.functions.account import UpdateStatusRequest
        return await self._client(UpdateStatusRequest(offline=offline))

    async def set_offline(self):
        """Shortcut: mark self as offline."""
        return await self.update_status(offline=True)

    async def set_online(self):
        """Shortcut: mark self as online."""
        return await self.update_status(offline=False)

    # -- security / sessions --
    async def get_authorizations(self):
        """List active sessions (logged-in devices)."""
        self._require_client()
        from telethon.tl.functions.account import GetAuthorizationsRequest
        return await self._client(GetAuthorizationsRequest())

    async def reset_authorization(self, session_hash):
        """Terminate a specific session by its hash (from get_authorizations)."""
        self._require_client()
        from telethon.tl.functions.account import ResetAuthorizationRequest
        return await self._client(ResetAuthorizationRequest(hash=session_hash))

    async def get_password(self):
        """Fetch 2FA password info (has_password, hint, etc.)."""
        self._require_client()
        from telethon.tl.functions.account import GetPasswordRequest
        return await self._client(GetPasswordRequest())

    async def get_web_authorizations(self):
        """List logged-in websites."""
        self._require_client()
        from telethon.tl.functions.account import GetWebAuthorizationsRequest
        return await self._client(GetWebAuthorizationsRequest())

    async def reset_web_authorization(self, hash_):
        """Terminate one web session."""
        self._require_client()
        from telethon.tl.functions.account import ResetWebAuthorizationRequest
        return await self._client(ResetWebAuthorizationRequest(hash=hash_))

    async def reset_web_authorizations(self):
        """Terminate all web sessions."""
        self._require_client()
        from telethon.tl.functions.account import ResetWebAuthorizationsRequest
        return await self._client(ResetWebAuthorizationsRequest())

    async def get_account_ttl(self):
        """Get account self-destruct time (in days)."""
        self._require_client()
        from telethon.tl.functions.account import GetAccountTTLRequest
        return await self._client(GetAccountTTLRequest())

    async def set_account_ttl(self, ttl):
        """Set account self-destruct time (ttl: AccountDaysTTL instance)."""
        self._require_client()
        from telethon.tl.functions.account import SetAccountTTLRequest
        return await self._client(SetAccountTTLRequest(ttl=ttl))

    # -- privacy --
    async def get_privacy(self, key):
        """Get privacy rules for a key (e.g. InputPrivacyKeyStatusTimestamp)."""
        self._require_client()
        from telethon.tl.functions.account import GetPrivacyRequest
        return await self._client(GetPrivacyRequest(key=key))

    async def set_privacy(self, key, rules):
        """Set privacy rules (rules: list of InputPrivacyRule)."""
        self._require_client()
        from telethon.tl.functions.account import SetPrivacyRequest
        return await self._client(SetPrivacyRequest(key=key, rules=rules))

    # -- notify --
    async def get_notify_settings(self, peer):
        """Fetch notification settings for a peer (InputNotifyPeer)."""
        self._require_client()
        from telethon.tl.functions.account import GetNotifySettingsRequest
        return await self._client(GetNotifySettingsRequest(peer=peer))

    async def update_notify_settings(self, peer, settings):
        """Update notification settings for a peer."""
        self._require_client()
        from telethon.tl.functions.account import UpdateNotifySettingsRequest
        return await self._client(UpdateNotifySettingsRequest(
            peer=peer, settings=settings,
        ))

    # -- content / auto-download --
    async def get_content_settings(self):
        """Get content sensitivity settings."""
        self._require_client()
        from telethon.tl.functions.account import GetContentSettingsRequest
        return await self._client(GetContentSettingsRequest())

    async def get_auto_download_settings(self):
        """Get auto-download settings."""
        self._require_client()
        from telethon.tl.functions.account import GetAutoDownloadSettingsRequest
        return await self._client(GetAutoDownloadSettingsRequest())


# ---------- attach everything ----------
def bind_to(client_cls):
    """Attach auto-generated + hand-written methods to VibeClient."""
    # 1) hand-written
    for name, fn in AccountMixin.__dict__.items():
        if name.startswith("__") or not callable(fn):
            continue
        if name.startswith("_"):
            continue
        setattr(client_cls, name, fn)
    # 2) auto-generated (only if not already overridden by hand-written)
    generated = _collect_account_methods()
    count_new, count_skipped = 0, 0
    for name, fn in generated.items():
        if hasattr(client_cls, name):
            count_skipped += 1
            continue
        setattr(client_cls, name, fn)
        count_new += 1
    return count_new, count_skipped


_vlog("[account] module loaded; call bind_to(VibeClient) to attach methods")
