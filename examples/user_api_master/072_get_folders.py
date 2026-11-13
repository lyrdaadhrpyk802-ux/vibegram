# ============================================
#  examples/user_api_master/072_get_folders.py - لیست فولدرها
#  All code and comments are English. No emojis.
# ============================================
# این فایل به صورت خودکار برای تست و آموزش متد get_folders تولید شده است.
# برای اجرای این مثال، مطمئن شوید که لاگین هستید.

import asyncio
from userapi import VibeClient

async def main():
    async with VibeClient() as client:
        print("[+] Connected to Vibe.")
        
        try:
            # فراخوانی متد با پارامترهای پیش‌فرض
            # توجه: برخی متدها نیاز به ورودی خاصی دارند که باید در کد جایگزین شود.
            result = await client.get_folders()
            print(f"[+] Method get_folders executed successfully. Result: {type(result).__name__}")
        except Exception as e:
            print(f"[!] Error executing get_folders: {type(e).__name__}: {e}")

if __name__ == "__main__":
    asyncio.run(main())
