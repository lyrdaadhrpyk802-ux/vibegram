# ============================================
#  tests/test_vibe_auth.py - tests for the Vibe auth patches
#  Verifies patch application, constructor id, _bytes layout, idempotency,
#  rollback via unapply_patches, and the Telethon version guard.
# ============================================
import os
import struct

import pytest
import telethon
from telethon.tl.types import PQInnerData
from telethon.crypto import rsa


from userapi.crypto import vibe_auth as V

# userapi auto-applies patches at import time (and other test modules may have
# imported it before us), so restore the pristine state first, THEN capture.
V.unapply_patches()

VIBE_EXPECTED_CID = 0xA9F55F95
_PRISTINE_CID = PQInnerData.CONSTRUCTOR_ID
_PRISTINE_RSA = rsa.encrypt
_PRISTINE_INIT = PQInnerData.__init__
_PRISTINE_BYTES = PQInnerData._bytes


@pytest.fixture(autouse=True)
def _reset_patches():
    """Ensure each test starts and ends in a clean, unpatched state."""
    V.unapply_patches()
    yield
    V.unapply_patches()
    # Re-apply at the very end of the suite so downstream imports stay patched.
    V.apply_patches()


def test_fingerprint_constant():
    assert V.VIBE_FINGERPRINT == -7080122280541503745


def test_apply_sets_constructor_id():
    V.apply_patches()
    assert PQInnerData.CONSTRUCTOR_ID == VIBE_EXPECTED_CID


def test_apply_swaps_rsa_encrypt():
    V.apply_patches()
    assert rsa.encrypt is V._vibe_rsa_encrypt


def test_apply_replaces_init_and_bytes():
    V.apply_patches()
    assert PQInnerData.__init__ is V._pq_inner_init
    assert PQInnerData._bytes is V._pq_inner_bytes


def test_apply_is_idempotent():
    V.apply_patches()
    cid_after_first = PQInnerData.CONSTRUCTOR_ID
    V.apply_patches()  # must be a no-op
    assert PQInnerData.CONSTRUCTOR_ID == cid_after_first


def test_unapply_before_apply_is_noop():
    # Should not raise even though nothing was applied.
    V.unapply_patches()
    assert V._APPLIED is False


def test_unapply_restores_all_originals():
    V.apply_patches()
    V.unapply_patches()
    assert PQInnerData.CONSTRUCTOR_ID == _PRISTINE_CID
    assert rsa.encrypt is _PRISTINE_RSA
    assert PQInnerData.__init__ is _PRISTINE_INIT
    assert PQInnerData._bytes is _PRISTINE_BYTES
    assert V._APPLIED is False
    assert V._ORIGINALS is None


def test_pq_inner_bytes_layout():
    V.apply_patches()
    obj = PQInnerData(
        pq=(0x17ED48941B32A6).to_bytes(8, "big"),
        p=(0x3C2DD8E5).to_bytes(4, "big"),
        q=(0x5E849F1B).to_bytes(4, "big"),
        nonce=0x11111111111111111111111111111111,
        server_nonce=0x22222222222222222222222222222222,
        new_nonce=0x3333333333333333333333333333333333333333333333333333333333333333,
        dc=2,
    )
    raw = PQInnerData._bytes(obj)
    # Prefix is the Vibe p_q_inner_data_dc constructor id (little-endian).
    assert raw[:4] == b"\x95\x5f\xf5\xa9"
    # Trailing 4 bytes are the dc field as a little-endian int32.
    assert struct.unpack("<i", raw[-4:])[0] == 2


def test_vibe_rsa_encrypt_rejects_oversized_input():
    # A fake public key with a large modulus is enough; we never reach the
    # RSA step because the length check fires first.
    class FakePub:
        n = (1 << 2048)
        e = 65537
    with pytest.raises(ValueError):
        V.vibe_rsa_encrypt(b"x" * 200, FakePub())


def test_version_guard_rejects_unsupported(monkeypatch):
    monkeypatch.setattr(telethon, "__version__", "2.5.0")
    monkeypatch.delenv("VIBE_TELETHON_STRICT", raising=False)
    V._APPLIED = False  # force the guard to run
    with pytest.raises(RuntimeError):
        V.apply_patches()


def test_version_guard_strict_zero_downgrades(monkeypatch):
    monkeypatch.setattr(telethon, "__version__", "2.5.0")
    monkeypatch.setenv("VIBE_TELETHON_STRICT", "0")
    V._APPLIED = False
    # Must NOT raise; patches still apply.
    V.apply_patches()
    assert PQInnerData.CONSTRUCTOR_ID == VIBE_EXPECTED_CID


def test_version_guard_accepts_supported(monkeypatch):
    monkeypatch.setattr(telethon, "__version__", "1.45.0")
    monkeypatch.delenv("VIBE_TELETHON_STRICT", raising=False)
    V._APPLIED = False
    V.apply_patches()
    assert PQInnerData.CONSTRUCTOR_ID == VIBE_EXPECTED_CID
