# ============================================
#  examples/22_stickers.py - Stickers Management
#  All code and comments are English. No emojis.
# ============================================
# این مثال نشان می‌دهد چطور استیکرهای نصب شده را ببینید و یک استیکر بفرستید.

import asyncio
from userapi import VibeClient

async def main():
    async with VibeClient() as client:
        print("[+] متصل شد.")
        
        # ۱. گرفتن لیست استیکرهای نصب شده
        print("[i] دریافت استیکرها...")
        stickers = await client.get_my_stickers()
        
        if not stickers:
            print("[-] شما هیچ استیکری نصب نکرده‌اید.")
            return

        first_set = stickers[0]
        print(f"[+] اولین پک استیکر شما: {first_set.title}")
        
        # ۲. فرستادن اولین استیکر از آن پک (اگر وجود داشته باشد)
        # نکته: برای ارسال استیکر، به فایل استیکر نیاز است
        # await client.send_file("me", first_set.documents[0])

if __name__ == "__main__":
    asyncio.run(main())
