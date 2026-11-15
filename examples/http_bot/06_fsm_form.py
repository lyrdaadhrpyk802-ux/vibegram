# ============================================
#  examples/http_bot/06_fsm_form.py - Simple FSM (state machine) form
#  All code and comments are English. No emojis.
# ============================================
import asyncio
import os
import sys

from botapi import VibeBotHTTP

user_states = {}

async def main():
    token = os.getenv("VIBE_BOT_TOKEN", "").strip()
    if not token:
        print("[fsm_form] error: set VIBE_BOT_TOKEN environment variable")
        sys.exit(1)

    async with VibeBotHTTP(token) as bot:
        print("[fsm_form] polling updates...")
        async for update in bot.poll_updates(timeout=30):
            msg = update.get("message")
            if not msg or not msg.get("text"):
                continue

            text = msg["text"].strip()
            chat_id = msg["chat"]["id"]

            if text == "/start":
                user_states[chat_id] = {"step": "name"}
                await bot.send_message(chat_id=chat_id, text="What is your name?")
                continue

            if text == "/cancel":
                user_states.pop(chat_id, None)
                await bot.send_message(chat_id=chat_id, text="Cancelled.")
                continue

            state = user_states.get(chat_id)
            if not state:
                await bot.send_message(chat_id=chat_id, text="Send /start to begin.")
                continue

            if state["step"] == "name":
                state["name"] = text
                state["step"] = "age"
                await bot.send_message(chat_id=chat_id, text=f"Nice to meet you, {text}. How old are you?")

            elif state["step"] == "age":
                if not text.isdigit():
                    await bot.send_message(chat_id=chat_id, text="Please send a valid number.")
                    continue
                state["age"] = int(text)
                state["step"] = "done"
                await bot.send_message(
                    chat_id=chat_id,
                    text=f"Form complete! Name: {state['name']}, Age: {state['age']}"
                )
                user_states.pop(chat_id, None)

if __name__ == "__main__":
    asyncio.run(main())
