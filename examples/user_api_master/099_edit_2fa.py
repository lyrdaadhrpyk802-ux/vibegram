# ============================================
#  examples/user_api_master/099_edit_2fa.py - تنظیم رمز دو مرحله‌ای
#  All code and comments are English. No emojis.
# ============================================
# این فایل به صورت خودکار برای تست و آموزش متد edit_2fa تولید شده است.
# برای اجرای این مثال، مطمئن شوید که لاگین هستید.

import asyncio
from userapi import VibeClient

async def main():
    async with VibeClient() as client:
        print("[+] Connected to Vibe.")
        
        try:
            # فراخوانی متد با پارامترهای پیش‌فرض
            result = await client.edit_2fa()
            print(f"[+] Method edit_2fa executed successfully. Result: {type(result).__name__}")
        except Exception as e:
            print(f"[!] Error executing edit_2fa: {type(e).__name__}: {e}")

if __name__ == "__main__":
    asyncio.run(main())
