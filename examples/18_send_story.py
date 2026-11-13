# ============================================
#  examples/18_send_story.py - Send Story
#  All code and comments are English. No emojis.
# ============================================
# این مثال نشان می‌دهد چطور یک استوری (عکس) با دسترسی محدود ارسال کنید.

import asyncio
from pathlib import Path
from userapi import VibeClient
from telethon.tl.types import InputMediaUploadedPhoto, InputPrivacyValueAllowCloseFriends

async def main():
    async with VibeClient() as client:
        # ساخت یک عکس تستی (در دنیای واقعی از فایل خودتان استفاده کنید)
        img_path = Path("story_test.png")
        img_path.write_bytes(bytes.fromhex("89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c4890000000d49444154789c63600000000005000156a6b4b70000000049454e44ae426082"))
        
        print("[i] آپلود عکس...")
        uploaded = await client.upload_file(str(img_path))
        
        print("[i] ارسال استوری...")
        await client.send_story(
            peer="me",
            media=InputMediaUploadedPhoto(file=uploaded),
            privacy_rules=[InputPrivacyValueAllowCloseFriends()], # فقط دوستان نزدیک
            period=86400 # ۲۴ ساعت
        )
        print("[+] استوری با موفقیت ارسال شد.")
        
        img_path.unlink()

if __name__ == "__main__":
    asyncio.run(main())
