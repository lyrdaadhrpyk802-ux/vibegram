# ============================================
#  examples/user_api_master/112_reorder_usernames.py - مرتب‌سازی یوزرنیم‌ها
#  All code and comments are English. No emojis.
# ============================================
# این فایل به صورت خودکار برای تست و آموزش متد reorder_usernames تولید شده است.
# برای اجرای این مثال، مطمئن شوید که لاگین هستید.

import asyncio
from userapi import VibeClient

async def main():
    async with VibeClient() as client:
        print("[+] Connected to Vibe.")
        
        try:
            # فراخوانی متد با پارامترهای پیش‌فرض
            result = await client.reorder_usernames()
            print(f"[+] Method reorder_usernames executed successfully. Result: {type(result).__name__}")
        except Exception as e:
            print(f"[!] Error executing reorder_usernames: {type(e).__name__}: {e}")

if __name__ == "__main__":
    asyncio.run(main())
