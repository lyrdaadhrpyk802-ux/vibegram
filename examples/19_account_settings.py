# ============================================
#  examples/19_account_settings.py - Profile Settings
#  All code and comments are English. No emojis.
# ============================================
# این مثال نشان می‌دهد چطور بیوگرافی، یوزرنیم و عکس پروفایل خود را تغییر دهید.

import asyncio
from userapi import VibeClient

async def main():
    async with VibeClient() as client:
        print("[+] متصل شد.")
        
        # ۱. تغییر بیوگرافی (Bio)
        print("[i] در حال تغییر بیوگرافی...")
        await client.set_bio("من یک برنامه‌نویس پایتون هستم.")
        print("[+] بیوگرافی تغییر کرد.")
        
        # ۲. تغییر وضعیت آنلاین/آفلاین
        print("[i] تنظیم وضعیت به آفلاین...")
        await client.set_offline()
        print("[+] وضعیت آفلاین شد.")
        
        # ۳. گرفتن اطلاعات کامل حساب
        me = await client.get_me()
        full = await client.get_full_user(me)
        print(f"[+] بیوگرافی فعلی: {full.full_user.about}")

if __name__ == "__main__":
    asyncio.run(main())
