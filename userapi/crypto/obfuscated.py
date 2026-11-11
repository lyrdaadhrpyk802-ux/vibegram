# ============================================
#  userapi/crypto/obfuscated.py - obfuscated2 header builder
#  All code and comments are English. No emojis.
# ============================================
import os
from Crypto.Cipher import AES


RESERVED_FIRST_DWORD = {1145128264, 1414745936, 542393671,
                        1230262351, 4008636142, 3722304989}


def _random_header() -> bytearray:
    while True:
        buf = bytearray(os.urandom(64))
        first = int.from_bytes(buf[0:4], 'little')
        if buf[0] != 0xef and first not in RESERVED_FIRST_DWORD:
            return buf


def build_init(dc_id: int = 2, tag: bytes = b'\xef\xef\xef\xef'):
    """Build obfuscated2 init header and cipher state.

    Key derivation (verified against real pcap):
      enc_key = header[8:40]   (raw, NO SHA256)
      enc_iv  = header[40:56]  (raw)
      dec_key = reverse(header)[8:40]
      dec_iv  = reverse(header)[40:56]
    """
    buf = _random_header()
    buf[56:60] = tag
    buf[60:62] = dc_id.to_bytes(2, 'little')

    enc_key = bytes(buf[8:40])
    enc_iv = bytes(buf[40:56])
    rev = bytes(buf)[::-1]
    dec_key = rev[8:40]
    dec_iv = rev[40:56]

    cipher = AES.new(enc_key, AES.MODE_CTR, nonce=b'', initial_value=enc_iv)
    enc = cipher.encrypt(bytes(buf))
    buf[56:64] = enc[56:64]
    return bytes(buf), cipher, (dec_key, dec_iv)
