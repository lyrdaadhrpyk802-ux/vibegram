# ============================================
#  examples/16_send_album.py - Media & Album
#  All code and comments are English. No emojis.
# ============================================
# این مثال نشان می‌دهد چطور چند فایل را با هم (آلبوم) یا با نوار پیشرفت ارسال کنید.

import asyncio
from pathlib import Path
from userapi import VibeClient, make_progress_bar

async def main():
    async with VibeClient() as client:
        print("[+] متصل شد.")
        
        # ارسال آلبوم (فرض بر وجود دو عکس در پوشه)
        # اگر عکس ندارید، این بخش را کامنت کنید
        # photos = ["photo1.jpg", "photo2.jpg"]
        # await client.send_file("me", photos, caption="این یک آلبوم است")
        
        # ارسال فایل با نوار پیشرفت
        test_file = Path("test_file.txt")
        test_file.write_text("این یک فایل تستی است." * 1000)
        
        print("[i] در حال ارسال فایل با نمایش درصد...")
        bar = make_progress_bar("Upload")
        await client.send_file("me", str(test_file), progress_callback=bar)
        
        test_file.unlink() # پاک کردن فایل تستی
        print("[+] ارسال تمام شد.")

if __name__ == "__main__":
    asyncio.run(main())
