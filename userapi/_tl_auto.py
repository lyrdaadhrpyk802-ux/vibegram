# ============================================
#  userapi/_tl_auto.py - shared TL auto-wrapper helpers
#  Generates async methods for TL request classes. Handles:
#    - automatic hash=0 default when required
#    - automatic InputChannel conversion for channels.* requests
#  All code and comments are English. No emojis.
# ============================================
import inspect
import re


_SKIP = frozenset({"TLRequest", "TLObject", "List", "Optional"})


def snake(name):
    n = name[:-7] if name.endswith("Request") else name
    return re.sub(r"(?<!^)(?=[A-Z])", "_", n).lower()


async def _ensure_input_channel(client, value):
    """Convert value to InputChannel (accepts entity, InputPeerChannel, InputChannel)."""
    from telethon.tl.types import InputChannel, InputPeerChannel
    if isinstance(value, InputChannel):
        return value
    if isinstance(value, InputPeerChannel):
        return InputChannel(
            channel_id=value.channel_id,
            access_hash=value.access_hash,
        )
    ent = await client.get_input_entity(value)
    if isinstance(ent, InputPeerChannel):
        return InputChannel(channel_id=ent.channel_id, access_hash=ent.access_hash)
    return ent


def make_wrapper(tl_name, tl_cls, prefix, channel_fix=False):
    has_hash = False
    has_channel_param = False
    try:
        sig = inspect.signature(tl_cls.__init__)
        params = sig.parameters
        if "hash" in params:
            has_hash = True
        if "channel" in params:
            has_channel_param = True
    except (ValueError, TypeError):
        pass

    async def wrapper(self, *args, **kwargs):
        self._require_client()
        if has_hash and not args and "hash" not in kwargs:
            kwargs["hash"] = 0
        if channel_fix and has_channel_param:
            key = None
            for k in ("channel", "peer"):
                if k in kwargs:
                    key = k
                    break
            if key is not None:
                kwargs[key] = await _ensure_input_channel(self._client, kwargs[key])
        return await self._client(tl_cls(*args, **kwargs))

    wrapper.__name__ = snake(tl_name)
    wrapper.__qualname__ = f"{prefix}.{wrapper.__name__}"
    doc = f"{prefix}: {tl_name}. Wraps TL request {tl_name}."
    try:
        sig = inspect.signature(tl_cls.__init__)
        params = [p for n, p in sig.parameters.items() if n != "self"]
        if params:
            doc += "\n\nSignature: " + str(sig).replace("(self, ", "(").replace("(self)", "()")
    except (ValueError, TypeError):
        pass
    wrapper.__doc__ = doc
    return wrapper


def collect(namespace_module, prefix, channel_fix=False):
    methods = {}
    for name in dir(namespace_module):
        if name.startswith("_") or not name.endswith("Request"):
            continue
        if name in _SKIP:
            continue
        cls = getattr(namespace_module, name, None)
        if not isinstance(cls, type) or not hasattr(cls, "CONSTRUCTOR_ID"):
            continue
        methods[snake(name)] = make_wrapper(name, cls, prefix, channel_fix=channel_fix)
    return methods


def bind(client_cls, namespace_module, prefix, extra_mixin=None, channel_fix=False):
    if extra_mixin is not None:
        for name, fn in extra_mixin.__dict__.items():
            if name.startswith("__") or name.startswith("_"):
                continue
            if not callable(fn):
                continue
            setattr(client_cls, name, fn)
    generated = collect(namespace_module, prefix, channel_fix=channel_fix)
    new, skipped = 0, 0
    for name, fn in generated.items():
        if hasattr(client_cls, name):
            skipped += 1
            continue
        setattr(client_cls, name, fn)
        new += 1
    return new, skipped
