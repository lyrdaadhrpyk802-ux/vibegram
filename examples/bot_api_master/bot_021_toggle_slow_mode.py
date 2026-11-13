# ============================================
#  examples/bot_api_master/bot_021_toggle_slow_mode.py - حالت آهسته
#  All code and comments are English. No emojis.
# ============================================
# این فایل به صورت خودکار برای تست و آموزش متد ربات toggle_slow_mode تولید شده است.
# برای اجرای این مثال، توکن ربات خود را جایگزین کنید.

import asyncio
from botapi import VibeBot

BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"

async def main():
    async with VibeBot(token=BOT_TOKEN) as bot:
        print("[+] Bot connected.")
        
        try:
            result = await bot.toggle_slow_mode()
            print(f"[+] Method toggle_slow_mode executed. Result: {type(result).__name__}")
        except Exception as e:
            print(f"[!] Error executing toggle_slow_mode: {type(e).__name__}: {e}")

if __name__ == "__main__":
    asyncio.run(main())
