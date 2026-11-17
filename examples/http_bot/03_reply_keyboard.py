# ============================================
#  examples/http_bot/03_reply_keyboard.py - Reply keyboard (bottom buttons)
#  All code and comments are English. No emojis.
# ============================================
import asyncio
import os
import sys

from botapi import VibeBotHTTP

async def main():
    token = os.getenv("VIBE_BOT_TOKEN", "").strip()
    if not token:
        print("[reply_keyboard] error: set VIBE_BOT_TOKEN environment variable")
        sys.exit(1)

    async with VibeBotHTTP(token) as bot:
        print("[reply_keyboard] polling updates...")
        async for update in bot.poll_updates(timeout=30):
            msg = update.get("message")
            if not msg:
                continue
            text = msg.get("text")
            chat_id = msg["chat"]["id"]

            if text == "/start":
                await bot.send_message(
                    chat_id=chat_id,
                    text="Welcome. Please choose an option below:",
                    reply_markup={
                        "keyboard": [
                            [{"text": "Option A"}, {"text": "Option B"}],
                            [{"text": "Help"}],
                        ],
                        "resize_keyboard": True,
                        "one_time_keyboard": False,
                    }
                )
            elif text in ("Option A", "Option B", "Help"):
                await bot.send_message(chat_id=chat_id, text=f"You selected: {text}")
            else:
                await bot.send_message(chat_id=chat_id, text=f"Unknown command: {text}")

if __name__ == "__main__":
    asyncio.run(main())
