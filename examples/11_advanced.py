# ============================================
#  examples/11_advanced.py - raw TL calls
#  All code and comments are English. No emojis.
# ============================================
# این مثال نشان می دهد چطور از دستورات خام (Raw TL) استفاده کنید.
# اگر متدی مستقیما در VibeClient نبود، می توانید از raw استفاده کنید.

import asyncio
from telethon.tl.functions.help import GetConfigRequest
from telethon.tl.functions.users import GetFullUserRequest
from userapi import VibeClient


async def main():
    c = VibeClient()
    try:
        await c.connect()
        print("[+] متصل شد\n")

        # 1) دریافت تنظیمات سرور (Raw)
        print("[+] تنظیمات سرور Vibe:")
        config = await c.raw(GetConfigRequest())
        print(f"    دیتاسنتر: {config.this_dc}")
        print(f"    تاریخ: {config.date}")
        print(f"    حداکثر حجم فایل: {getattr(config, 'file_size_max', '?')}")

        # 2) دریافت اطلاعات کامل کاربر (Raw)
        print("\n[+] اطلاعات کامل حساب شما:")
        me = await c.get_me()
        input_me = await c.get_input_entity(me)
        full_user = await c.raw(GetFullUserRequest(id=input_me))
        
        about = getattr(full_user.full_user, 'about', '')
        print(f"    بیوگرافی: {about or '(خالی)'}")
        print(f"    تعداد چت مشترک: {getattr(full_user.full_user, 'common_chats_count', 0)}")

        # 3) لیست تم ها (Raw)
        print("\n[+] تم های موجود:")
        from telethon.tl.functions.account import GetThemesRequest
        themes = await c.raw(GetThemesRequest(format="", hash=0))
        for t in themes.themes[:3]:
            print(f"    - {t.title} (slug: {t.slug})")

        # 4) متد های عمومی در VibeClient
        print("\n[i] اکثر متدها مستقیما در VibeClient هستند (مثلا c.get_me()).")
        print("[i] اگر متدی نبود، با c.raw(Request(...)) قابل دسترسی است.")

    finally:
        await c.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
