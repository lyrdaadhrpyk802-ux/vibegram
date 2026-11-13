# ============================================
#  examples/bot_api_master/bot_005_send_document.py - ارسال فایل
#  All code and comments are English. No emojis.
# ============================================
# این فایل به صورت خودکار برای تست و آموزش متد ربات send_document تولید شده است.
# برای اجرای این مثال، توکن ربات خود را جایگزین کنید.

import asyncio
from botapi import VibeBot

BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"

async def main():
    async with VibeBot(token=BOT_TOKEN) as bot:
        print("[+] Bot connected.")
        
        try:
            result = await bot.send_document()
            print(f"[+] Method send_document executed. Result: {type(result).__name__}")
        except Exception as e:
            print(f"[!] Error executing send_document: {type(e).__name__}: {e}")

if __name__ == "__main__":
    asyncio.run(main())
