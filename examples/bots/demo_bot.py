# ============================================
#  examples/bots/demo_bot.py - Echo Bot (No /start needed)
#  All code and comments are English. No emojis.
# ============================================
import asyncio
from botapi import VibeBot
from telethon import events

# Replace with your token
BOT_TOKEN = "1780243525:rfPx6zSuVGUoCfoISwunFTyLLIYQ94I_YxP"

async def main():
    bot = VibeBot(token=BOT_TOKEN)
    
    try:
        print("[i] Connecting (timeout=60s)...")
        # Increase connection timeout because of weak internet
        await bot.connect(timeout=60)
        
        me = await bot.get_me()
        print(f"[+] Bot @{me.username} is now running!")
        print("[i] Send ANY message to the bot in the app. It will reply.\n")

        # Listen to ANY incoming message
        @bot.raw.on(events.NewMessage(incoming=True))
        async def echo_handler(event):
            print(f"[>] Received: {event.raw_text}")
            
            # Reply with the same text
            await event.reply(f"پاسخ ربات: {event.raw_text}")
            print("[<] Replied!")

        await bot.run_until_disconnected()

    except asyncio.TimeoutError:
        print("\n[!] Connection timed out. Your internet is too weak right now.")
        print("[i] Please check your connection and try again.")
    except KeyboardInterrupt:
        print("\n[i] Bot stopped.")
    except Exception as e:
        print(f"\n[!] Error: {type(e).__name__}: {e}")
    finally:
        await bot.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
