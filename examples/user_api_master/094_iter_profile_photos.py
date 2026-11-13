# ============================================
#  examples/user_api_master/094_iter_profile_photos.py - پیمایش عکس‌های پروفایل
#  All code and comments are English. No emojis.
# ============================================
# این فایل به صورت خودکار برای تست و آموزش متد iter_profile_photos تولید شده است.
# برای اجرای این مثال، مطمئن شوید که لاگین هستید.

import asyncio
from userapi import VibeClient

async def main():
    async with VibeClient() as client:
        print("[+] Connected to Vibe.")
        
        try:
            # فراخوانی متد با پارامترهای پیش‌فرض
            result = await client.iter_profile_photos()
            print(f"[+] Method iter_profile_photos executed successfully. Result: {type(result).__name__}")
        except Exception as e:
            print(f"[!] Error executing iter_profile_photos: {type(e).__name__}: {e}")

if __name__ == "__main__":
    asyncio.run(main())
