# ============================================
#  examples/user_api_master/019_download_file.py - دانلود فایل
#  All code and comments are English. No emojis.
# ============================================
# این فایل به صورت خودکار برای تست و آموزش متد download_file تولید شده است.
# برای اجرای این مثال، مطمئن شوید که لاگین هستید.

import asyncio
from userapi import VibeClient

async def main():
    async with VibeClient() as client:
        print("[+] Connected to Vibe.")
        
        try:
            # فراخوانی متد با پارامترهای پیش‌فرض
            # توجه: برخی متدها نیاز به ورودی خاصی دارند که باید در کد جایگزین شود.
            result = await client.download_file()
            print(f"[+] Method download_file executed successfully. Result: {type(result).__name__}")
        except Exception as e:
            print(f"[!] Error executing download_file: {type(e).__name__}: {e}")

if __name__ == "__main__":
    asyncio.run(main())
