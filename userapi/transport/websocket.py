# ============================================
#  userapi/transport/websocket.py - WebSocket transport
#  All code and comments are English. No emojis.
# ============================================
import struct
import time
from Crypto.Cipher import AES
import websockets

from userapi.crypto.obfuscated import build_init


DEFAULT_URL = "wss://apiws.vibegram.chat/apiws"


def _msg_id() -> bytes:
    """Time-based MTProto msg_id, divisible by 4."""
    now = time.time()
    secs = int(now)
    micros = int((now - secs) * 1e6)
    return ((secs << 32) | (micros << 2) & 0xFFFFFFFC).to_bytes(8, 'little')


def _frame_abridged(body: bytes, cipher: AES) -> bytes:
    """Wrap body in abridged framing (length in words), then encrypt."""
    enc = cipher.encrypt(body)
    return bytes([len(body) // 4]) + enc


class WebSocketTransport:
    """Single-use MTProto transport over WebSocket."""

    def __init__(self, url: str = DEFAULT_URL, dc_id: int = 2):
        self.url = url
        self.dc_id = dc_id
        self._ws = None
        self._dec_key = None
        self._dec_iv = None

    async def connect(self):
        header, cipher, dec = build_init(dc_id=self.dc_id)
        self._dec_key, self._dec_iv = dec
        self._ws = await websockets.connect(
            self.url, subprotocols=["binary"],
            max_size=None, open_timeout=15,
        )
        await self._ws.send(header)
        return self

    async def send_request(self, payload: bytes):
        """Send a req_pq_multi payload (no auth_key_id, no msg_id)."""
        from userapi.crypto.obfuscated import build_init
        # cipher state is consumed at connect; rebuild fresh state here
        # for a single-use connection this is fine
        raise NotImplementedError("use send_raw with fresh cipher")

    async def close(self):
        if self._ws:
            await self._ws.close()
            self._ws = None
