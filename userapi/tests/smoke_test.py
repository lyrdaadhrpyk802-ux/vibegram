# ============================================
#  userapi/tests/smoke_test.py - single-shot connectivity check
#  All code and comments are English. No emojis.
# ============================================
import asyncio
import os
import struct
from Crypto.Cipher import AES
import websockets

from userapi.crypto.obfuscated import build_init


URL = "wss://apiws.vibegram.chat/apiws"


def _msg_id():
    import time
    now = time.time()
    secs = int(now)
    micros = int((now - secs) * 1e6)
    return ((secs << 32) | (micros << 2) & 0xFFFFFFFC).to_bytes(8, 'little')


async def run():
    header, cipher, (dec_key, dec_iv) = build_init(dc_id=2)
    nonce = os.urandom(16)
    payload = b'\xf1\x8e\x7e\xbe' + nonce       # req_pq_multi
    inner = b'\x00' * 8 + _msg_id() + struct.pack('<I', len(payload)) + payload
    frame = header + bytes([len(inner) // 4]) + cipher.encrypt(inner)

    print(f"[>] sending {len(frame)}B to {URL}")
    async with websockets.connect(URL, subprotocols=["binary"],
                                  max_size=None, open_timeout=15) as ws:
        await ws.send(frame)
        try:
            resp = await asyncio.wait_for(ws.recv(), timeout=15)
        except asyncio.TimeoutError:
            print("[-] timeout (rate limit likely active)")
            return
    dec = AES.new(dec_key, AES.MODE_CTR, nonce=b'', initial_value=dec_iv).decrypt(resp)
    print(f"[<] {len(resp)}B: {dec[:32].hex()}")
    if b'\x63\x24\x16\x05' in dec:
        print("[+] resPQ — handshake works")
    elif len(dec) >= 5 and dec[0] == 0x01:
        code = struct.unpack('<i', dec[1:5])[0]
        print(f"[<] abridged error code: {code}")


if __name__ == "__main__":
    asyncio.run(run())
