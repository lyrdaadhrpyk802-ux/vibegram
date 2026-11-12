# ============================================
#  examples/bots/group_admin_deep_test.py - Deep Admin Test
#  All code and comments are English. No emojis.
# ============================================
import asyncio
import sys
from botapi import VibeBot
from telethon import events

BOT_TOKEN = "1780243525:rfPx6zSuVGUoCfoISwunFTyLLIYQ94I_YxP"

async def main():
    bot = VibeBot(token=BOT_TOKEN)
    
    async with bot:
        me = await bot.get_me()
        print(f"[+] Deep Test Bot @{me.username} is running!")
        print("[i] Send /deep_test in the Test bot group.\n")

        @bot.command("deep_test")
        async def deep_test_handler(event):
            chat_id = event.chat_id
            print(f"\n--- Starting Deep Admin Test ---")
            await event.reply("شروع تست عمیق مدیریت گروه...")

            # 1. Test: Restrict User (Take Access)
            try:
                sender = await event.get_sender()
                # Remove send_messages permission for 5 seconds, then revert
                await bot.edit_permissions(chat_id, sender, send_messages=False)
                print("[OK] Restrict User: Successfully muted the user.")
                await asyncio.sleep(2)
                await bot.edit_permissions(chat_id, sender, send_messages=True)
                print("[OK] Restrict User: Successfully unmuted the user.")
                await event.reply("محدود کردن کاربر: موفق (سکوت و رفع سکوت شد)")
            except Exception as e:
                print(f"[FAIL] Restrict User: {e}")
                await event.reply(f"محدود کردن کاربر: ناموفق ({type(e).__name__})")

            # 2. Test: Slow Mode
            try:
                await bot.toggle_slow_mode(chat_id, seconds=5)
                print("[OK] Slow Mode: Enabled (5s).")
                await asyncio.sleep(1)
                await bot.toggle_slow_mode(chat_id, seconds=0)
                print("[OK] Slow Mode: Disabled.")
                await event.reply("حالت آهسته (Slow Mode): موفق")
            except Exception as e:
                print(f"[FAIL] Slow Mode: {e}")
                await event.reply(f"حالت آهسته: ناموفق ({type(e).__name__})")

            # 3. Test: Anti-Spam
            try:
                await bot.toggle_anti_spam(chat_id, enabled=True)
                print("[OK] Anti-Spam: Enabled.")
                await asyncio.sleep(1)
                await bot.toggle_anti_spam(chat_id, enabled=False)
                print("[OK] Anti-Spam: Disabled.")
                await event.reply("ضد اسپم: موفق")
            except Exception as e:
                print(f"[FAIL] Anti-Spam: {e}")
                await event.reply(f"ضد اسپم: ناموفق ({type(e).__name__})")

            # 4. Test: No Forwards (Protect Content)
            try:
                await bot.toggle_no_forwards(chat_id, enabled=True)
                print("[OK] No Forwards: Enabled.")
                await asyncio.sleep(1)
                await bot.toggle_no_forwards(chat_id, enabled=False)
                print("[OK] No Forwards: Disabled.")
                await event.reply("قفل فوروارد: موفق")
            except Exception as e:
                print(f"[FAIL] No Forwards: {e}")
                await event.reply(f"قفل فوروارد: ناموفق ({type(e).__name__})")

            # 5. Test: Group Call (Creation only)
            try:
                # Just try to create, then discard immediately
                from telethon.tl.functions.phone import CreateGroupCallRequest
                from telethon.tl.types import InputPeerChannel, InputChannel
                
                inp = await bot.get_input_entity(chat_id)
                if isinstance(inp, InputPeerChannel):
                    ch = InputChannel(channel_id=inp.channel_id, access_hash=inp.access_hash)
                else:
                    ch = inp

                await bot.raw(CreateGroupCallRequest(peer=ch, random_id=12345))
                print("[OK] Group Call: Successfully created a group call.")
                await event.reply("ساخت گروه کال (Voice Chat): موفق (کال ساخته شد)")
                # Note: Discarding call requires an inputGroupCall object which we didn't fetch here to keep it simple.
            except Exception as e:
                print(f"[FAIL] Group Call: {e}")
                await event.reply(f"ساخت گروه کال: ناموفق ({type(e).__name__})")

            await event.reply("تست عمیق به پایان رسید. لاگ‌ها را در ترمینال ببینید.")
            print("--- Deep Admin Test Finished ---\n")

        try:
            await bot.run_until_disconnected()
        except asyncio.CancelledError:
            print("\n[i] Bot disconnected cleanly.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(0)
