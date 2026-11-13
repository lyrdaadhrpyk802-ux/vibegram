# ============================================
#  examples/user_api_master/111_check_username.py - بررسی آزاد بودن یوزرنیم
#  All code and comments are English. No emojis.
# ============================================
# این فایل به صورت خودکار برای تست و آموزش متد check_username تولید شده است.
# برای اجرای این مثال، مطمئن شوید که لاگین هستید.

import asyncio
from userapi import VibeClient

async def main():
    async with VibeClient() as client:
        print("[+] Connected to Vibe.")
        
        try:
            # فراخوانی متد با پارامترهای پیش‌فرض
            result = await client.check_username()
            print(f"[+] Method check_username executed successfully. Result: {type(result).__name__}")
        except Exception as e:
            print(f"[!] Error executing check_username: {type(e).__name__}: {e}")

if __name__ == "__main__":
    asyncio.run(main())
