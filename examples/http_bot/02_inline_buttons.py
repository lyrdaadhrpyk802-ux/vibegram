# ============================================
#  examples/http_bot/02_inline_buttons.py - Inline buttons (callback & url)
#  All code and comments are English. No emojis.
# ============================================
import asyncio
import os
import sys

from botapi import VibeBotHTTP

async def main():
    token = os.getenv("VIBE_BOT_TOKEN", "").strip()
    if not token:
        print("[inline_buttons] error: set VIBE_BOT_TOKEN environment variable")
        sys.exit(1)

    async with VibeBotHTTP(token) as bot:
        print("[inline_buttons] polling updates...")
        async for update in bot.poll_updates(timeout=30):
            msg = update.get("message")
            if msg and msg.get("text"):
                chat_id = msg["chat"]["id"]
                if msg["text"] == "/start":
                    await bot.send_message(
                        chat_id=chat_id,
                        text="Choose an option:",
                        reply_markup={
                            "inline_keyboard": [
                                [{"text": "Button 1", "callback_data": "btn1"}],
                                [{"text": "Website", "url": "https://vibegram.chat"}],
                            ]
                        }
                    )
                else:
                    await bot.send_message(chat_id=chat_id, text=f"echo: {msg['text']}")

            cq = update.get("callback_query")
            if cq:
                await bot.answer_callback_query(
                    callback_query_id=cq["id"],
                    text=f"You pressed {cq['data']}",
                    show_alert=True
                )
                await bot.send_message(
                    chat_id=cq["message"]["chat"]["id"],
                    text=f"Callback received: {cq['data']}"
                )

if __name__ == "__main__":
    asyncio.run(main())
