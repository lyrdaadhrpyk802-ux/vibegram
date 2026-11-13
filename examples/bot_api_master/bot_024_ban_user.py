# ============================================
#  examples/bot_api_master/bot_024_ban_user.py - بن کردن
#  All code and comments are English. No emojis.
# ============================================
# این فایل به صورت خودکار برای تست و آموزش متد ربات ban_user تولید شده است.
# برای اجرای این مثال، توکن ربات خود را جایگزین کنید.

import asyncio
from botapi import VibeBot

BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"

async def main():
    async with VibeBot(token=BOT_TOKEN) as bot:
        print("[+] Bot connected.")
        
        try:
            result = await bot.ban_user()
            print(f"[+] Method ban_user executed. Result: {type(result).__name__}")
        except Exception as e:
            print(f"[!] Error executing ban_user: {type(e).__name__}: {e}")

if __name__ == "__main__":
    asyncio.run(main())
