# pyvibe

Python client library for Vibe Messenger (vibegram.chat).
MTProto over WebSocket with Vibe's custom authentication scheme.

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
cd pyvibe
pip install -e .

## Quick Start
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

## Documentation
- ARCHITECTURE.md - Technical details of transport and auth.
- VIBE_COMPAT.md - Feature support matrix.
- examples/ - 11 guided examples with Persian comments.

## License
MIT License
