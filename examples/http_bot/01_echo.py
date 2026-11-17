# ============================================
#  examples/http_bot/echo_bot.py - Echo bot via Vibe Bot HTTP API
#  Reads token from VIBE_BOT_TOKEN env var.
#  Long polls getUpdates and echoes every text message.
# ============================================
import asyncio
import os
import sys

from botapi import VibeBotHTTP, VibeBotAPIError


async def main():
    token = os.getenv("VIBE_BOT_TOKEN", "").strip()
    if not token:
        print("[echo_bot] error: set VIBE_BOT_TOKEN environment variable")
        sys.exit(1)

    async with VibeBotHTTP(token) as bot:
        try:
            me = await bot.get_me()
        except (VibeBotAPIError, ConnectionError) as e:
            print(f"[echo_bot] error: getMe failed: {e}")
            sys.exit(1)

        username = me.get("username", "-")
        first_name = me.get("first_name", "-")
        print(f"[echo_bot] connected as {first_name} (@{username})")
        print("[echo_bot] polling for updates (Ctrl+C to stop)...")

        try:
            async for update in bot.poll_updates(timeout=30):
                msg = update.get("message")
                if not msg:
                    continue
                text = msg.get("text")
                if not text:
                    continue
                chat_id = msg.get("chat", {}).get("id")
                if chat_id is None:
                    continue
                try:
                    await bot.send_message(chat_id=chat_id, text=f"echo: {text}")
                except (VibeBotAPIError, ConnectionError) as e:
                    print(f"[echo_bot] sendMessage error: {e}")
        except KeyboardInterrupt:
            print("\n[echo_bot] stopped by user")
        except (VibeBotAPIError, ConnectionError) as e:
            print(f"[echo_bot] polling error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
