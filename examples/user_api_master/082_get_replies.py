# ============================================
#  examples/user_api_master/082_get_replies.py - دریافت پاسخ‌های یک پیام
#  All code and comments are English. No emojis.
# ============================================
# این فایل به صورت خودکار برای تست و آموزش متد get_replies تولید شده است.
# برای اجرای این مثال، مطمئن شوید که لاگین هستید.

import asyncio
from userapi import VibeClient

async def main():
    async with VibeClient() as client:
        print("[+] Connected to Vibe.")
        
        try:
            # فراخوانی متد با پارامترهای پیش‌فرض
            result = await client.get_replies()
            print(f"[+] Method get_replies executed successfully. Result: {type(result).__name__}")
        except Exception as e:
            print(f"[!] Error executing get_replies: {type(e).__name__}: {e}")

if __name__ == "__main__":
    asyncio.run(main())
