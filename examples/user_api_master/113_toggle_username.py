# ============================================
#  examples/user_api_master/113_toggle_username.py - فعال/غیرفعال یوزرنیم
#  All code and comments are English. No emojis.
# ============================================
# این فایل به صورت خودکار برای تست و آموزش متد toggle_username تولید شده است.
# برای اجرای این مثال، مطمئن شوید که لاگین هستید.

import asyncio
from userapi import VibeClient

async def main():
    async with VibeClient() as client:
        print("[+] Connected to Vibe.")
        
        try:
            # فراخوانی متد با پارامترهای پیش‌فرض
            result = await client.toggle_username()
            print(f"[+] Method toggle_username executed successfully. Result: {type(result).__name__}")
        except Exception as e:
            print(f"[!] Error executing toggle_username: {type(e).__name__}: {e}")

if __name__ == "__main__":
    asyncio.run(main())
