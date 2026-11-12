# ============================================
#  examples/09_contacts.py - list, block, unblock
#  All code and comments are English. No emojis.
# ============================================
# این مثال لیست مخاطبین و بلاک شده ها را نشان می دهد.

import asyncio
from userapi import VibeClient


async def main():
    c = VibeClient()
    try:
        await c.connect()
        print("[+] متصل شد\n")

        # 1) لیست مخاطبین
        print("[+] لیست مخاطبین:")
        contacts = await c.get_contacts()
        if not contacts:
            print("    (لیست مخاطبین خالی است)")
        else:
            for u in contacts[:10]:
                name = f"{getattr(u, 'first_name', '')} {getattr(u, 'last_name', '')}".strip()
                username = f" (@{u.username})" if getattr(u, "username", None) else ""
                print(f"    id={u.id} {name}{username}")
            if len(contacts) > 10:
                print(f"    ... و {len(contacts) - 10} مخاطب دیگر")

        # 2) لیست بلاک شده ها
        print("\n[+] کاربران بلاک شده:")
        blocked = await c.get_blocked()
        if not blocked:
            print("    (کسی را بلاک نکرده اید)")
        else:
            for b in blocked:
                print(f"    {b}")

        # 3) نمونه کد بلاک کردن یک ربات (از کامنت خارج نکنید مگر بخواهید)
        # print("\n[i] تست بلاک کردن یک ربات (Vibe)")
        # try:
        #     await c.block_user(777000) # 777000 معمولا آیدی رسمی تلگرام/وایب است
        #     print("    بلاک شد")
        #     await c.unblock_user(777000)
        #     print("    آنبلاک شد")
        # except Exception as e:
        #     print(f"    خطا: {e}")

    finally:
        await c.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
