# ============================================
#  userapi/contacts.py - Vibe contacts API
#  Wraps all functions.contacts.* TL requests plus convenience methods.
#  All code and comments are English. No emojis.
# ============================================
import inspect
import re

from telethon.tl import functions as tl_functions
from userapi._log import info as _vlog


_SKIP = frozenset({"TLRequest", "TLObject", "List", "Optional"})


def _snake(name):
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
    wrapper.__qualname__ = f"Contacts.{wrapper.__name__}"
    doc = f"Contacts: {tl_name}. Wraps functions.contacts.{tl_name}."
    try:
        sig = inspect.signature(tl_cls.__init__)
        params = [p for n, p in sig.parameters.items() if n != "self"]
        if params:
            doc += "\n\nSignature: " + str(sig).replace("(self, ", "(").replace("(self)", "()")
    except (ValueError, TypeError):
        pass
    wrapper.__doc__ = doc
    return wrapper


def _collect_contacts_methods():
    methods = {}
    for name in dir(tl_functions.contacts):
        if name.startswith("_") or not name.endswith("Request"):
            continue
        if name in _SKIP:
            continue
        cls = getattr(tl_functions.contacts, name, None)
        if not isinstance(cls, type) or not hasattr(cls, "CONSTRUCTOR_ID"):
            continue
        methods[_snake(name)] = _make_async_wrapper(name, cls)
    return methods


class ContactsMixin:
    """Hand-written convenience methods for contacts."""

    async def get_contacts(self):
        """Return the full contact list (list of User objects)."""
        from telethon.tl.functions.contacts import GetContactsRequest
        self._require_client()
        r = await self._client(GetContactsRequest(hash=0))
        return r.users

    async def add_contact(self, user_id, first_name, last_name="",
                          phone=None, add_phone_privacy_exception=False):
        """Add user to contacts."""
        from telethon.tl.functions.contacts import AddContactRequest
        from telethon.tl.types import InputPhoneContact
        self._require_client()
        contact = InputPhoneContact(
            client_id=0, phone=phone or "",
            first_name=first_name, last_name=last_name,
        )
        return await self._client(AddContactRequest(
            id=[contact], first_name=first_name, last_name=last_name,
            phone=phone or "",
            add_phone_privacy_exception=add_phone_privacy_exception,
        ))

    async def delete_contacts(self, user_ids):
        """Delete contacts by user id list."""
        from telethon.tl.functions.contacts import DeleteContactsRequest
        self._require_client()
        if not isinstance(user_ids, (list, tuple)):
            user_ids = [user_ids]
        users = [await self._client.get_input_entity(uid) for uid in user_ids]
        return await self._client(DeleteContactsRequest(id=users))

    async def import_contacts(self, phone_contacts):
        """Bulk import contacts from InputPhoneContact list."""
        from telethon.tl.functions.contacts import ImportContactsRequest
        self._require_client()
        return await self._client(ImportContactsRequest(contacts=phone_contacts))

    async def block_user(self, user):
        """Block a user."""
        from telethon.tl.functions.contacts import BlockRequest
        self._require_client()
        entity = await self._client.get_input_entity(user)
        return await self._client(BlockRequest(id=entity))

    async def unblock_user(self, user):
        """Unblock a user."""
        from telethon.tl.functions.contacts import UnblockRequest
        self._require_client()
        entity = await self._client.get_input_entity(user)
        return await self._client(UnblockRequest(id=entity))

    async def get_blocked(self):
        """List blocked users."""
        from telethon.tl.functions.contacts import GetBlockedRequest
        self._require_client()
        r = await self._client(GetBlockedRequest(offset=0, limit=100))
        return r.blocked


def bind_to(client_cls):
    for name, fn in ContactsMixin.__dict__.items():
        if name.startswith("__") or name.startswith("_"):
            continue
        if not callable(fn):
            continue
        setattr(client_cls, name, fn)
    generated = _collect_contacts_methods()
    count_new, count_skipped = 0, 0
    for name, fn in generated.items():
        if hasattr(client_cls, name):
            count_skipped += 1
            continue
        setattr(client_cls, name, fn)
        count_new += 1
    return count_new, count_skipped


_vlog("[contacts] module loaded; call bind_to(VibeClient) to attach methods")
