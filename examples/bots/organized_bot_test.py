# ============================================
#  examples/bots/organized_bot_test.py
#  All code and comments are English. No emojis.
# ============================================
import asyncio
from botapi import VibeBot

BOT_TOKEN = "1780243525:rfPx6zSuVGUoCfoISwunFTyLLIYQ94I_YxP"

async def main():
    bot = VibeBot(token=BOT_TOKEN)
    
    async with bot:
        me = await bot.get_me()
        print(f"[+] Organized Bot @{me.username} is running!")
        
        # Test 1: Set Commands Menu
        await bot.set_commands([
            ("start", "Start the bot"),
            ("help", "Get help")
        ])
        print("[OK] Command menu set.")

        # Test 2: Set Bot Description
        try:
            await bot.set_bot_description("This is an organized test bot for vibegram.")
            print("[OK] Bot description set.")
        except Exception as e:
            print(f"[FAIL] Description: {e}")

        # Test 3: Send typing status (simulated in console)
        # (Requires a chat ID to send to, we'll skip this in the script to avoid spamming)

        print("[i] All bot method tests completed. You can check the app for the new menu.")
        await asyncio.sleep(3)

if __name__ == "__main__":
    asyncio.run(main())
