# ============================================
#  examples/17_backup_chat.py - Chat Backup
#  All code and comments are English. No emojis.
# ============================================
# این مثال نشان می‌دهد چطور از پیام‌های یک گروه یا کانال بکاپ JSON بگیرید.

import asyncio
from userapi import VibeClient
from userapi.backup import backup_chat

async def main():
    async with VibeClient() as client:
        target = "@Linkdooni"  # یوزرنیم یا آیدی کانال/گروه
        print(f"[i] در حال دریافت بکاپ از {target}...")
        
        # پارامتر limit را برای محدود کردن تعداد پیام تنظیم می‌کند
        path, info = await backup_chat(client, target, limit=50, download_media=False)
        
        print(f"[+] بکاپ در این مسیر ذخیره شد: {path}")
        print(f"[+] تعداد پیام‌های ذخیره شده: {info['message_count']}")

if __name__ == "__main__":
    asyncio.run(main())
