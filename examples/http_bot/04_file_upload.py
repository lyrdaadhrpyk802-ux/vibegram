# ============================================
#  examples/http_bot/04_file_upload.py - Upload photos, documents, and albums
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
        print("[file_upload] error: set VIBE_BOT_TOKEN environment variable")
        sys.exit(1)

    png_path = Path("test_image.png")
    if not png_path.exists():
        png_path.write_bytes(bytes.fromhex(
            "89504e470d0a1a0a0000000d494844520000000100000001"
            "08060000001f15c4890000000d49444154789c6360000000"
            "0005000156a6b4b70000000049454e44ae426082"
        ))

    txt_path = Path("test_doc.txt")
    if not txt_path.exists():
        txt_path.write_text("Hello from Vibe Bot HTTP API!")

    async with VibeBotHTTP(token) as bot:
        print("[file_upload] polling updates...")
        async for update in bot.poll_updates(timeout=30):
            msg = update.get("message")
            if msg and msg.get("text") == "/start":
                chat_id = msg["chat"]["id"]
                print(f"[file_upload] sending files to {chat_id}")

                await bot.send_photo(chat_id=chat_id, photo=png_path, caption="This is a PNG")

                await bot.send_document(
                    chat_id=chat_id,
                    document=txt_path.read_bytes(),
                    caption="This is a text document sent from bytes"
                )

                await bot.send_media_group(
                    chat_id=chat_id,
                    media=[
                        {"type": "photo", "media": png_path, "caption": "Album item 1"},
                        {"type": "photo", "media": png_path, "caption": "Album item 2"},
                    ]
                )

if __name__ == "__main__":
    asyncio.run(main())
