# ============================================
#  examples/01_login.py - login with phone + OTP
#  All code and comments are English. No emojis.
# ============================================
# این مثال نشان می‌دهد چطور با شماره تلفن وارد Vibe شوید.
# اگر قبلاً لاگین کرده‌اید، فقط اطلاعات حساب را نشان می‌دهد.

import asyncio
from userapi import VibeClient


async def main():
    c = VibeClient()
    try:
        await c.connect()
        print("[+] اتصال به Vibe برقرار شد")

        if await c.is_authorized():
            me = await c.get_me()
            print(f"[+] قبلاً لاگین هستید: {me.first_name} (@{getattr(me, 'username', '-')})")
            return

        phone = input("شماره تلفن (با کد کشور، مثال: +98912...): ").strip()
        phone = phone.replace(" ", "").replace("-", "")
        if not phone.startswith("+"):
            phone = "+" + phone.lstrip("0")

        await c.request_code(phone)
        print("[+] کد تأیید ارسال شد")

        code = input("کد تأیید: ").strip()
        try:
            await c.sign_in(phone, code)
        except Exception as e:
            if "password" in str(e).lower():
                pw = input("رمز دو مرحله‌ای (2FA): ").strip()
                await c.sign_in(phone, code, password=pw)
            else:
                raise

        me = await c.get_me()
        print(f"[+] خوش آمدید: {me.first_name} (@{getattr(me, 'username', '-')})")
    finally:
        await c.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
