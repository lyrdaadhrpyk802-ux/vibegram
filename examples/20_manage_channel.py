# ============================================
#  examples/20_manage_channel.py - Channel Management
#  All code and comments are English. No emojis.
# ============================================
# این مثال نشان می‌دهد چطور یک کانال بسازید، عنوان آن را تغییر دهید و لینک دعوت بگیرید.

import asyncio
from userapi import VibeClient

async def main():
    async with VibeClient() as client:
        print("[+] متصل شد.")
        
        # ۱. ساخت یک کانال جدید
        print("[i] در حال ساخت کانال...")
        result = await client.create_channel("کانال تست پایتون", about="توضیحات تستی")
        print("[+] کانال ساخته شد.")
        
        # ۲. تغییر عنوان کانال
        # نکته: به جای آیدی عددی، می‌توانید از یوزرنیم یا اسم استفاده کنید
        # await client.edit_channel_title("@my_channel", "عنوان جدید")
        
        # ۳. گرفتن لینک دعوت
        # link = await client.get_chat_invite_link("@my_channel")
        # print(f"[+] لینک دعوت: {link.link}")

if __name__ == "__main__":
    asyncio.run(main())
