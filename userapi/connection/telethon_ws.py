# ============================================
#  userapi/connection/telethon_ws.py
#  Telethon Connection: obfuscated2 abridged over WebSocket.
#  Supports SOCKS5/HTTP proxy via module-level set_proxy().
#  Debug logs enabled via VIBE_DEBUG=1 env var.
#  All code and comments are English. No emojis.
# ============================================
import os

from Crypto.Cipher import AES
from telethon.network.connection.tcpabridged import ConnectionTcpAbridged

try:
    from websockets.asyncio.client import connect as ws_connect
except ImportError:
    from websockets import connect as ws_connect


DEFAULT_URL = "wss://apiws.vibegram.chat/apiws"
RESERVED = {1145128264, 1414745936, 542393671,
            1230262351, 4008636142, 3722304989}
_DEBUG = os.getenv("VIBE_DEBUG") == "1"
_PROXY_URL = None


def set_proxy(url):
    global _PROXY_URL
    _PROXY_URL = url


def get_proxy():
    return _PROXY_URL


def _coerce_proxy(p):
    if p is None:
        return None
    if isinstance(p, str):
        return p
    if isinstance(p, (tuple, list)):
        scheme = {
            "socks5": "socks5", "socks4": "socks4",
            "http": "http", "https": "https",
        }.get(str(p[0]).lower(), "socks5")
        host, port = p[1], p[2]
        cred = ""
        if len(p) >= 5 and p[3]:
            cred = f"{p[3]}:{p[4]}@"
        elif len(p) >= 4 and p[3]:
            cred = f"{p[3]}@"
        return f"{scheme}://{cred}{host}:{port}"
    if isinstance(p, dict):
        scheme = str(p.get("proxy_type", "socks5")).lower()
        host = p.get("addr") or p.get("host")
        port = p.get("port")
        user = p.get("username") or p.get("user")
        pw = p.get("password") or p.get("pass")
        cred = ""
        if user:
            cred = f"{user}:{pw}@" if pw else f"{user}@"
        return f"{scheme}://{cred}{host}:{port}"
    return None


class _WsReader:
    def __init__(self, ws, cipher):
        self._ws = ws
        self._cipher = cipher
        self._buf = bytearray()

    async def readexactly(self, n):
        while len(self._buf) < n:
            raw = await self._ws.recv()
            if isinstance(raw, str):
                raw = raw.encode()
            dec = self._cipher.decrypt(raw)
            if _DEBUG:
                print(f"[ws-r] dec {len(dec)}B: {dec[:64].hex()}")
            self._buf.extend(dec)
        out = bytes(self._buf[:n])
        del self._buf[:n]
        return out

    def at_eof(self):
        return False


class _WsWriter:
    def __init__(self, ws, cipher):
        self._ws = ws
        self._cipher = cipher
        self._pending = bytearray()

    def write(self, data):
        if _DEBUG and data:
            print(f"[ws-w] plain {len(data)}B: {data[:64].hex()}")
        self._pending.extend(self._cipher.encrypt(data))

    async def drain(self):
        if self._pending:
            await self._ws.send(bytes(self._pending))
            self._pending.clear()

    def close(self):
        pass

    async def wait_closed(self):
        pass


class ConnectionWebSocketAbridgedObfuscated(ConnectionTcpAbridged):
    def __init__(self, ip, port, dc_id, *, loggers, proxy=None, url=None, **kwargs):
        super().__init__(ip, port, dc_id, loggers=loggers, proxy=None, **kwargs)
        self._url = url or DEFAULT_URL
        self._ws_proxy = _coerce_proxy(proxy)
        self._ws = None

    async def _connect(self, timeout=None, **kwargs):
        proxy = self._ws_proxy or _PROXY_URL
        connect_kwargs = dict(
            subprotocols=["binary"],
            max_size=None,
            open_timeout=timeout or 15,
            ping_interval=None,
        )
        if proxy:
            connect_kwargs["proxy"] = proxy
            if _DEBUG:
                print(f"[ws] proxy: {proxy}")
        self._ws = await ws_connect(self._url, **connect_kwargs)

        while True:
            buf = bytearray(os.urandom(64))
            first = int.from_bytes(buf[0:4], "little")
            if buf[0] != 0xef and first not in RESERVED:
                break

        buf[56:60] = b"\xef\xef\xef\xef"
        buf[60:62] = self._dc_id.to_bytes(2, "little")

        enc_key = bytes(buf[8:40])
        enc_iv = bytes(buf[40:56])
        rev = bytes(buf)[::-1]
        dec_key = rev[8:40]
        dec_iv = rev[40:56]

        send_cipher = AES.new(enc_key, AES.MODE_CTR,
                              nonce=b"", initial_value=enc_iv)
        recv_cipher = AES.new(dec_key, AES.MODE_CTR,
                              nonce=b"", initial_value=dec_iv)

        enc_all = send_cipher.encrypt(bytes(buf))
        buf[56:64] = enc_all[56:64]
        await self._ws.send(bytes(buf))

        self._codec = self.packet_codec(self)
        self._reader = _WsReader(self._ws, recv_cipher)
        self._writer = _WsWriter(self._ws, send_cipher)
        self._connected = True

    async def disconnect(self, **kwargs):
        self._connected = False
        if self._ws is not None:
            try:
                await self._ws.close()
            except Exception as e:
                print(f"[ws] error: {e}")
            self._ws = None
