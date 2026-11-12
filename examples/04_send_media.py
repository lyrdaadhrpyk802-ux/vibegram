# ============================================
#  examples/04_send_media.py - send media (photo, doc, geo)
#  All code and comments are English. No emojis.
# ============================================
# این مثال نشان می‌دهد چطور عکس، فایل، لوکیشن و نظرسنجی بفرستید.
# فایل ها در پوشه موقت ساخته و در انتها پاک می شوند.

import asyncio
import os
from pathlib import Path
from telethon.tl.types import (
    InputMediaGeoPoint, InputGeoPoint, InputMediaPoll, Poll, PollAnswer, TextWithEntities
)
from userapi import VibeClient


async def main():
    c = VibeClient()
    temp_dir = Path.home() / "pyvibe" / "temp_media"
    temp_dir.mkdir(exist_ok=True)
    sent_ids = []

    try:
        await c.connect()
        print("[+] متصل شد\n")

        # 1) عکس
        png_path = temp_dir / "test.png"
        # یک عکس 1x1 ساده
        png_path.write_bytes(bytes.fromhex("89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c4890000000d49444154789c63600000000005000156a6b4b70000000049454e44ae426082"))
        
        msg = await c.send_file("me", str(png_path), caption="تست عکس")
        sent_ids.append(msg.id)
        print(f"[+] عکس فرستاده شد (id={msg.id})")

        # 2) فایل متنی
        txt_path = temp_dir / "test.txt"
        txt_path.write_text("سلام، این یک فایل متنی است.")
        
        msg = await c.send_file("me", str(txt_path), caption="تست فایل", force_document=True)
        sent_ids.append(msg.id)
        print(f"[+] فایل فرستاده شد (id={msg.id})")

        # 3) لوکیشن (نقطه روی نقشه - تهران)
        geo = InputMediaGeoPoint(geo_point=InputGeoPoint(lat=35.6892, long=51.3890))
        await c.send_media("me", geo)
        print("[+] لوکیشن فرستاده شد")

        # 4) نظرسنجی
        poll = Poll(
            id=0, 
            question=TextWithEntities(text="وایب چطوره؟", entities=[]),
            answers=[
                PollAnswer(text=TextWithEntities(text="عالیه", entities=[]), option=b"1"),
                PollAnswer(text=TextWithEntities(text="معمولیه", entities=[]), option=b"2"),
            ],
            closed=False, public_voters=True, multiple_choice=False, quiz=False, hash=0
        )
        await c.send_media("me", InputMediaPoll(poll=poll))
        print("[+] نظرسنجی فرستاده شد")

        # پاکسازی
        await asyncio.sleep(1)
        if sent_ids:
            await c.delete_messages("me", sent_ids, revoke=True)
        print("\n[+] پیام های تست پاک شدند")

    finally:
        await c.disconnect()
        # پاک کردن فایل های موقت
        for f in temp_dir.glob("*"):
            try: f.unlink()
            except: pass
        try: temp_dir.rmdir()
        except: pass


if __name__ == "__main__":
    asyncio.run(main())
