# ============================================
#  examples/user_api_master/096_request_code.py - درخواست کد
#  All code and comments are English. No emojis.
# ============================================
# این فایل به صورت خودکار برای تست و آموزش متد request_code تولید شده است.
# برای اجرای این مثال، مطمئن شوید که لاگین هستید.

import asyncio
from userapi import VibeClient

async def main():
    async with VibeClient() as client:
        print("[+] Connected to Vibe.")
        
        try:
            # فراخوانی متد با پارامترهای پیش‌فرض
            result = await client.request_code()
            print(f"[+] Method request_code executed successfully. Result: {type(result).__name__}")
        except Exception as e:
            print(f"[!] Error executing request_code: {type(e).__name__}: {e}")

if __name__ == "__main__":
    asyncio.run(main())
