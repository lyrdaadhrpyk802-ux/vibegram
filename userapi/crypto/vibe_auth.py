# ============================================
#  userapi/crypto/vibe_auth.py - Vibe custom auth patches
#  Vibe uses a non-standard RSA scheme for req_DH_params:
#    - PQInnerData -> p_q_inner_data_dc (0xa9f55f95) with dc field
#    - RSA encryption: pad192 + reverse + sha256+AES-IGE loop + raw RSA
#  All code and comments are English. No emojis.
# ============================================
import hashlib
import os
import struct

from telethon.crypto import rsa, AES
from telethon.tl.types import PQInnerData
from userapi._log import info as _vlog


VIBE_FINGERPRINT = -7080122280541503745
VIBE_DC_ID = 2

_APPLIED = False


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


_orig_rsa_encrypt = rsa.encrypt


def _vibe_rsa_encrypt(fp, data, *, use_old=False):
    if fp == VIBE_FINGERPRINT:
        key, old = rsa._server_keys.get(fp, [None, None])
        if not key or (old and not use_old):
            return None
        return vibe_rsa_encrypt(data, key)
    return _orig_rsa_encrypt(fp, data, use_old=use_old)


def apply_patches():
    """Apply Vibe auth patches to Telethon. Idempotent."""
    global _APPLIED
    if _APPLIED:
        return
    PQInnerData.__init__ = _pq_inner_init
    PQInnerData._bytes = _pq_inner_bytes
    PQInnerData.CONSTRUCTOR_ID = 0xa9f55f95
    rsa.encrypt = _vibe_rsa_encrypt
    _APPLIED = True
    _vlog("[vibe_auth] patches applied")
