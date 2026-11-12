# ============================================
#  examples/bots/debug_buttons.py - Isolate button issue
#  All code and comments are English. No emojis.
# ============================================
import asyncio
from botapi import VibeBot, InlineKeyboard
from telethon import events

BOT_TOKEN = "1780243525:rfPx6zSuVGUoCfoISwunFTyLLIYQ94I_YxP"

async def main():
    bot = VibeBot(token=BOT_TOKEN)
    async with bot:
        print("[+] Bot running. Send a message.")
        
        @bot.raw.on(events.NewMessage(incoming=True))
        async def handler(event):
            # 1. Try plain text (no buttons)
            try:
                await event.reply("Step 1: Plain text is OK")
                print("[OK] Plain text sent")
            except Exception as e:
                print(f"[FAIL] Plain text: {e}")
                return

            # 2. Try inline button
            try:
                kb = InlineKeyboard().add("Test", data="t1").row()
                await event.reply("Step 2: Button", buttons=kb.build())
                print("[OK] Button sent successfully!")
            except Exception as e:
                print(f"[FAIL] Button rejected: {e}")

        await bot.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
