# ============================================
#  examples/user_api_master/083_get_pinned_messages.py - همه پیام‌های پین شده
#  All code and comments are English. No emojis.
# ============================================
# این فایل به صورت خودکار برای تست و آموزش متد get_pinned_messages تولید شده است.
# برای اجرای این مثال، مطمئن شوید که لاگین هستید.

import asyncio
from userapi import VibeClient

async def main():
    async with VibeClient() as client:
        print("[+] Connected to Vibe.")
        
        try:
            # فراخوانی متد با پارامترهای پیش‌فرض
            result = await client.get_pinned_messages()
            print(f"[+] Method get_pinned_messages executed successfully. Result: {type(result).__name__}")
        except Exception as e:
            print(f"[!] Error executing get_pinned_messages: {type(e).__name__}: {e}")

if __name__ == "__main__":
    asyncio.run(main())
