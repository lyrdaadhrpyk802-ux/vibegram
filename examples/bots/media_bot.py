# ============================================
#  examples/bots/media_bot.py - Bot to test media sending
#  All code and comments are English. No emojis.
# ============================================
import asyncio
import sys
from pathlib import Path
from botapi import VibeBot
from botapi.keyboards import ReplyKeyboard
from telethon import events
from telethon.tl.types import InputMediaGeoPoint, InputGeoPoint
from telethon.errors import ChatSendVoicesForbiddenError

BOT_TOKEN = "1780243525:rfPx6zSuVGUoCfoISwunFTyLLIYQ94I_YxP"

async def main():
    bot = VibeBot(token=BOT_TOKEN)
    
    temp_dir = Path.home() / "pyvibe_bot_temp"
    temp_dir.mkdir(exist_ok=True)
    
    png_path = temp_dir / "test.png"
    png_path.write_bytes(bytes.fromhex("89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c4890000000d49444154789c63600000000005000156a6b4b70000000049454e44ae426082"))
    
    txt_path = temp_dir / "test.txt"
    txt_path.write_text("This is a test file from the bot.")

    ogg_path = temp_dir / "test.ogg"
    ogg_path.write_bytes(b"OggS\x00\x02" + b"\x00" * 60)

    try:
        async with bot:
            me = await bot.get_me()
            print(f"[+] Media Bot @{me.username} is running!")
            print("[i] Send 'photo', 'file', 'voice', or 'location' to test.\n")

            @bot.raw.on(events.NewMessage(incoming=True))
            async def message_handler(event):
                text = event.raw_text.strip().lower()
                
                if text == "photo":
                    await event.reply("Sending photo...")
                    await bot.send_photo(event.chat_id, str(png_path), caption="This is a test photo.")
                    print("[OK] Photo sent!")
                    
                elif text == "file":
                    await event.reply("Sending document...")
                    await bot.send_document(event.chat_id, str(txt_path), caption="This is a test document.")
                    print("[OK] Document sent!")
                    
                elif text == "voice":
                    await event.reply("Sending voice...")
                    try:
                        await bot.send_voice(event.chat_id, str(ogg_path))
                        print("[OK] Voice sent!")
                    except ChatSendVoicesForbiddenError:
                        await event.reply("Vibe server does not allow bots to send voice notes.")
                        print("[FAIL] Voice rejected by server.")
                    except Exception as e:
                        print(f"[FAIL] Voice error: {e}")
                    
                elif text == "location":
                    await event.reply("Sending location...")
                    geo = InputMediaGeoPoint(geo_point=InputGeoPoint(lat=35.6892, long=51.3890))
                    await bot.send_media(event.chat_id, geo)
                    print("[OK] Location sent!")
                    
                else:
                    rkb = ReplyKeyboard(resize=True)
                    rkb.add("Photo").add("File").row()
                    rkb.add("Voice").add("Location").row()
                    await event.reply("Please choose an option:", buttons=rkb.build())

            try:
                await bot.run_until_disconnected()
            except asyncio.CancelledError:
                print("\n[i] Bot disconnected cleanly.")

    except KeyboardInterrupt:
        pass
    finally:
        for f in temp_dir.glob("*"):
            try: f.unlink()
            except: pass
        try: temp_dir.rmdir()
        except: pass

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(0)
