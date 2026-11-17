# ============================================
#  examples/13_bot_fsm.py - State Machine Bot
#  All code and comments are English. No emojis.
# ============================================
# این مثال یک ربات ثبت‌نام مرحله‌به‌مرحله (ماشین حالت) می‌سازد.
# کاربر دستور 'ثبت نام' را می‌فرستد، ربات نام و سن او را می‌پرسد.

import asyncio
from botapi import VibeBot
from botapi.fsm import State, StatesGroup
from telethon import events

BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"

class Form(StatesGroup):
    name = State("WaitingForName")
    age = State("WaitingForAge")

async def main():
    bot = VibeBot(token=BOT_TOKEN)
    
    async with bot:
        print("[+] ربات ثبت‌نام روشن شد.")
        print("[i] به ربات پیام 'ثبت نام' بدهید.")
        
        @bot.raw.on(events.NewMessage(incoming=True))
        async def handler(event):
            uid = event.sender_id
            text = event.raw_text.strip()
            state = bot.fsm.get_state(uid)

            if text == "ثبت نام":
                bot.fsm.set_state(uid, Form.name)
                await event.respond("سلام! لطفاً نام خود را وارد کنید:")
                return
                
            if text == "لغو":
                bot.fsm.clear_state(uid)
                await event.respond("ثبت‌نام لغو شد.")
                return

            if state == Form.name:
                bot.fsm.set_state(uid, Form.age)
                await event.respond(f"ممنون {text} عزیز. حالا سن خود را وارد کنید:")
            elif state == Form.age:
                if not text.isdigit():
                    await event.respond("لطفاً فقط عدد وارد کنید:")
                    return
                bot.fsm.clear_state(uid)
                await event.respond("ثبت‌نام شما با موفقیت انجام شد!")
            else:
                await event.respond("برای شروع، پیام 'ثبت نام' را بفرستید.")

        await bot.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
