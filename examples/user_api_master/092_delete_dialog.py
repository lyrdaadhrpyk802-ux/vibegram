# ============================================
#  examples/user_api_master/092_delete_dialog.py - حذف دیالوگ
#  All code and comments are English. No emojis.
# ============================================
# این فایل به صورت خودکار برای تست و آموزش متد delete_dialog تولید شده است.
# برای اجرای این مثال، مطمئن شوید که لاگین هستید.

import asyncio
from userapi import VibeClient

async def main():
    async with VibeClient() as client:
        print("[+] Connected to Vibe.")
        
        try:
            # فراخوانی متد با پارامترهای پیش‌فرض
            result = await client.delete_dialog()
            print(f"[+] Method delete_dialog executed successfully. Result: {type(result).__name__}")
        except Exception as e:
            print(f"[!] Error executing delete_dialog: {type(e).__name__}: {e}")

if __name__ == "__main__":
    asyncio.run(main())
