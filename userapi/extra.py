# ============================================
#  userapi/extra.py - remaining TL namespaces
#  One module that wraps every leftover functions.* namespace:
#    auth, bots, ephemeral, fragment, help, langpack, aicompose, smsjobs,
#    payments, phone, premium, stats, stickers, stories, updates, upload
#  Call bind_all(VibeClient) once at import time.
#  All code and comments are English. No emojis.
# ============================================
from telethon.tl import functions as tl_functions
from userapi._tl_auto import bind as _bind
from userapi._log import info as _vlog


_NAMESPACES = [
    ("auth",       "Auth",        False),
    ("bots",       "Bots",        False),
    ("ephemeral",  "Ephemeral",   False),
    ("fragment",   "Fragment",    False),
    ("help",       "Help",        False),
    ("langpack",   "Langpack",    False),
    ("aicompose",  "Aicompose",   False),
    ("smsjobs",    "Smsjobs",     False),
    ("payments",   "Payments",    False),
    ("phone",      "Phone",       False),
    ("premium",    "Premium",     False),
    ("stats",      "Stats",       False),
    ("stickers",   "Stickers",    False),
    ("stories",    "Stories",     False),
    ("updates",    "Updates",     False),
    ("upload",     "Upload",      False),
]


def bind_all(client_cls):
    """Attach every functions.<ns>.* TL request as an async method."""
    summary = []
    for ns_name, prefix, channel_fix in _NAMESPACES:
        ns = getattr(tl_functions, ns_name, None)
        if ns is None:
            summary.append((ns_name, 0, 0, "namespace missing"))
            continue
        new, skipped = _bind(
            client_cls, ns, prefix, None, channel_fix=channel_fix,
        )
        summary.append((ns_name, new, skipped, "ok"))
    return summary


_vlog("[extra] module loaded; call bind_all(VibeClient) to attach methods")
