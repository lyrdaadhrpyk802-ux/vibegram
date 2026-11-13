# ============================================
#  examples/bot_api_master/bot_018_set_bot_about.py - تنظیم بیوگرافی
#  All code and comments are English. No emojis.
# ============================================
# این فایل به صورت خودکار برای تست و آموزش متد ربات set_bot_about تولید شده است.
# برای اجرای این مثال، توکن ربات خود را جایگزین کنید.

import asyncio
from botapi import VibeBot

BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"

async def main():
    async with VibeBot(token=BOT_TOKEN) as bot:
        print("[+] Bot connected.")
        
        try:
            result = await bot.set_bot_about()
            print(f"[+] Method set_bot_about executed. Result: {type(result).__name__}")
        except Exception as e:
            print(f"[!] Error executing set_bot_about: {type(e).__name__}: {e}")

if __name__ == "__main__":
    asyncio.run(main())
