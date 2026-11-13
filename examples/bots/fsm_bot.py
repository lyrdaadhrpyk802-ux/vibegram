# ============================================
#  examples/bots/fsm_bot.py - Form Bot using FSM
#  All code and comments are English. No emojis.
# ============================================
import asyncio
from botapi import VibeBot
from botapi.fsm import State, StatesGroup
from telethon import events

BOT_TOKEN = "1780243525:Gej5Nez33l5iLXwY81kuEUTF79_fSgsJa53"

# Define conversation states
class Form(StatesGroup):
    name = State("WaitingForName")
    age = State("WaitingForAge")

async def main():
    bot = VibeBot(token=BOT_TOKEN)

    async with bot:
        print("[+] FSM Bot is running...")
        print("[i] Send 'ثبت نام' to start the registration process.")

        @bot.raw.on(events.NewMessage(incoming=True))
        async def handler(event):
            user_id = event.sender_id
            text = event.raw_text.strip()
            current_state = bot.fsm.get_state(user_id)

            # Start command
            if text == "ثبت نام":
                bot.fsm.set_state(user_id, Form.name)
                await event.respond("سلام! لطفاً نام خود را وارد کنید:")
                return

            # Cancel command
            if text == "لغو":
                bot.fsm.clear_state(user_id)
                await event.respond("عملیات لغو شد.")
                return

            # Handle states
            if current_state == Form.name:
                # Save name (in a real app, save to database)
                bot.fsm.set_state(user_id, Form.age)
                await event.respond(f"خوشحالم {text} عزیز. حالا سن خود را وارد کنید:")
            
            elif current_state == Form.age:
                if not text.isdigit():
                    await event.respond("لطفاً فقط عدد وارد کنید.")
                    return
                
                bot.fsm.clear_state(user_id)
                await event.respond(f"ثبت نام کامل شد! (سن شما {text} سال ثبت شد)")
            
            else:
                # Default fallback
                await event.respond("برای شروع ثبت نام دستور 'ثبت نام' را بفرستید.")

        await bot.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
