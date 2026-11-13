# ============================================
#  examples/24_privacy.py - Privacy Settings
#  All code and comments are English. No emojis.
# ============================================
# این مثال نشان می‌دهد چطور تنظیمات حریم خصوصی (آخرین بازدید) را تغییر دهید.

import asyncio
from userapi import VibeClient
from telethon.tl.types import InputPrivacyKeyStatusTimestamp, InputPrivacyValueAllowContacts

async def main():
    async with VibeClient() as client:
        print("[+] متصل شد.")
        
        # تنظیم آخرین بازدید فقط برای مخاطبین
        print("[i] تغییر حریم خصوصی آخرین بازدید...")
        await client.set_privacy(
            key=InputPrivacyKeyStatusTimestamp(),
            rules=[InputPrivacyValueAllowContacts()]
        )
        print("[+] حریم خصوصی به 'فقط مخاطبین' تغییر یافت.")

if __name__ == "__main__":
    asyncio.run(main())
