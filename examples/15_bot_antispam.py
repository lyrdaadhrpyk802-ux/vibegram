# ============================================
#  examples/15_bot_antispam.py - Anti-Spam Bot
#  All code and comments are English. No emojis.
# ============================================
# این مثال یک سیستم ضد لینک و اسپم ساده را برای گروه پیاده‌سازی می‌کند.

import asyncio
import re
from botapi import VibeBot
from telethon import events

BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
LINK_PATTERN = re.compile(r'(https?://\S+|t\.me/\S+|@\w+)', re.IGNORECASE)

async def main():
    bot = VibeBot(token=BOT_TOKEN)
    warnings = {}

    async with bot:
        print("[+] ربات ضد اسپم روشن شد.")
        
        @bot.raw.on(events.NewMessage(incoming=True))
        async def handler(event):
            if not event.is_group: return
            
            perms = await bot.get_permissions(event.chat_id, event.sender_id)
            if perms.is_admin or perms.is_creator: return # ادمین‌ها مصون هستند

            if LINK_PATTERN.search(event.raw_text):
                await event.delete()
                uid = event.sender_id
                warnings[uid] = warnings.get(uid, 0) + 1
                
                if warnings[uid] >= 3:
                    await bot.edit_permissions(event.chat_id, uid, send_messages=False)
                    await event.respond("به دلیل ارسال لینک مکرر، سکوت شدید.")
                    warnings[uid] = 0
                else:
                    await event.respond(f"ارسال لینک مجاز نیست. (اخطار {warnings[uid]} از 3)")

        await bot.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
