# ============================================
#  examples/user_api_master/091_get_stats.py - آمار کانال
#  All code and comments are English. No emojis.
# ============================================
# این فایل به صورت خودکار برای تست و آموزش متد get_stats تولید شده است.
# برای اجرای این مثال، مطمئن شوید که لاگین هستید.

import asyncio
from userapi import VibeClient

async def main():
    async with VibeClient() as client:
        print("[+] Connected to Vibe.")
        
        try:
            # فراخوانی متد با پارامترهای پیش‌فرض
            result = await client.get_stats()
            print(f"[+] Method get_stats executed successfully. Result: {type(result).__name__}")
        except Exception as e:
            print(f"[!] Error executing get_stats: {type(e).__name__}: {e}")

if __name__ == "__main__":
    asyncio.run(main())
