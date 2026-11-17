# ============================================
#  examples/http_bot/05_file_download.py - Download files by file_id
#  All code and comments are English. No emojis.
# ============================================
import asyncio
import os
import sys
from pathlib import Path

from botapi import VibeBotHTTP

async def main():
    token = os.getenv("VIBE_BOT_TOKEN", "").strip()
    if not token:
        print("[file_download] error: set VIBE_BOT_TOKEN environment variable")
        sys.exit(1)

    async with VibeBotHTTP(token) as bot:
        print("[file_download] polling updates...")
        async for update in bot.poll_updates(timeout=30):
            msg = update.get("message")
            if not msg:
                continue

            photos = msg.get("photo")
            if photos:
                chat_id = msg["chat"]["id"]
                file_id = max(photos, key=lambda p: p.get("file_size", 0))["file_id"]
                dest = Path(f"downloaded_{msg['message_id']}.png")

                await bot.send_message(chat_id=chat_id, text="Downloading your photo...")
                try:
                    await bot.download_file(file_id=file_id, dest=dest)
                    await bot.send_message(chat_id=chat_id, text=f"Saved to {dest.absolute()}")
                except Exception as e:
                    await bot.send_message(chat_id=chat_id, text=f"Download failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
