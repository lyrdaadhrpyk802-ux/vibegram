# ============================================
#  examples/bot_api_master/bot_017_set_bot_description.py - تنظیم توضیحات
#  All code and comments are English. No emojis.
# ============================================
# این فایل به صورت خودکار برای تست و آموزش متد ربات set_bot_description تولید شده است.
# برای اجرای این مثال، توکن ربات خود را جایگزین کنید.

import asyncio
from botapi import VibeBot

BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"

async def main():
    async with VibeBot(token=BOT_TOKEN) as bot:
        print("[+] Bot connected.")
        
        try:
            result = await bot.set_bot_description()
            print(f"[+] Method set_bot_description executed. Result: {type(result).__name__}")
        except Exception as e:
            print(f"[!] Error executing set_bot_description: {type(e).__name__}: {e}")

if __name__ == "__main__":
    asyncio.run(main())
