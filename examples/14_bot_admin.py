# ============================================
#  examples/14_bot_admin.py - Admin Group Bot
#  All code and comments are English. No emojis.
# ============================================
# این مثال نشان می‌دهد چطور یک ربات ادمین بسازید که با دستورات فارسی
# کاربران را سکوت، اخراج یا ادمین کند.

import asyncio
from botapi import VibeBot
from telethon import events

BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"

async def main():
    bot = VibeBot(token=BOT_TOKEN)
    
    async with bot:
        print("[+] ربات مدیریت گروه روشن شد.")
        
        @bot.raw.on(events.NewMessage(incoming=True))
        async def handler(event):
            if not event.is_group: return
            text = event.raw_text.strip()

            # بررسی اینکه آیا فرستنده ادمین است یا نه
            perms = await bot.get_permissions(event.chat_id, event.sender_id)
            if not perms.is_admin and not perms.is_creator:
                return

            if text == "سکوت" and event.is_reply:
                user = await (await event.get_reply_message()).get_sender()
                await bot.edit_permissions(event.chat_id, user, send_messages=False)
                await event.reply(f"کاربر {user.first_name} سکوت شد.")
                
            elif text == "اخراج" and event.is_reply:
                user = await (await event.get_reply_message()).get_sender()
                await bot.kick_participant(event.chat_id, user)
                await event.reply(f"کاربر {user.first_name} اخراج شد.")
                
            elif text == "ادمین" and event.is_reply:
                user = await (await event.get_reply_message()).get_sender()
                await bot.edit_admin(event.chat_id, user, is_admin=True)
                await event.reply(f"کاربر {user.first_name} ادمین شد.")

        await bot.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
