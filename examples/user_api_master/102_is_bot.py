# ============================================
#  examples/user_api_master/102_is_bot.py - بررسی ربات بودن
#  All code and comments are English. No emojis.
# ============================================
# این فایل به صورت خودکار برای تست و آموزش متد is_bot تولید شده است.
# برای اجرای این مثال، مطمئن شوید که لاگین هستید.

import asyncio
from userapi import VibeClient

async def main():
    async with VibeClient() as client:
        print("[+] Connected to Vibe.")
        
        try:
            # فراخوانی متد با پارامترهای پیش‌فرض
            result = await client.is_bot()
            print(f"[+] Method is_bot executed successfully. Result: {type(result).__name__}")
        except Exception as e:
            print(f"[!] Error executing is_bot: {type(e).__name__}: {e}")

if __name__ == "__main__":
    asyncio.run(main())
