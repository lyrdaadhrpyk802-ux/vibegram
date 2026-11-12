# ============================================
#  scripts/test_uncertain.py - probe uncertain Vibe features
#  Each probe sends to Saved Messages ("me"), reports OK/FAIL, cleans up.
#  Designed so a failure of one probe does not stop the rest.
#  All code and comments are English. No emojis.
# ============================================
import asyncio
import os
import sys
import time
from datetime import datetime, timedelta, timezone

from userapi import VibeClient


PROBE_TIMEOUT = 25  # seconds per probe


def _label(name):
    return f"{name:30s}"


async def probe(name, coro_factory, sent_ids):
    try:
        result = await asyncio.wait_for(coro_factory(), timeout=PROBE_TIMEOUT)
        mid = getattr(result, "id", None)
        if mid is not None:
            sent_ids.append(mid)
        print(f"[OK]   {_label(name)} -> id={mid}")
        return result
    except asyncio.TimeoutError:
        print(f"[TIME] {_label(name)} -> timeout {PROBE_TIMEOUT}s")
    except Exception as e:
        print(f"[FAIL] {_label(name)} -> {type(e).__name__}: {str(e)[:160]}")
    return None


async def main():
    if os.getenv("VIBE_DEBUG") != "1":
        import logging
        logging.getLogger("telethon.network.mtprotosender").setLevel(logging.CRITICAL)
        logging.getLogger("telethon.network.connection.connection").setLevel(logging.CRITICAL)
        logging.getLogger("websockets").setLevel(logging.CRITICAL)

    c = VibeClient()
    sent_ids = []
    try:
        await c.connect()
        me = await c.get_me()
        print(f"[+] connected as id={me.id} @{getattr(me, 'username', '-')}\n")

        # -------- basic messaging features --------
        print("--- basic messaging ---")

        await probe(
            "silent send",
            lambda: c.send_message("me", "silent test", silent=True),
            sent_ids,
        )

        await probe(
            "scheduled send (+2min)",
            lambda: c.send_message(
                "me", "scheduled test",
                schedule=datetime.now(timezone.utc) + timedelta(minutes=2),
            ),
            sent_ids,
        )

        await probe(
            "reply markup (button)",
            lambda: c.send_message(
                "me", "button test",
                buttons=[[("Click", "https://example.com")]],
            ),
            sent_ids,
        )

        await probe(
            "no_webpage send",
            lambda: c.send_message(
                "me", "link https://example.com", link_preview=False,
            ),
            sent_ids,
        )

        # -------- reactions with custom (premium) emoji --------
        print("\n--- reactions ---")

        r = await probe(
            "send message for reaction",
            lambda: c.send_message("me", "react to me"),
            sent_ids,
        )
        if r is not None:
            await probe(
                "reaction normal emoji",
                lambda: c.send_reaction("me", r.id, emoticon="❤"),
                sent_ids,
            )
            # Custom emoji (premium) - needs a real document_id; skip if not known
            # We'll try with a placeholder to see if Vibe accepts the request shape
            await probe(
                "reaction paid/star shape",
                lambda: c.send_reaction("me", r.id, emoticon="⭐"),
                sent_ids,
            )
            await c.send_reaction("me", r.id, emoticon=None)

        # -------- media types --------
        print("\n--- media ---")

        # Voice note
        async def send_voice():
            import tempfile
            from pathlib import Path
            p = Path.home() / "pyvibe" / "_probe_voice.ogg"
            # minimal OGG/Opus-ish header (may fail server-side if Vibe validates)
            p.write_bytes(b"OggS\x00\x02" + b"\x00" * 60)
            try:
                return await c.send_file("me", str(p), voice_note=True)
            finally:
                try:
                    p.unlink()
                except Exception:
                    pass
        await probe("voice note", send_voice, sent_ids)

        # Video note
        async def send_video_note():
            from pathlib import Path
            p = Path.home() / "pyvibe" / "_probe_vnote.mp4"
            p.write_bytes(b"\x00" * 128)
            try:
                return await c.send_file("me", str(p), video_note=True)
            finally:
                try:
                    p.unlink()
                except Exception:
                    pass
        await probe("video note", send_video_note, sent_ids)

        # Poll
        async def send_poll():
            from telethon.tl.types import (
                InputMediaPoll, Poll, PollAnswer,
            )
            from telethon.tl.types import TextWithEntities
            poll = Poll(
                id=0,
                question=TextWithEntities(text="Vibe poll?", entities=[]),
                answers=[
                    PollAnswer(
                        text=TextWithEntities(text="yes", entities=[]),
                        option=b"1",
                    ),
                    PollAnswer(
                        text=TextWithEntities(text="no", entities=[]),
                        option=b"2",
                    ),
                ],
                closed=False, public_voters=True,
                multiple_choice=False, quiz=False,
                hash=0,
            )
            return await c.send_media("me", InputMediaPoll(poll=poll))
        await probe("poll", send_poll, sent_ids)

        # Dice
        async def send_dice():
            from telethon.tl.types import InputMediaDice
            return await c.send_media("me", InputMediaDice(emoticon="🎲"))
        await probe("dice", send_dice, sent_ids)

        # Contact
        async def send_contact():
            from telethon.tl.types import InputMediaContact
            return await c.send_media("me", InputMediaContact(
                phone_number="+REDACTED_PHONE",
                first_name="Test", last_name="Contact",
                vcard="",
            ))
        await probe("contact", send_contact, sent_ids)

        # -------- stories --------
        print("\n--- stories ---")
        await probe(
            "get_all_stories",
            lambda: c.get_all_stories(),
            sent_ids,
        )
        await probe(
            "get_peer_stories (self)",
            lambda: c.get_peer_stories("me"),
            sent_ids,
        )

        # -------- channel post with silent --------
        print("\n--- channel-specific ---")
        try:
            beta = await c.get_entity("بتا تسترهای وایب")
            # Try to get pinned in channel (read-only)
            await probe(
                "get pinned message",
                lambda: c.get_pinned_message(beta),
                sent_ids,
            )
        except Exception as e:
            print(f"[skip] channel context: {type(e).__name__}: {e}")

        # -------- bot / inline --------
        # Note: bots.* methods generally require logging in AS a bot, not a
        # user. Skipping bot-specific probes here.
        print("\n--- bots ---")
        print("[skip] bots.* need bot login (not applicable for user account)")

        # -------- premium / stars --------
        print("\n--- premium / stars ---")
        await probe(
            "get_my_stars",
            lambda: c.get_my_stars() if hasattr(c, "get_my_stars") else _noop(),
            sent_ids,
        )

        # -------- cleanup --------
        print(f"\n[i] total probes with id: {len(sent_ids)} -> {sent_ids}")
        try:
            await asyncio.sleep(1)
            # Delete our recent messages
            recent = await c.get_messages("me", limit=20)
            to_delete = [m.id for m in recent if m.id in sent_ids]
            if to_delete:
                await c.delete_messages("me", to_delete)
                print(f"[i] cleaned {len(to_delete)} message(s)")
        except Exception as e:
            print(f"[i] cleanup skipped: {type(e).__name__}: {e}")

    except Exception as e:
        print(f"[test_uncertain] fatal: {type(e).__name__}: {e}")
    finally:
        await c.disconnect()


async def _noop():
    return None


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(0)
