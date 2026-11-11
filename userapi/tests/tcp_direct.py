# ============================================
#  userapi/tests/tcp_direct.py
#  Direct TCP test to 5.42.223.7:2398 (Android endpoint)
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


def build_header(dc_id):
    while True:
        buf = bytearray(os.urandom(64))
        first = int.from_bytes(buf[0:4], 'little')
        if buf[0] != 0xef and first not in RESERVED:
            break
    buf[56:60] = b'\xef\xef\xef\xef'
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


def make_msg_id():
    now = time.time()
    return ((int(now) << 32)
            | (int((now % 1) * 0x100000000) & 0xFFFFFFFC)).to_bytes(8, 'little')


def run(dc_id):
    print(f"[*] DC={dc_id}, target={HOST}:{PORT}")
    header, cipher, (dec_key, dec_iv) = build_header(dc_id)

    nonce = os.urandom(16)
    pq = b'\xf1\x8e\x7e\xbe' + nonce  # req_pq_multi
    inner = b'\x00' * 8 + make_msg_id() + struct.pack('<I', len(pq)) + pq
    frame = header + bytes([len(inner) // 4]) + cipher.encrypt(inner)

    print(f"[*] header[0:8]={header[0:8].hex()} header[56:64]={header[56:64].hex()}")
    print(f"[*] frame={len(frame)}B")

    try:
        s = socket.create_connection((HOST, PORT), timeout=10)
    except (socket.timeout, OSError) as e:
        print(f"[!] TCP connect failed: {type(e).__name__}: {e}")
        return False

    with s:
        s.settimeout(12)
        print("[+] TCP connected")
        s.sendall(frame)
        print(f"[>] sent {len(frame)}B")

        try:
            resp = s.recv(4096)
        except socket.timeout:
            print("[-] timeout waiting for response (server alive but silent)")
            return False

        if not resp:
            print("[-] server closed without data")
            return False

        print(f"[<] {len(resp)}B raw hex: {resp[:64].hex()}")
        print(f"[<] raw ascii   : {resp[:64]!r}")

        dec = AES.new(dec_key, AES.MODE_CTR, nonce=b'',
                      initial_value=dec_iv).decrypt(resp)
        print(f"[<] decrypted   : {dec[:64].hex()}")

        if b'\x63\x24\x16\x05' in dec or b'\x05\x16\x24\x63' in dec:
            print("[+++] *** resPQ MATCH! TCP endpoint is the real DC. ***")
            return True
        if nonce in dec:
            print("[+++] *** nonce echoed! ***")
            return True
        if len(dec) >= 5 and dec[0] == 0x01:
            code = struct.unpack('<i', dec[1:5])[0]
            print(f"[<] abridged error code: {code}")
            if code == -404:
                print("[i] -404 is a valid MTProto response. Endpoint is real.")
                return True
        return False


if __name__ == "__main__":
    dc = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    run(dc)
