# ============================================
#  scripts/backup_chat.py - CLI to backup a chat to JSON
#  Usage:
#    python -B scripts/backup_chat.py <peer>
#    python -B scripts/backup_chat.py <peer> --limit 1000
#    python -B scripts/backup_chat.py <peer> --no-media
#    python -B scripts/backup_chat.py <peer> --fresh
#    python -B scripts/backup_chat.py <peer> --output ~/my_backups
#  All code and comments are English. No emojis.
# ============================================
import argparse
import asyncio
import os
import sys

from userapi import VibeClient
from userapi.backup import backup_chat


async def main():
    ap = argparse.ArgumentParser(prog="backup_chat")
    ap.add_argument("peer", help="username (@x), id, phone, or title")
    ap.add_argument("--limit", type=int, default=None,
                    help="max messages per run (default: all)")
    ap.add_argument("--no-media", action="store_true",
                    help="skip downloading media files")
    ap.add_argument("--output", default=None,
                    help="output root directory (default: ~/pyvibe/backups)")
    ap.add_argument("--fresh", action="store_true",
                    help="ignore existing backup and start over")
    ap.add_argument("--quiet", action="store_true",
                    help="do not print per-message progress")
    args = ap.parse_args()

    if os.getenv("VIBE_DEBUG") != "1":
        import logging
        logging.getLogger("telethon.network.mtprotosender").setLevel(logging.CRITICAL)
        logging.getLogger("telethon.network.connection.connection").setLevel(logging.CRITICAL)
        logging.getLogger("websockets").setLevel(logging.CRITICAL)

    c = VibeClient()
    try:
        await c.connect()

        def progress(step, total, msg):
            if args.quiet:
                return
            mt = msg.get("media_type") or "-"
            txt = (msg.get("text") or "")[:40].replace("\n", " ")
            print(f"  [{step}{('/' + str(total)) if total else ''}] "
                  f"id={msg.get('id')} {mt:8s} {txt!r}")

        path, doc = await backup_chat(
            c, args.peer,
            output_root=args.output,
            limit=args.limit,
            download_media=not args.no_media,
            progress=progress,
            fresh=args.fresh,
        )
        print(f"\n[+] saved {doc['message_count']} message(s), "
              f"{doc['media_count']} media file(s)")
        print(f"[+] json: {path}")
        print(f"[+] dir:  {path.parent}")
    except Exception as e:
        print(f"[backup_chat] error: {type(e).__name__}: {e}")
    finally:
        await c.disconnect()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(0)
