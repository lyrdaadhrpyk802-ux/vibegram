# ============================================
#  examples/user_api_master/054_get_chat_history.py - تاریخچه چت
#  All code and comments are English. No emojis.
# ============================================
# این فایل به صورت خودکار برای تست و آموزش متد get_chat_history تولید شده است.
# برای اجرای این مثال، مطمئن شوید که لاگین هستید.

import asyncio
from userapi import VibeClient

async def main():
    async with VibeClient() as client:
        print("[+] Connected to Vibe.")
        
        try:
            # فراخوانی متد با پارامترهای پیش‌فرض
            # توجه: برخی متدها نیاز به ورودی خاصی دارند که باید در کد جایگزین شود.
            result = await client.get_chat_history()
            print(f"[+] Method get_chat_history executed successfully. Result: {type(result).__name__}")
        except Exception as e:
            print(f"[!] Error executing get_chat_history: {type(e).__name__}: {e}")

if __name__ == "__main__":
    asyncio.run(main())
