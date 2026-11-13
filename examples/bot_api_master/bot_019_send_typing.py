# ============================================
#  examples/bot_api_master/bot_019_send_typing.py - وضعیت تایپ
#  All code and comments are English. No emojis.
# ============================================
# این فایل به صورت خودکار برای تست و آموزش متد ربات send_typing تولید شده است.
# برای اجرای این مثال، توکن ربات خود را جایگزین کنید.

import asyncio
from botapi import VibeBot

BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"

async def main():
    async with VibeBot(token=BOT_TOKEN) as bot:
        print("[+] Bot connected.")
        
        try:
            result = await bot.send_typing()
            print(f"[+] Method send_typing executed. Result: {type(result).__name__}")
        except Exception as e:
            print(f"[!] Error executing send_typing: {type(e).__name__}: {e}")

if __name__ == "__main__":
    asyncio.run(main())
