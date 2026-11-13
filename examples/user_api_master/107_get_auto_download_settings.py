# ============================================
#  examples/user_api_master/107_get_auto_download_settings.py - تنظیمات دانلود خودکار
#  All code and comments are English. No emojis.
# ============================================
# این فایل به صورت خودکار برای تست و آموزش متد get_auto_download_settings تولید شده است.
# برای اجرای این مثال، مطمئن شوید که لاگین هستید.

import asyncio
from userapi import VibeClient

async def main():
    async with VibeClient() as client:
        print("[+] Connected to Vibe.")
        
        try:
            # فراخوانی متد با پارامترهای پیش‌فرض
            result = await client.get_auto_download_settings()
            print(f"[+] Method get_auto_download_settings executed successfully. Result: {type(result).__name__}")
        except Exception as e:
            print(f"[!] Error executing get_auto_download_settings: {type(e).__name__}: {e}")

if __name__ == "__main__":
    asyncio.run(main())
