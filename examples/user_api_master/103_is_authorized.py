# ============================================
#  examples/user_api_master/103_is_authorized.py - بررسی لاگین بودن
#  All code and comments are English. No emojis.
# ============================================
# این فایل به صورت خودکار برای تست و آموزش متد is_authorized تولید شده است.
# برای اجرای این مثال، مطمئن شوید که لاگین هستید.

import asyncio
from userapi import VibeClient

async def main():
    async with VibeClient() as client:
        print("[+] Connected to Vibe.")
        
        try:
            # فراخوانی متد با پارامترهای پیش‌فرض
            result = await client.is_authorized()
            print(f"[+] Method is_authorized executed successfully. Result: {type(result).__name__}")
        except Exception as e:
            print(f"[!] Error executing is_authorized: {type(e).__name__}: {e}")

if __name__ == "__main__":
    asyncio.run(main())
