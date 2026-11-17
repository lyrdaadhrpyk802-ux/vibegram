# ============================================
#  examples/http_bot/07_group_admin.py - Basic group admin commands
#  All code and comments are English. No emojis.
# ============================================
import asyncio
import os
import sys

from botapi import VibeBotHTTP, VibeBotAPIError

async def main():
    token = os.getenv("VIBE_BOT_TOKEN", "").strip()
    if not token:
        print("[group_admin] error: set VIBE_BOT_TOKEN environment variable")
        sys.exit(1)

    async with VibeBotHTTP(token) as bot:
        print("[group_admin] polling updates...")
        async for update in bot.poll_updates(timeout=30):
            msg = update.get("message")
            if not msg or not msg.get("text"):
                continue

            text = msg["text"].strip()
            chat_id = msg["chat"]["id"]
            chat_type = msg["chat"]["type"]

            if chat_type not in ("group", "supergroup"):
                continue

            if text in ("/ban", "/unban") and msg.get("reply_to_message"):
                target_user = msg["reply_to_message"]["from"]["id"]
                try:
                    if text == "/ban":
                        await bot.ban_chat_member(chat_id=chat_id, user_id=target_user)
                        await bot.send_message(chat_id=chat_id, text=f"Banned user {target_user}")
                    else:
                        await bot.unban_chat_member(chat_id=chat_id, user_id=target_user)
                        await bot.send_message(chat_id=chat_id, text=f"Unbanned user {target_user}")
                except VibeBotAPIError as e:
                    await bot.send_message(chat_id=chat_id, text=f"Error: {e.description}")

            elif text == "/pin" and msg.get("reply_to_message"):
                target_msg_id = msg["reply_to_message"]["message_id"]
                await bot.pin_chat_message(chat_id=chat_id, message_id=target_msg_id)
                await bot.send_message(chat_id=chat_id, text="Message pinned.")

            elif text == "/unpin":
                await bot.unpin_chat_message(chat_id=chat_id)
                await bot.send_message(chat_id=chat_id, text="Message unpinned.")

if __name__ == "__main__":
    asyncio.run(main())
