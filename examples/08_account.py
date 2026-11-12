# ============================================
#  examples/08_account.py - account info, profile, sessions
#  All code and comments are English. No emojis.
# ============================================
# این مثال اطلاعات حساب، دستگاه های لاگین شده و تنظیمات را نشان می دهد.
# به صورت پیش فرض هیچ تغییری در حساب ایجاد نمی کند (فقط خواندن).

import asyncio
from userapi import VibeClient


async def main():
    c = VibeClient()
    try:
        await c.connect()
        print("[+] متصل شد\n")

        # 1) اطلاعات حساب
        me = await c.get_me()
        print(f"[+] نام: {me.first_name} {getattr(me, 'last_name', '')}")
        print(f"    یوزرنیم: @{getattr(me, 'username', '-')}")
        print(f"    شناسه: {me.id}")
        print(f"    شماره: {getattr(me, 'phone', '-')}")
        print(f"    پرمیوم: {getattr(me, 'premium', False)}")

        # 2) لیست دستگاه های لاگین شده
        print("\n[+] دستگاه های لاگین شده:")
        auths = await c.get_authorizations()
        for auth in auths.authorizations:
            device = getattr(auth, "device_model", "ناشناس")
            platform = getattr(auth, "platform", "ناشناس")
            ip = getattr(auth, "ip", "-")
            country = getattr(auth, "country", "-")
            current = " (این دستگاه)" if getattr(auth, "current", False) else ""
            print(f"    - {device} ({platform}) | IP: {ip} {country}{current}")
            print(f"      هش: {auth.hash}")

        # 3) تنظیمات حریم خصوصی پیام ها
        print("\n[+] حریم خصوصی (آخرین بازدید):")
        try:
            from telethon.tl.types import InputPrivacyKeyStatusTimestamp
            privacy = await c.get_privacy(key=InputPrivacyKeyStatusTimestamp())
            print(f"    {privacy}")
        except Exception as e:
            print(f"    [i] خطا در خواندن: {e}")

        # 4) تغییر موقت اسم (بدون تغییر دائمی)
        print("\n[i] تست تغییر نام (اختیاری)")
        # برای اینکه اسم را تغییر دهید، خطوط زیر را از کامنت خارج کنید
        # current_first = me.first_name
        # await c.update_profile(first_name="تست pyvibe")
        # print("    نام تغییر کرد. برگرداندن...")
        # await c.update_profile(first_name=current_first)
        # print("    نام برگشت")

    finally:
        await c.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
