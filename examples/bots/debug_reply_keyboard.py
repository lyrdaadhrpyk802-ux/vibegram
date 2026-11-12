# ============================================
#  examples/bots/debug_reply_keyboard.py
#  All code and comments are English. No emojis.
# ============================================
import asyncio
from botapi import VibeBot
from botapi.keyboards import ReplyKeyboard
from telethon import events

BOT_TOKEN = "1780243525:rfPx6zSuVGUoCfoISwunFTyLLIYQ94I_YxP"

async def main():
    bot = VibeBot(token=BOT_TOKEN)
    async with bot:
        print("[+] Bot running. Send a message to test Reply Keyboard.")
        
        @bot.raw.on(events.NewMessage(incoming=True))
        async def handler(event):
            try:
                rkb = ReplyKeyboard(resize=True)
                rkb.add("گزینه اول").add("گزینه دوم").row()
                
                await bot.send_message(
                    event.chat_id, 
                    "این یک منوی پایین صفحه است:", 
                    buttons=rkb.build() # Pass the build object directly
                )
                print("[OK] Reply Keyboard sent successfully!")
            except Exception as e:
                print(f"[FAIL] Reply Keyboard rejected: {e}")

        await bot.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
