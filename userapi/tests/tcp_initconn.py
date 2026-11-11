# ============================================
#  userapi/tests/tcp_initconn.py
#  TCP + obfuscated2 + initConnection wrapper to real DC
#  All code and comments are English. No emojis.
# ============================================
import os
import socket
import struct
import sys
import time
from Crypto.Cipher import AES


HOST, PORT = "5.42.223.7", 2398
RESERVED = {1145128264, 1414745936, 542393671,
            1230262351, 4008636142, 3722304989}
LAYER = 158
API_ID = 4


def build_header(dc_id):
    while True:
        buf = bytearray(os.urandom(64))
        if buf[0] != 0xef and int.from_bytes(buf[0:4], 'little') not in RESERVED:
            break
    buf[56:60] = b'\xef\xef\xef\xef'
    buf[60:62] = dc_id.to_bytes(2, 'little')
    c = AES.new(bytes(buf[8:40]), AES.MODE_CTR, nonce=b'',
                initial_value=bytes(buf[40:56]))
    e = c.encrypt(bytes(buf))
    buf[56:64] = e[56:64]
    rev = bytes(buf)[::-1]
    return bytes(buf), c, (rev[8:40], rev[40:56])


def msg_id():
    now = time.time()
    return ((int(now) << 32) | (int((now % 1) * 1e6) << 2) & 0xFFFFFFFC).to_bytes(8, 'little')


def s(x):
    b = x.encode() if isinstance(x, str) else x
    pad = (4 - len(b) % 4) % 4
    return bytes([len(b)]) + b + b'\x00' * pad


def build_init_connection():
    """invokeWithLayer(layer, initConnection(api_id, ..., req_pq_multi(nonce)))"""
    nonce = os.urandom(16)
    req_pq = b'\xf1\x8e\x7e\xbe' + nonce

    # initConnection#c1cd5ea9
    init = struct.pack('<I', 0xc1cd5ea9)   # constructor
    init += struct.pack('<I', 0)           # flags
    init += struct.pack('<i', API_ID)      # api_id
    init += s("Samsung SM-G975F")          # device_model
    init += s("SDK 29")                    # system_version
    init += s("1.0.1 (500)")               # app_version
    init += s("fa")                        # system_lang_code
    init += s("")                          # lang_pack
    init += s("fa")                        # lang_code
    init += req_pq                         # query

    # invokeWithLayer#da9b0d0d
    wrapped = struct.pack('<I', 0xda9b0d0d)
    wrapped += struct.pack('<i', LAYER)
    wrapped += init
    return wrapped, nonce


def run(dc, mode):
    print(f"\n=== DC={dc}, mode={mode} ===")
    header, cipher, (dk, di) = build_header(dc)

    if mode == "initconn":
        payload, nonce = build_init_connection()
    elif mode == "raw":
        nonce = os.urandom(16)
        payload = b'\xf1\x8e\x7e\xbe' + nonce
    else:
        return

    auth_key_id = b'\x00' * 8
    inner = auth_key_id + msg_id() + struct.pack('<I', len(payload)) + payload
    frame = header + bytes([len(inner) // 4]) + cipher.encrypt(inner)

    print(f"[*] sending {len(frame)}B")
    try:
        s_sock = socket.create_connection((HOST, PORT), timeout=10)
    except Exception as e:
        print(f"[!] connect: {type(e).__name__}: {e}")
        return

    with s_sock:
        s_sock.settimeout(15)
        s_sock.sendall(frame)
        try:
            resp = s_sock.recv(4096)
        except socket.timeout:
            print("[-] timeout (silence)")
            return
        if not resp:
            print("[-] closed no data")
            return
        print(f"[<] {len(resp)}B raw: {resp[:64].hex()}")
        dec = AES.new(dk, AES.MODE_CTR, nonce=b'', initial_value=di).decrypt(resp)
        print(f"[<] decrypted : {dec[:64].hex()}")
        if b'\x63\x24\x16\x05' in dec:
            print("[+++] resPQ!")
            return True
        if len(dec) >= 5 and dec[0] == 0x01:
            code = struct.unpack('<i', dec[1:5])[0]
            print(f"[<] error code: {code}")
        return False


if __name__ == "__main__":
    dc = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    mode = sys.argv[2] if len(sys.argv) > 2 else "initconn"
    run(dc, mode)
