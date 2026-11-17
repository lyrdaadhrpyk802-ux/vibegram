# ============================================
#  examples/03_read_messages.py - read chats, messages, search
#  All code and comments are English. No emojis.
# ============================================
# این مثال نشان می‌دهد چطور دیالوگ ها و پیام ها را بخوانید و جستجو کنید.

import asyncio
from userapi import VibeClient


async def main():
    c = VibeClient()
    try:
        await c.connect()
        print("[+] متصل شد\n")

        # 1) لیست دیالوگ ها
        print("[+] 5 چت آخر:")
        dialogs = await c.get_dialogs(limit=5)
        for d in dialogs:
            kind = "کاربر" if getattr(d.entity, "first_name", None) else "گروه/کانال"
            print(f"    {kind:12s}  id={d.id:<15}  {d.name}")

        # 2) خواندن پیام های Saved Messages
        print("\n[+] 5 پیام آخر در Saved Messages:")
        msgs = await c.get_messages("me", limit=5)
        for m in msgs:
            text = (m.text or "<بدون متن>")[:60].replace("\n", " ")
            print(f"    [{m.id}] {text}")

        # 3) جستجوی متن در یک چت
        query = "pyvibe"
        print(f"\n[+] جستجوی {query} در Saved Messages:")
        hits = await c.search_messages("me", query, limit=5)
        if not hits:
            print("    (چیزی پیدا نشد)")
        else:
            for m in hits:
                text = (m.text or "<بدون متن>")[:60].replace("\n", " ")
                print(f"    [{m.id}] {text}")

        # 4) جستجوی کاربر/کانال
        print("\n[+] جستجوی کاربر Ali:")
        found = await c.search_peers("Ali", limit=5)
        for u in found.users[:5]:
            name = getattr(u, "first_name", "?")
            username = getattr(u, "username", "-")
            print(f"    id={u.id} {name} (@{username})")

        # 5) اطلاعات کامل یک چت
        print("\n[+] اطلاعات کامل Saved Messages:")
        ent = await c.get_entity("me")
        print(f"    نوع: {type(ent).__name__}")
        print(f"    id: {ent.id}")
        print(f"    نام: {getattr(ent, 'first_name', '-')}")

    finally:
        await c.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
