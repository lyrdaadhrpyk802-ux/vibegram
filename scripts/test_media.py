# ============================================
#  scripts/test_media.py - test sending photo, document, geo, venue
#  Sends to Saved Messages ("me") and reports result per media type.
#  All code and comments are English. No emojis.
# ============================================
import asyncio
import os
import sys
from pathlib import Path

from telethon.tl.types import (
    InputMediaGeoPoint, InputGeoPoint,
    InputMediaVenue,
)

from userapi import VibeClient


async def _safe(label, coro):
    try:
        result = await coro
        mid = getattr(result, "id", "?")
        print(f"[OK] {label} -> msg_id={mid}")
        return result
    except Exception as e:
        print(f"[!!] {label}: {type(e).__name__}: {str(e)[:200]}")
        return None


async def main():
    if os.getenv("VIBE_DEBUG") != "1":
        import logging
        logging.getLogger("telethon.network.mtprotosender").setLevel(logging.CRITICAL)
        logging.getLogger("telethon.network.connection.connection").setLevel(logging.CRITICAL)
        logging.getLogger("websockets").setLevel(logging.CRITICAL)

    test_dir = Path.home() / "pyvibe" / "_media_test"
    test_dir.mkdir(exist_ok=True)

    # small PNG (1x1, valid)
    png_bytes = bytes.fromhex(
        "89504e470d0a1a0a0000000d4948445200000001000000010806000000"
        "1f15c4890000000d49444154789c63600000000005000156a6b4b700"
        "00000049454e44ae426082"
    )
    png_path = test_dir / "test.png"
    png_path.write_bytes(png_bytes)

    txt_path = test_dir / "test.txt"
    txt_path.write_text("hello from pyvibe media test\n")

    c = VibeClient()
    try:
        await c.connect()
        me = await c.get_me()
        print(f"[+] connected as id={me.id} @{getattr(me, 'username', '-')}\n")

        sent_ids = []

        # 1) photo
        r = await _safe("send_file(photo)", c.send_file("me", str(png_path), caption="photo test"))
        if r is not None:
            sent_ids.append(r.id)

        # 2) document
        r = await _safe("send_file(document)", c.send_file(
            "me", str(txt_path), caption="doc test", force_document=True,
        ))
        if r is not None:
            sent_ids.append(r.id)

        # 3) geo point (location)
        geo = InputMediaGeoPoint(geo_point=InputGeoPoint(
            lat=35.6892, long=51.3890,  # Tehran
        ))
        r = await _safe("send_media(geo)", c.send_media("me", geo))
        if r is not None:
            sent_ids.append(r.id)

        # 4) venue (place with title)
        venue = InputMediaVenue(
            geo_point=InputGeoPoint(lat=35.6892, long=51.3890),
            title="Tehran",
            address="Tehran, Iran",
            provider="",
            venue_id="tehran-1",
            venue_type="city",
        )
        r = await _safe("send_media(venue)", c.send_media("me", venue))
        if r is not None:
            sent_ids.append(r.id)

        print(f"\n[i] total sent: {len(sent_ids)} -> {sent_ids}")

        # Cleanup recent test messages (safe: only our own labels)
        try:
            await asyncio.sleep(1)
            recent = await c.get_messages("me", limit=10)
            to_delete = [
                m.id for m in recent
                if m.id in sent_ids
            ]
            if to_delete:
                await c.delete_messages("me", to_delete)
                print(f"[i] cleaned {len(to_delete)} test message(s)")
        except Exception as e:
            print(f"[i] cleanup skipped: {type(e).__name__}: {e}")

    except Exception as e:
        print(f"[test_media] fatal: {type(e).__name__}: {e}")
    finally:
        await c.disconnect()
        try:
            for f in test_dir.iterdir():
                f.unlink()
            test_dir.rmdir()
        except Exception:
            pass


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(0)
