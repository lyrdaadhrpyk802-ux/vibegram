# Architecture

## Layer Stack

VibeClient (userapi/client.py)
-> TelegramClient (Telethon 1.45.0)
-> ConnectionWebSocketAbridgedObfuscated (userapi/connection/telethon_ws.py)
-> WebSocket (wss://apiws.vibegram.chat/apiws)

## Transport Layer
- Protocol: obfuscated2 + abridged framing.
- Encryption: AES-CTR.
- Endpoint: wss://apiws.vibegram.chat/apiws

Key derivation (verified against captured traffic):
enc_key = header[8:40]
enc_iv = header[40:56]
dec_key = reverse(header)[8:40]
dec_iv = reverse(header)[40:56]

## Vibe Custom Authentication
Vibe uses a non-standard variant of the MTProto DH exchange:
1. PQInnerData: Replaced by p_q_inner_data_dc (0xa9f55f95) with an additional dc field.
2. RSA Encryption: The req_DH_params payload uses a custom scheme:
   - Pad p_q_inner_data_dc to 192 bytes with random data.
   - Reverse the padded buffer.
   - Loop: Generate 32-byte key (t), compute sha256(t + padded), apply AES-IGE with zero IV.
   - XOR the key with the hash, append the AES output.
   - Apply raw RSA encryption (no PKCS#1 padding).

## RSA Key
- Fingerprint: -7080122280541503745
- Extracted from libtmessages.49.so (Key 2 of 4).
- Registered via userapi/connection/vibe_keys.py.
