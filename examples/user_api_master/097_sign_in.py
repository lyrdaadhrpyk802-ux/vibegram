# ============================================
#  examples/user_api_master/097_sign_in.py - ورود
#  All code and comments are English. No emojis.
# ============================================
# این فایل به صورت خودکار برای تست و آموزش متد sign_in تولید شده است.
# برای اجرای این مثال، مطمئن شوید که لاگین هستید.

import asyncio
from userapi import VibeClient

async def main():
    async with VibeClient() as client:
        print("[+] Connected to Vibe.")
        
        try:
            # فراخوانی متد با پارامترهای پیش‌فرض
            result = await client.sign_in()
            print(f"[+] Method sign_in executed successfully. Result: {type(result).__name__}")
        except Exception as e:
            print(f"[!] Error executing sign_in: {type(e).__name__}: {e}")

if __name__ == "__main__":
    asyncio.run(main())
