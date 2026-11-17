# ============================================
#  examples/10_backup.py - backup chat to JSON
#  All code and comments are English. No emojis.
# ============================================
# این مثال نشان می دهد چطور از یک چت بکاپ بگیرید.
# بکاپ در پوشه ~/pyvibe/backups/ ذخیره می شود.

import asyncio
from pathlib import Path
from userapi import VibeClient
from userapi.backup import backup_chat


async def main():
    c = VibeClient()
    try:
        await c.connect()
        print("[+] متصل شد\n")

        target = input("نام چت یا یوزرنیم (مثلا me یا @username): ").strip()
        if not target:
            target = "me"
            
        print(f"[i] در حال بکاپ گرفتن از: {target}")
        print("[i] فقط 20 پیام آخر برای تست دانلود می شود...\n")

        def progress(step, total, msg):
            text = (msg.get('text') or '')[:40].replace('\n', ' ')
            mt = msg.get('media_type') or 'متن'
            print(f"  [{step}/{total}] id={msg['id']} ({mt}) {text}")

        path, doc = await backup_chat(
            c, target,
            limit=20,
            download_media=True,
            progress=progress
        )

        print(f"\n[+] پایان بکاپ!")
        print(f"    تعداد پیام ها: {doc['message_count']}")
        print(f"    تعداد مدیا: {doc['media_count']}")
        print(f"    مسیر: {path}")

    finally:
        await c.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
