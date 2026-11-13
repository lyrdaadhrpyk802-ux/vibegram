# ============================================
#  examples/bot_api_master/bot_008_kick_participant.py - اخراج کاربر
#  All code and comments are English. No emojis.
# ============================================
# این فایل به صورت خودکار برای تست و آموزش متد ربات kick_participant تولید شده است.
# برای اجرای این مثال، توکن ربات خود را جایگزین کنید.

import asyncio
from botapi import VibeBot

BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"

async def main():
    async with VibeBot(token=BOT_TOKEN) as bot:
        print("[+] Bot connected.")
        
        try:
            result = await bot.kick_participant()
            print(f"[+] Method kick_participant executed. Result: {type(result).__name__}")
        except Exception as e:
            print(f"[!] Error executing kick_participant: {type(e).__name__}: {e}")

if __name__ == "__main__":
    asyncio.run(main())
