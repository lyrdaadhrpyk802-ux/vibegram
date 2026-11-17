# ============================================
#  examples/21_search_filters.py - Advanced Search
#  All code and comments are English. No emojis.
# ============================================
# این مثال نشان می‌دهد چطور در یک چت، فقط عکس‌ها یا فایل‌ها را جستجو کنید.

import asyncio
from userapi import VibeClient
from telethon.tl.types import InputMessagesFilterPhotos, InputMessagesFilterDocument

async def main():
    async with VibeClient() as client:
        print("[+] متصل شد.")
        
        chat = "me" # یا "@channel"
        
        # ۱. جستجوی فقط عکس‌ها
        print("[i] در حال جستجوی عکس‌ها...")
        photos = await client.search_messages(chat, "", limit=5, message_filter=InputMessagesFilterPhotos())
        print(f"[+] تعداد عکس‌های پیدا شده: {len(photos)}")
        
        # ۲. جستجوی فقط فایل‌های سند (Document)
        print("[i] در حال جستجوی فایل‌ها...")
        docs = await client.search_messages(chat, "", limit=5, message_filter=InputMessagesFilterDocument())
        print(f"[+] تعداد فایل‌های پیدا شده: {len(docs)}")

if __name__ == "__main__":
    asyncio.run(main())
