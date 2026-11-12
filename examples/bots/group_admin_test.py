# ============================================
#  examples/bots/group_admin_test.py - Test admin capabilities
#  All code and comments are English. No emojis.
# ============================================
import asyncio
import sys
from botapi import VibeBot
from telethon import events
from telethon.tl.functions.channels import EditTitleRequest
from telethon.tl.types import InputChannel, InputPeerChannel

BOT_TOKEN = "1780243525:rfPx6zSuVGUoCfoISwunFTyLLIYQ94I_YxP"

async def main():
    bot = VibeBot(token=BOT_TOKEN)
    
    async with bot:
        me = await bot.get_me()
        print(f"[+] Admin Test Bot @{me.username} is running!")
        print("[i] Add this bot to a group as an Admin, then type /admin_test in the group.\n")

        @bot.command("admin_test")
        async def admin_test_handler(event):
            chat = await event.get_chat()
            print(f"\n--- Starting Admin Test in {chat.title} ---")
            
            # 1. Test: Get Participants
            try:
                participants = await bot.get_participants(chat.id, limit=5)
                print(f"[OK] Get Participants: Found {len(participants)} members.")
                await event.reply(f"دریافت لیست اعضا: موفق ({len(participants)} عضو)")
            except Exception as e:
                print(f"[FAIL] Get Participants: {e}")
                await event.reply(f"دریافت لیست اعضا: ناموفق ({type(e).__name__})")

            # 2. Test: Pin a message
            try:
                test_msg = await bot.send_message(chat.id, "This message will be pinned.")
                await bot.pin_message(chat.id, test_msg.id, notify=False)
                print("[OK] Pin Message: Success.")
                await event.reply("پین کردن پیام: موفق")
                # Unpin immediately to clean up
                await bot.unpin_message(chat.id, test_msg.id)
            except Exception as e:
                print(f"[FAIL] Pin Message: {e}")
                await event.reply(f"پین کردن پیام: ناموفق ({type(e).__name__})")

            # 3. Test: Get Invite Link
            try:
                link = await bot.get_chat_invite_link(chat.id)
                invite_link = getattr(link, 'link', 'Unknown')
                print(f"[OK] Get Invite Link: {invite_link}")
                await event.reply(f"ساخت لینک دعوت: موفق\n{invite_link}")
            except Exception as e:
                print(f"[FAIL] Get Invite Link: {e}")
                await event.reply(f"ساخت لینک دعوت: ناموفق ({type(e).__name__})")

            # 4. Test: Edit Group Title (Safe, changes and reverts)
            original_title = chat.title
            try:
                inp = await bot.get_input_entity(chat.id)
                if isinstance(inp, InputPeerChannel):
                    ch = InputChannel(channel_id=inp.channel_id, access_hash=inp.access_hash)
                else:
                    ch = inp
                await bot.raw(EditTitleRequest(channel=ch, title=original_title + " [Test]"))
                await asyncio.sleep(1)
                await bot.raw(EditTitleRequest(channel=ch, title=original_title))
                print("[OK] Edit Title: Success.")
                await event.reply("تغییر نام گروه: موفق")
            except Exception as e:
                print(f"[FAIL] Edit Title: {e}")
                await event.reply(f"تغییر نام گروه: ناموفق ({type(e).__name__})")

            await event.reply("تست مدیریت گروه به پایان رسید. لاگ‌ها را در ترمینال ببینید.")
            print("--- Admin Test Finished ---\n")

        try:
            await bot.run_until_disconnected()
        except asyncio.CancelledError:
            print("\n[i] Bot disconnected cleanly.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(0)
