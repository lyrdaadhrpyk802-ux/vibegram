# ============================================
#  userapi/_tl_auto.py - shared TL auto-wrapper helpers
#  Generates async methods that invoke a TL request class with automatic
#  `hash=0` default when the request signature requires it.
#  All code and comments are English. No emojis.
# ============================================
import inspect
import re


_SKIP = frozenset({"TLRequest", "TLObject", "List", "Optional"})


def snake(name):
    n = name[:-7] if name.endswith("Request") else name
    return re.sub(r"(?<!^)(?=[A-Z])", "_", n).lower()


def make_wrapper(tl_name, tl_cls, prefix):
    has_hash = False
    try:
        sig = inspect.signature(tl_cls.__init__)
        if "hash" in sig.parameters:
            has_hash = True
    except (ValueError, TypeError):
        pass

    async def wrapper(self, *args, **kwargs):
        self._require_client()
        if has_hash and not args and "hash" not in kwargs:
            kwargs["hash"] = 0
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


def collect(namespace_module, prefix):
    methods = {}
    for name in dir(namespace_module):
        if name.startswith("_") or not name.endswith("Request"):
            continue
        if name in _SKIP:
            continue
        cls = getattr(namespace_module, name, None)
        if not isinstance(cls, type) or not hasattr(cls, "CONSTRUCTOR_ID"):
            continue
        methods[snake(name)] = make_wrapper(name, cls, prefix)
    return methods


def bind(client_cls, namespace_module, prefix, extra_mixin=None):
    if extra_mixin is not None:
        for name, fn in extra_mixin.__dict__.items():
            if name.startswith("__") or name.startswith("_"):
                continue
            if not callable(fn):
                continue
            setattr(client_cls, name, fn)
    generated = collect(namespace_module, prefix)
    new, skipped = 0, 0
    for name, fn in generated.items():
        if hasattr(client_cls, name):
            skipped += 1
            continue
        setattr(client_cls, name, fn)
        new += 1
    return new, skipped
