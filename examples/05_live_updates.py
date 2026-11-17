# ============================================
#  examples/05_live_updates.py - listen for live messages
#  All code and comments are English. No emojis.
# ============================================
# این مثال نشان می‌دهد چطور به پیام های زنده گوش دهید.
# برای خروج Ctrl+C بزنید.
# در حین اجرا، از یک دستگاه دیگر به خودتان پیام بدهید تا ببینید.

import asyncio
from telethon import events
from userapi import VibeClient


async def main():
    c = VibeClient()
    try:
        await c.connect()
        print("[+] متصل شد. در حال گوش دادن به پیام های جدید...")
        print("    (Ctrl+C برای خروج)\n")

        # ثبت شنونده برای همه پیام های جدید
        @c.raw.on(events.NewMessage())
        async def handler(event):
            msg = event.message
            sender = await event.get_sender()
            chat = await event.get_chat()
            
            chat_name = getattr(chat, 'title', getattr(chat, 'first_name', 'ناشناس'))
            sender_name = getattr(sender, 'first_name', 'ناشناس')
            text = msg.text or "<بدون متن/مدیا>"
            
            print(f"[پیام جدید] در {chat_name} از {sender_name}:")
            print(f"  {text[:80]}\n")

        # حلقه بی نهایت تا زمانی که کاربر قطع کند
        await c.raw.run_until_disconnected()

    except KeyboardInterrupt:
        print("\n[i] خارج شد")
    finally:
        await c.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
