# ============================================
#  userapi/crypto/vibe_auth.py - Vibe custom auth patches
#  Vibe uses a non-standard RSA scheme for req_DH_params:
#    - PQInnerData -> p_q_inner_data_dc (0xa9f55f95) with dc field
#    - RSA encryption: pad192 + reverse + sha256+AES-IGE loop + raw RSA
#  Patches are applied to Telethon at runtime; originals are saved so
#  they can be restored via unapply_patches(). A version guard rejects
#  unsupported Telethon builds to avoid silent breakage on upgrade.
#  All code and comments are English. No emojis.
# ============================================
import hashlib
import os
import struct

import telethon
from telethon.crypto import rsa, AES
from telethon.tl.types import PQInnerData
from userapi._log import info as _vlog


VIBE_FINGERPRINT = -7080122280541503745
VIBE_DC_ID = 2

# Telethon versions known to be compatible with these patches.
# The PQInnerData layout and rsa.encrypt signature must stay stable.
SUPPORTED_TELETHON_MIN = (1, 36, 0)
SUPPORTED_TELETHON_MAX = (2, 0, 0)  # exclusive upper bound

_APPLIED = False
_ORIGINALS = None  # dict of saved attributes, set when applied


def _parse_version(v: str):
    parts = []
    for chunk in v.split("."):
        num = ""
        for ch in chunk:
            if ch.isdigit():
                num += ch
            else:
                break
        parts.append(int(num) if num else 0)
    return tuple(parts)


def _check_telethon_version():
    """Raise RuntimeError if the installed Telethon is outside the supported range.

    Set VIBE_TELETHON_STRICT=0 in the environment to downgrade to a warning.
    """
    raw = getattr(telethon, "__version__", "0")
    ver = _parse_version(raw)
    ok = SUPPORTED_TELETHON_MIN <= ver < SUPPORTED_TELETHON_MAX
    msg = (f"[vibe_auth] Telethon {raw} detected; "
           f"supported range is >={'.'.join(map(str, SUPPORTED_TELETHON_MIN))}, "
           f"<{'.'.join(map(str, SUPPORTED_TELETHON_MAX))}.")
    if ok:
        return
    if os.getenv("VIBE_TELETHON_STRICT", "1") == "0":
        print(f"{msg} Continuing because VIBE_TELETHON_STRICT=0.")
        return
    raise RuntimeError(msg + " Set VIBE_TELETHON_STRICT=0 to override.")


def _pq_inner_init(self, pq=None, p=None, q=None, nonce=None,
                   server_nonce=None, new_nonce=None, dc=VIBE_DC_ID, **kwargs):
    self.pq = kwargs.get("pq", pq)
    self.p = kwargs.get("p", p)
    self.q = kwargs.get("q", q)
    self.nonce = kwargs.get("nonce", nonce)
    self.server_nonce = kwargs.get("server_nonce", server_nonce)
    self.new_nonce = kwargs.get("new_nonce", new_nonce)
    self.dc = dc


def _pq_inner_bytes(self):
    return b"".join((
        b"\x95\x5f\xf5\xa9",
        self.serialize_bytes(self.pq),
        self.serialize_bytes(self.p),
        self.serialize_bytes(self.q),
        self.nonce.to_bytes(16, "little", signed=True),
        self.server_nonce.to_bytes(16, "little", signed=True),
        self.new_nonce.to_bytes(32, "little", signed=True),
        struct.pack("<i", self.dc),
    ))


def vibe_rsa_encrypt(data, pub):
    """Vibe custom RSA scheme for req_DH_params encrypted_data."""
    if len(data) > 144:
        raise ValueError(f"p_q_inner_data too long: {len(data)}")
    a = data + os.urandom(192 - len(data))
    o = a[::-1]
    while True:
        t = os.urandom(32)
        h = hashlib.sha256(t + a).digest()
        n = o + h
        r = AES.encrypt_ige(n, t, b"\x00" * 32)
        x = bytes(p ^ q for p, q in zip(t, hashlib.sha256(r).digest()))
        combined = x + r
        s = int.from_bytes(combined, "big")
        if s < pub.n:
            break
    return pow(s, pub.e, pub.n).to_bytes(256, "big")


def _vibe_rsa_encrypt(fp, data, *, use_old=False):
    # Resolve the original lazily so unapply_patches can swap it back cleanly.
    orig = _ORIGINALS["rsa.encrypt"] if _ORIGINALS else _orig_rsa_encrypt
    if fp == VIBE_FINGERPRINT:
        key, old = rsa._server_keys.get(fp, [None, None])
        if not key or (old and not use_old):
            return None
        return vibe_rsa_encrypt(data, key)
    return orig(fp, data, use_old=use_old)


# Captured at import time as a last-resort fallback; apply_patches() re-captures.
_orig_rsa_encrypt = rsa.encrypt


def apply_patches():
    """Apply Vibe auth patches to Telethon. Idempotent.

    Saves the original PQInnerData attributes and rsa.encrypt so they can be
    restored with unapply_patches(). Raises RuntimeError on unsupported
    Telethon versions unless VIBE_TELETHON_STRICT=0 is set.
    """
    global _APPLIED, _ORIGINALS
    if _APPLIED:
        return
    _check_telethon_version()
    _ORIGINALS = {
        "PQInnerData.__init__": PQInnerData.__init__,
        "PQInnerData._bytes": PQInnerData._bytes,
        "PQInnerData.CONSTRUCTOR_ID": PQInnerData.CONSTRUCTOR_ID,
        "rsa.encrypt": rsa.encrypt,
    }
    PQInnerData.__init__ = _pq_inner_init
    PQInnerData._bytes = _pq_inner_bytes
    PQInnerData.CONSTRUCTOR_ID = 0xa9f55f95
    rsa.encrypt = _vibe_rsa_encrypt
    _APPLIED = True
    _vlog("[vibe_auth] patches applied")


def unapply_patches():
    """Restore Telethon originals saved by apply_patches().

    Safe to call even if patches were never applied.
    """
    global _APPLIED, _ORIGINALS
    if not _APPLIED or _ORIGINALS is None:
        return
    try:
        PQInnerData.__init__ = _ORIGINALS["PQInnerData.__init__"]
        PQInnerData._bytes = _ORIGINALS["PQInnerData._bytes"]
        PQInnerData.CONSTRUCTOR_ID = _ORIGINALS["PQInnerData.CONSTRUCTOR_ID"]
        rsa.encrypt = _ORIGINALS["rsa.encrypt"]
    except Exception as e:
        print(f"[vibe_auth] error: failed to restore originals: {e}")
    finally:
        _APPLIED = False
        _ORIGINALS = None
        _vlog("[vibe_auth] patches reverted")
