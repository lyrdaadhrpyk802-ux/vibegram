# ============================================
#  examples/bots/advanced_bot.py - Full Feature Bot
#  All code and comments are English. No emojis.
# ============================================
import asyncio
import sys
from botapi import VibeBot
from botapi.keyboards import ReplyKeyboard
from telethon import events

BOT_TOKEN = "1780243525:rfPx6zSuVGUoCfoISwunFTyLLIYQ94I_YxP"

async def main():
    bot = VibeBot(token=BOT_TOKEN)
    
    async with bot:
        me = await bot.get_me()
        print(f"[+] Advanced Bot @{me.username} is running!")
        
        # 1. Set bot commands (menu)
        await bot.set_commands([
            ("start", "Show menu"),
            ("help", "Get help")
        ])
        print("[+] Bot commands menu updated.")

        @bot.raw.on(events.NewMessage(incoming=True))
        async def message_handler(event):
            text = event.raw_text.strip().lower()
            
            if text == "/start":
                await event.reply("Welcome! Please choose an option:", buttons=ReplyKeyboard().add("Option 1").add("Option 2").row().build())
            elif text == "/help":
                await event.reply("This is a help message.")
            else:
                # Show typing status before doing long work
                await bot.send_typing(event.chat_id)
                await asyncio.sleep(1.5) # Simulate a delay
                await event.reply(f"You said: {text}")

        try:
            await bot.run_until_disconnected()
        except asyncio.CancelledError:
            print("\n[i] Bot disconnected cleanly.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(0)
