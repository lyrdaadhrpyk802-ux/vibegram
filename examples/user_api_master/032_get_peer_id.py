# ============================================
#  examples/user_api_master/032_get_peer_id.py - دریافت آیدی
#  All code and comments are English. No emojis.
# ============================================
# این فایل به صورت خودکار برای تست و آموزش متد get_peer_id تولید شده است.
# برای اجرای این مثال، مطمئن شوید که لاگین هستید.

import asyncio
from userapi import VibeClient

async def main():
    async with VibeClient() as client:
        print("[+] Connected to Vibe.")
        
        try:
            # فراخوانی متد با پارامترهای پیش‌فرض
            # توجه: برخی متدها نیاز به ورودی خاصی دارند که باید در کد جایگزین شود.
            result = await client.get_peer_id()
            print(f"[+] Method get_peer_id executed successfully. Result: {type(result).__name__}")
        except Exception as e:
            print(f"[!] Error executing get_peer_id: {type(e).__name__}: {e}")

if __name__ == "__main__":
    asyncio.run(main())
