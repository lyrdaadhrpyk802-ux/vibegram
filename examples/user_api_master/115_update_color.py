# ============================================
#  examples/user_api_master/115_update_color.py - بروزرسانی رنگ پروفایل
#  All code and comments are English. No emojis.
# ============================================
# این فایل به صورت خودکار برای تست و آموزش متد update_color تولید شده است.
# برای اجرای این مثال، مطمئن شوید که لاگین هستید.

import asyncio
from userapi import VibeClient

async def main():
    async with VibeClient() as client:
        print("[+] Connected to Vibe.")
        
        try:
            # فراخوانی متد با پارامترهای پیش‌فرض
            result = await client.update_color()
            print(f"[+] Method update_color executed successfully. Result: {type(result).__name__}")
        except Exception as e:
            print(f"[!] Error executing update_color: {type(e).__name__}: {e}")

if __name__ == "__main__":
    asyncio.run(main())
