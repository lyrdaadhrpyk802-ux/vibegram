# ============================================
#  examples/user_api_master/088_get_admin_log.py - دریافت لاگ ادمین
#  All code and comments are English. No emojis.
# ============================================
# این فایل به صورت خودکار برای تست و آموزش متد get_admin_log تولید شده است.
# برای اجرای این مثال، مطمئن شوید که لاگین هستید.

import asyncio
from userapi import VibeClient

async def main():
    async with VibeClient() as client:
        print("[+] Connected to Vibe.")
        
        try:
            # فراخوانی متد با پارامترهای پیش‌فرض
            result = await client.get_admin_log()
            print(f"[+] Method get_admin_log executed successfully. Result: {type(result).__name__}")
        except Exception as e:
            print(f"[!] Error executing get_admin_log: {type(e).__name__}: {e}")

if __name__ == "__main__":
    asyncio.run(main())
