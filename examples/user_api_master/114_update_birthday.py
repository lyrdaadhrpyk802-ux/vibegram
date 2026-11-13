# ============================================
#  examples/user_api_master/114_update_birthday.py - بروزرسانی تاریخ تولد
#  All code and comments are English. No emojis.
# ============================================
# این فایل به صورت خودکار برای تست و آموزش متد update_birthday تولید شده است.
# برای اجرای این مثال، مطمئن شوید که لاگین هستید.

import asyncio
from userapi import VibeClient

async def main():
    async with VibeClient() as client:
        print("[+] Connected to Vibe.")
        
        try:
            # فراخوانی متد با پارامترهای پیش‌فرض
            result = await client.update_birthday()
            print(f"[+] Method update_birthday executed successfully. Result: {type(result).__name__}")
        except Exception as e:
            print(f"[!] Error executing update_birthday: {type(e).__name__}: {e}")

if __name__ == "__main__":
    asyncio.run(main())
