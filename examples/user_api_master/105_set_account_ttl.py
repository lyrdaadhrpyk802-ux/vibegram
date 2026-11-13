# ============================================
#  examples/user_api_master/105_set_account_ttl.py - تنظیم مدت زمان حذف
#  All code and comments are English. No emojis.
# ============================================
# این فایل به صورت خودکار برای تست و آموزش متد set_account_ttl تولید شده است.
# برای اجرای این مثال، مطمئن شوید که لاگین هستید.

import asyncio
from userapi import VibeClient

async def main():
    async with VibeClient() as client:
        print("[+] Connected to Vibe.")
        
        try:
            # فراخوانی متد با پارامترهای پیش‌فرض
            result = await client.set_account_ttl()
            print(f"[+] Method set_account_ttl executed successfully. Result: {type(result).__name__}")
        except Exception as e:
            print(f"[!] Error executing set_account_ttl: {type(e).__name__}: {e}")

if __name__ == "__main__":
    asyncio.run(main())
