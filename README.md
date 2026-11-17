# pyvibe

Python client library for Vibe Messenger (vibegram.chat).
MTProto over WebSocket with Vibe's custom authentication scheme.

## API Modes

This library provides two ways to interact with Vibe Messenger:

1. **MTProto (User & Legacy Bot)**: High-level client wrapping Telethon (`userapi.VibeClient` and `botapi.VibeBot`). Fully reverse-engineered protocol over WebSocket.
2. **HTTP Bot API (`botapi.VibeBotHTTP`)**: A Telegram-compatible HTTP Bot API client. Highly recommended for creating bots, fully supporting inline buttons, file uploads, and webhooks. See `botapi/README.md` for details.

## About the Author
- Name: Ali VEX
- Email: lyrdaadhrpyk802@gmail.com
- GitHub: lyrdaadhrpyk802-ux
- Jabber: @UserBoT

(درباره سازنده: علی، توسعه‌دهنده پایتون. این پروژه در محیط Termux اندروید بدون روت توسعه یافته است.)

## Project Status
- 852 high-level methods available directly on VibeClient.
- Full passthrough to 875 Telethon TL requests (raw API).
- Verified end-to-end: Login, Messaging, Media, Stories, Forums, JSON Backups.

(وضعیت پروژه: کتابخانه به صورت کامل روی سرور Vibe تست شده است. احراز هویت اختصاصی Vibe، ارسال و دریافت مدیا، استوری، فروم و بکاپ‌گیری کاملاً عملیاتی هستند.)

## Installation

```bash
cd pyvibe
pip install -e .
```

## Environment Variables

All sensitive or deployment-specific values are read from the environment,
with safe defaults (Vibe's public app credentials) so the library works
out of the box. Copy `.env.example` to `.env` and override as needed.

| Variable | Default | Purpose |
| --- | --- | --- |
| `VIBE_API_ID` | `4` | Vibe app id used by Telethon. |
| `VIBE_API_HASH` | `014b35b6...` | Vibe app hash used by Telethon. |
| `VIBE_DC_HOST` | `web.vibegram.chat` | Datacenter WebSocket host. |
| `VIBE_DC_PORT` | `443` | Datacenter WebSocket port. |
| `VIBE_DC_ID` | `2` | Datacenter id passed to the session and the auth handshake. |
| `VIBE_TELETHON_STRICT` | `1` | When `0`, an unsupported Telethon version downgrades from a hard error to a warning. |
| `VIBE_DEBUG` | unset | When `1`, re-enables Telethon network logging that is silenced by default. |

Credentials and DC settings can also be passed directly to `VibeClient`:

```python
c = VibeClient(dc_host="mirror.example.com", dc_port=8443,
               dc_id=5, api_id=123, api_hash="abcdef")
```

## Quick Start

```python
import asyncio
from userapi import VibeClient

async def main():
    c = VibeClient()
    await c.connect()

    if not await c.is_authorized():
        phone = input("Phone: ")
        await c.request_code(phone)
        code = input("OTP: ")
        await c.sign_in(phone, code)

    me = await c.get_me()
    print(f"Logged in as {me.first_name}")

    await c.send_message("me", "Hello from pyvibe")
    await c.disconnect()

asyncio.run(main())
```

## Security

- **Never hardcode** phone numbers, bot tokens, 2FA passwords, or API
  credentials. Always read them from the environment (`os.getenv`) or pass
  them as arguments. See `.env.example` for the supported variables.
- **Session files** (`*.session`, `*.session-journal`, `*.session-wm/wal`)
  contain live login material and must never be committed. They are listed
  in `.gitignore`.
- The Vibe authentication scheme was reverse-engineered from network
  traffic and has not received an independent cryptographic audit. Treat
  the transport as trusted only for Vibe's own servers. See `SECURITY.md`
  for the full policy and reporting instructions.

## Telethon Version Pinning and Upgrade Path

`vibegram` patches two Telethon internals at runtime:

- `telethon.tl.types.PQInnerData` (`__init__`, `_bytes`, `CONSTRUCTOR_ID`)
- `telethon.crypto.rsa.encrypt`

To avoid silent breakage on upgrade, Telethon is pinned to
`>=1.36,<2.0` in `pyproject.toml` and `requirements.txt`, and a version
guard in `userapi/crypto/vibe_auth.py` raises `RuntimeError` if a build
outside that range is loaded (set `VIBE_TELETHON_STRICT=0` to downgrade to
a warning).

The original attributes are captured when patches are applied and can be
restored at any time:

```python
from userapi import apply_patches, unapply_patches

apply_patches()    # idempotent; called automatically on `import userapi`
unapply_patches()  # restore pristine Telethon behavior
```

When upgrading Telethon:

1. Bump the pin in `pyproject.toml` and `requirements.txt`.
2. Run `python scripts/check_syntax.py`.
3. Run `pytest -v` — `tests/test_vibe_auth.py` exercises the patch surface
   and will fail loudly if the layout changed.
4. If the tests pass, the new version is safe to ship.

## Testing

```bash
pip install -e ".[dev]"
pytest -v          # run the suite
python scripts/check_syntax.py   # ast.parse guard for every .py file
```

CI (`.github/workflows/ci.yml`) runs the syntax gate and the full test
suite on every push and pull request.

## Documentation
- ARCHITECTURE.md - Technical details of transport and auth.
- VIBE_COMPAT.md - Feature support matrix.
- SECURITY.md - Security policy and reporting.
- examples/ - Guided examples with Persian comments.


## Development Notes (Project Origin)

This library was entirely conceived, reverse-engineered, and developed on an **Android device using Termux**, without access to a traditional PC or root privileges.

The challenge involved analyzing captured network traffic to reverse-engineer Vibe's custom authentication scheme (RSA and obfuscated2), successfully implementing it in Python, and wrapping it around the Telethon framework to provide over 850 high-level methods.

This project proves that a complete, production-ready SDK can be built entirely from a mobile environment.

> **یادداشت توسعه:**
> این کتابخانه به طور کامل روی یک گوشی اندروید (در محیط Termux و بدون روت) و بدون دسترسی به کامپیوتر نوشته شده است. چالش اصلی، مهندسی معکوس الگوریتم احراز هویت اختصاصی سرور وایب بود که با تحلیل ترافیک شبکه انجام شد. این پروژه اثبات می‌کند که می‌توان یک کتابخانه حرفه‌ای و کامل را تنها با یک گوشی موبایل توسعه داد.

## License
MIT License
