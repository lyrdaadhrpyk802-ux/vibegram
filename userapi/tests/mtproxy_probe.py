# ============================================
#  userapi/tests/mtproxy_probe.py
#  MTProxy probe: try multiple secret interpretations
#  All code and comments are English. No emojis.
# ============================================
import asyncio
import base64
import os
import struct
import sys
import time
from hashlib import sha256
from Crypto.Cipher import AES


HOST = "ai.golgoli1.co.uk"
PORT = 2096
SECRET_B64 = "eeNEgYdJvXrFGRMCIMJdCQ"


def msg_id():
    now = time.time()
    return ((int(now) << 32) | (int((now % 1) * 1e6) << 2) & 0xFFFFFFFC).to_bytes(8, 'little')


def make_frame(secret, tag, key_material_0_32, iv_material_32_48, reverse):
    """Build obfuscated2 header. reverse=True means use reversed buf for recv."""
    while True:
        buf = bytearray(os.urandom(64))
        if buf[0] != 0xef and int.from_bytes(buf[0:4], 'little') not in {1145128264, 1414745936}:
            break
    buf[56:60] = tag
    # For MTProxy: dc_id bytes stay 0 (or random if not set)

    # Key derivation
    if reverse:
        key_mat = bytes(buf[::-1][0:32])
        iv_mat = bytes(buf[::-1][32:48])
    else:
        key_mat = bytes(buf[0:32])
        iv_mat = bytes(buf[32:48])

    key = sha256(secret + key_mat).digest()
    iv = iv_mat

    c = AES.new(key, AES.MODE_CTR, nonce=b'', initial_value=iv)
    enc_header = c.encrypt(bytes(buf))
    buf[56:64] = enc_header[56:64]
    return bytes(buf), c


async def probe(label, secret, tag, use_reverse, dc_bytes_setting):
    print(f"\n=== {label} ===")
    try:
        header, c = make_frame(secret, tag, None, None, use_reverse)
        
        # If dc_bytes_setting is not None, put DC ID in 60:62 (after encrypt, so re-encrypt)
        if dc_bytes_setting is not None:
            # Rebuild with dc
            while True:
                buf = bytearray(os.urandom(64))
                if buf[0] != 0xef and int.from_bytes(buf[0:4], 'little') not in {1145128264, 1414745936}:
                    break
            buf[56:60] = tag
            buf[60:62] = dc_bytes_setting
            key = sha256(secret + bytes(buf[0:32])).digest()
            iv = bytes(buf[32:48])
            c = AES.new(key, AES.MODE_CTR, nonce=b'', initial_value=iv)
            enc = c.encrypt(bytes(buf))
            buf[56:64] = enc[56:64]
            header = bytes(buf)
        
        # Derive recv cipher independently
        rev = header[::-1]
        if use_reverse:
            recv_key = sha256(secret + header[::-1][0:32]).digest()
            recv_iv = header[::-1][32:48]
        else:
            recv_key = sha256(secret + rev[0:32]).digest()
            recv_iv = rev[32:48]
        
        nonce = os.urandom(16)
        pq = b'\xf1\x8e\x7e\xbe' + nonce
        inner = b'\x00'*8 + msg_id() + struct.pack('<I', len(pq)) + pq
        frame = header + bytes([len(inner)//4]) + c.encrypt(inner)
        
        reader, writer = await asyncio.open_connection(HOST, PORT)
        writer.write(frame)
        await writer.drain()
        
        try:
            resp = await asyncio.wait_for(reader.read(4096), timeout=10)
        except asyncio.TimeoutError:
            writer.close()
            print("[-] timeout")
            return False
        
        writer.close()
        if not resp:
            print("[-] no data")
            return False
        
        print(f"[<] {len(resp)}B raw: {resp[:16].hex()}...")
        dec = AES.new(recv_key, AES.MODE_CTR, nonce=b'', initial_value=recv_iv).decrypt(resp)
        print(f"[<] dec: {dec[:32].hex()}")
        if b'\x63\x24\x16\x05' in dec:
            print("[+++] *** resPQ MATCH ***")
            return True
        if len(dec) >= 5 and dec[0] == 0x01:
            print(f"[<] code: {struct.unpack('<i', dec[1:5])[0]}")
        return False
    except Exception as e:
        print(f"[!] {type(e).__name__}: {e}")
        return False


async def main():
    # Secret candidates
    candidates = [
        ("16B full (base64url decode all)", base64.urlsafe_b64decode("eeNEgYdJvXrFGRMCIMJdCQ" + "==")),
        ("strip ee, 15B", base64.urlsafe_b64decode("NEgYdJvXrFGRMCIMJdCQ" + "=")),
        ("strip ee, zero-pad 16B", base64.urlsafe_b64decode("NEgYdJvXrFGRMCIMJdCQ" + "=") + b'\x00'),
    ]
    
    tests = [
        ("no_reverse, no_dc", b'\xef\xef\xef\xef', False, None),
        ("no_reverse, dc0", b'\xef\xef\xef\xef', False, b'\x00\x00'),
        ("reverse, no_dc", b'\xef\xef\xef\xef', True, None),
    ]
    
    for label, sec in candidates:
        for tlabel, tag, rev, dc in tests:
            if await probe(f"{label} / {tlabel}", sec, tag, rev, dc):
                print(f"\n[+++] SUCCESS with: secret={label}, tag={tlabel}")
                return
            await asyncio.sleep(0.5)
    
    print("\n[-] All combinations failed.")


asyncio.run(main())
