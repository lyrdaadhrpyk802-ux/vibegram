# ============================================
#  examples/02_send_message.py - send, edit, delete
#  All code and comments are English. No emojis.
# ============================================
# این مثال نشان می‌دهد چطور پیام بفرستید، ویرایش کنید، پاسخ دهید،
# پین کنید، حذف کنید. همه به Saved Messages.

import asyncio
from userapi import VibeClient


async def main():
    c = VibeClient()
    sent_ids = []
    try:
        await c.connect()
        me = await c.get_me()
        print(f"[+] وارد شده به عنوان {me.first_name}\n")

        # 1) ارسال پیام ساده
        msg = await c.send_message("me", "سلام از pyvibe")
        sent_ids.append(msg.id)
        print(f"[+] پیام فرستاده شد (id={msg.id})")

        # 2) ارسال پیام سایلنت
        msg2 = await c.send_message("me", "پیام بی صدا", silent=True)
        sent_ids.append(msg2.id)
        print(f"[+] پیام سایلنت فرستاده شد (id={msg2.id})")

        # 3) ویرایش پیام
        await c.edit_message("me", msg.id, "متن ویرایش شد")
        print(f"[+] پیام {msg.id} ویرایش شد")

        # 4) پاسخ به پیام
        reply = await c.send_message("me", "این یک پاسخ است", reply_to=msg.id)
        sent_ids.append(reply.id)
        print(f"[+] پاسخ فرستاده شد (id={reply.id})")

        # 5) پین کردن
        try:
            await c.pin_message("me", msg.id, notify=False)
            print(f"[+] پیام {msg.id} پین شد")
        except Exception as e:
            print(f"[i] پین نشد: {type(e).__name__}")

        # 6) خواندن پیام های اخیر
        recent = await c.get_messages("me", limit=3)
        print("\n[+] 3 پیام آخر:")
        for m in recent:
            text = m.text or "<بدون متن>"
            print(f"    [{m.id}] {text[:50]}")

        # 7) پاک کردن پیام های تست
        print(f"\n[i] پاک کردن {len(sent_ids)} پیام تست...")
        await c.delete_messages("me", sent_ids, revoke=True)
        print("[+] پاک شدند")

    finally:
        await c.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
