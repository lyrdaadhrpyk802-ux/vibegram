# ============================================
#  examples/user_api_master/089_edit_admin.py - ویرایش ادمین
#  All code and comments are English. No emojis.
# ============================================
# این فایل به صورت خودکار برای تست و آموزش متد edit_admin تولید شده است.
# برای اجرای این مثال، مطمئن شوید که لاگین هستید.

import asyncio
from userapi import VibeClient

async def main():
    async with VibeClient() as client:
        print("[+] Connected to Vibe.")
        
        try:
            # فراخوانی متد با پارامترهای پیش‌فرض
            result = await client.edit_admin()
            print(f"[+] Method edit_admin executed successfully. Result: {type(result).__name__}")
        except Exception as e:
            print(f"[!] Error executing edit_admin: {type(e).__name__}: {e}")

if __name__ == "__main__":
    asyncio.run(main())
