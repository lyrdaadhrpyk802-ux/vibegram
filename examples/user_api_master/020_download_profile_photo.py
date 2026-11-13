# ============================================
#  examples/user_api_master/020_download_profile_photo.py - دانلود عکس پروفایل
#  All code and comments are English. No emojis.
# ============================================
# این فایل به صورت خودکار برای تست و آموزش متد download_profile_photo تولید شده است.
# برای اجرای این مثال، مطمئن شوید که لاگین هستید.

import asyncio
from userapi import VibeClient

async def main():
    async with VibeClient() as client:
        print("[+] Connected to Vibe.")
        
        try:
            # فراخوانی متد با پارامترهای پیش‌فرض
            # توجه: برخی متدها نیاز به ورودی خاصی دارند که باید در کد جایگزین شود.
            result = await client.download_profile_photo()
            print(f"[+] Method download_profile_photo executed successfully. Result: {type(result).__name__}")
        except Exception as e:
            print(f"[!] Error executing download_profile_photo: {type(e).__name__}: {e}")

if __name__ == "__main__":
    asyncio.run(main())
