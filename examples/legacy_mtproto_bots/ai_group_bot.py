# ============================================
#  examples/bots/ai_group_bot.py - AI Group Assistant Bot
#  All code and comments are English. No emojis.
# ============================================
import asyncio
import httpx
from botapi import VibeBot
from telethon import events

BOT_TOKEN = "1780243525:Gej5Nez33l5iLXwY81kuEUTF79_fSgsJa53"

# Address of your FastAPI server. 
# Note: If running on Termux, use 127.0.0.1. If on a remote server, use its IP.
API_URL = "http://127.0.0.1:8000/api/chat"

async def main():
    bot = VibeBot(token=BOT_TOKEN)

    async with bot:
        me = await bot.get_me()
        print(f"[+] AI Group Bot @{me.username} is running...")
        print(f"[+] Connected to AI Server at {API_URL}")
        print("[i] Add the bot to a group and send a message to test. Ctrl+C to stop.")

        @bot.raw.on(events.NewMessage(incoming=True))
        async def handler(event):
            # 1. Only respond in groups (not private messages)
            if not event.is_group:
                return
            
            # 2. Ignore commands and empty messages
            text = event.raw_text.strip()
            if not text or text.startswith("/"):
                return

            # 3. Show "typing..." status
            try:
                await bot.send_typing(event.chat_id)
            except Exception:
                pass

            # 4. Send request to FastAPI
            try:
                async with httpx.AsyncClient() as client:
                    payload = {
                        "user_id": event.sender_id,
                        "text": text
                    }
                    
                    # 30 seconds timeout for AI processing
                    response = await client.post(API_URL, json=payload, timeout=30)
                    response.raise_for_status()
                    data = response.json()
                    
                    ai_response = data.get("response", "خطا در دریافت پاسخ از سرور.")
                    
                    # 5. Reply to the message in the group
                    await event.reply(ai_response)
                    print(f"[>] Replied in group {event.chat_id}")

            except httpx.ConnectError:
                await event.reply("ارتباط با سرور هوش مصنوعی برقرار نشد. لطفا بعدا تلاش کنید.")
                print("[!] Failed to connect to FastAPI. Is it running?")
            except httpx.TimeoutException:
                await event.reply("پردازش پیام بیش از حد طول کشید.")
                print("[!] Timeout connecting to FastAPI.")
            except Exception as e:
                print(f"[!] Error: {type(e).__name__}: {e}")

        await bot.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
